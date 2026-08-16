#!/usr/bin/env python3
"""Create and validate durable agent-loop workflow packages."""

import argparse
import ctypes
import errno
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set
from urllib.parse import urlparse


CURRENT_SCHEMA_VERSION = "3.0"
V2_SCHEMA_VERSION = "2.0"
SUPPORTED_SCHEMA_VERSIONS = {"1.0", V2_SCHEMA_VERSION, CURRENT_SCHEMA_VERSION}
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
INPUT_NAME_RE = re.compile(r"^[a-z][a-z0-9_]{0,63}$")
DOMAINS = {"coding", "research", "content", "operations", "general"}
INPUT_TYPES = {"string", "integer", "number", "boolean", "path", "uri"}
RISK_LEVELS = {"low", "medium", "high"}
EXECUTION_MODES = {"sequential", "parallel"}
LOOP_STATES = {
    "ready",
    "running",
    "waiting_approval",
    "blocked",
    "completed",
    "failed",
    "cancelled",
}
TASK_STATES = {
    "pending",
    "in_progress",
    "awaiting_evaluation",
    "completed",
    "failed",
    "blocked",
}
EVIDENCE_TYPES = {"deterministic", "human_attestation", "independent_evaluator"}
AUTHORITY_EFFECTS = {"allow", "approve", "deny"}
BREAKER_SIGNALS = {
    "no_new_evidence",
    "task_attempts",
    "consecutive_verifier_failures",
    "tool_failures",
    "approval_denials",
}
BREAKER_ACTIONS = {"block", "fail"}
ROLE_NAMES = {"planner", "worker", "evaluator", "final_evaluator"}
PORT_TYPES = {"artifact", "evidence", "data", "text", "json"}
STABLE_ID_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
REQUIRED_FILES = {"WORKFLOW.md", "state.json", "progress.md", "handoff.md"}
RECOMMENDATION_FILE = "runtime-recommendation.json"
RECOMMENDATION_SCHEMA_VERSION = "1.0"
INFERENCE_STATUSES = {"inferred", "defaulted", "needs_input"}
CONFIDENCE_LEVELS = {"high", "medium", "low"}
RUNTIME_ROLES = ("planner", "worker", "evaluator", "final_evaluator")
RUNTIME_TOOLS = {
    "read", "grep", "find", "ls", "edit", "write", "shell_argv", "http_fetch", "web_search", "*"
}
VERIFIER_TYPES = {"command", "file", "schema", "http", "human_attestation"}


class ValidationError(Exception):
    """Raised when a package or creation specification is invalid."""


def utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def require_dict(value: Any, name: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise ValidationError("{} must be an object".format(name))
    return value


def reject_unknown(mapping: Dict[str, Any], allowed: Set[str], name: str) -> None:
    unknown = sorted(set(mapping) - allowed)
    if unknown:
        raise ValidationError(
            "{} contains unknown field(s): {}".format(name, ", ".join(unknown))
        )


def require_text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError("{} must be a nonblank string".format(name))
    return value.strip()


def require_string_list(
    value: Any, name: str, *, allow_empty: bool = False
) -> List[str]:
    if not isinstance(value, list):
        raise ValidationError("{} must be an array of strings".format(name))
    result = [require_text(item, "{}[]".format(name)) for item in value]
    if not allow_empty and not result:
        raise ValidationError("{} must contain at least one item".format(name))
    return result


def optional_positive_number(value: Any, name: str, *, integer: bool = False) -> Any:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValidationError("{} must be a positive number or null".format(name))
    if integer and not isinstance(value, int):
        raise ValidationError("{} must be a positive integer or null".format(name))
    if value <= 0:
        raise ValidationError("{} must be greater than zero".format(name))
    return value


def validate_slug(slug: str) -> str:
    if len(slug) > 64 or not SLUG_RE.fullmatch(slug):
        raise ValidationError(
            "slug must be at most 64 lowercase letters, digits, and single hyphens"
        )
    return slug


def normalize_template(value: Any, default_id: str) -> Dict[str, Any]:
    if value is None:
        return {"id": validate_slug(default_id), "version": 1}
    template = require_dict(value, "template")
    reject_unknown(template, {"id", "version"}, "template")
    version = template.get("version")
    if isinstance(version, bool) or not isinstance(version, int) or version < 1:
        raise ValidationError("template.version must be a positive integer")
    return {
        "id": validate_slug(require_text(template.get("id"), "template.id")),
        "version": version,
    }


def normalize_input_schema(value: Any) -> List[Dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise ValidationError("input_schema must contain at least one input")
    result: List[Dict[str, Any]] = []
    names: Set[str] = set()
    allowed = {"name", "type", "description", "required"}
    for index, raw_item in enumerate(value):
        item_name = "input_schema[{}]".format(index)
        item = require_dict(raw_item, item_name)
        reject_unknown(item, allowed, item_name)
        name = require_text(item.get("name"), "{}.name".format(item_name))
        if not INPUT_NAME_RE.fullmatch(name):
            raise ValidationError(
                "{}.name must use lowercase letters, digits, and underscores".format(item_name)
            )
        if name in names:
            raise ValidationError("duplicate input name: {}".format(name))
        names.add(name)
        input_type = require_text(item.get("type"), "{}.type".format(item_name))
        if input_type not in INPUT_TYPES:
            raise ValidationError(
                "{}.type must be one of: {}".format(
                    item_name, ", ".join(sorted(INPUT_TYPES))
                )
            )
        required = item.get("required")
        if not isinstance(required, bool):
            raise ValidationError("{}.required must be a boolean".format(item_name))
        result.append(
            {
                "name": name,
                "type": input_type,
                "description": require_text(
                    item.get("description"), "{}.description".format(item_name)
                ),
                "required": required,
            }
        )
    return result


def validate_input_value(value: Any, input_type: str, name: str) -> Any:
    if input_type in {"string", "path", "uri"}:
        return require_text(value, name)
    if input_type == "boolean":
        if not isinstance(value, bool):
            raise ValidationError("{} must be a boolean".format(name))
        return value
    if input_type == "integer":
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValidationError("{} must be an integer".format(name))
        return value
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValidationError("{} must be a number".format(name))
    return int(value) if isinstance(value, float) and value.is_integer() else value


def normalize_input_bindings(
    value: Any, input_schema: List[Dict[str, Any]]
) -> Dict[str, Any]:
    bindings = require_dict(value, "input_bindings")
    fields = {item["name"]: item for item in input_schema}
    reject_unknown(bindings, set(fields), "input_bindings")
    missing = [
        name
        for name, item in fields.items()
        if item["required"] and name not in bindings
    ]
    if missing:
        raise ValidationError(
            "input_bindings missing required input(s): {}".format(", ".join(missing))
        )
    return {
        name: validate_input_value(
            bindings[name], item["type"], "input_bindings.{}".format(name)
        )
        for name, item in fields.items()
        if name in bindings
    }


def ensure_acyclic(tasks: List[Dict[str, Any]]) -> None:
    dependencies = {task["id"]: task["dependencies"] for task in tasks}
    visiting: Set[str] = set()
    visited: Set[str] = set()

    def visit(task_id: str) -> None:
        if task_id in visiting:
            raise ValidationError("task dependency graph contains a cycle")
        if task_id in visited:
            return
        visiting.add(task_id)
        for dependency in dependencies[task_id]:
            visit(dependency)
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in dependencies:
        visit(task_id)


def normalize_tasks(value: Any) -> List[Dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise ValidationError("tasks must contain at least one task")
    allowed = {"id", "title", "description", "dependencies", "acceptance_criteria"}
    tasks: List[Dict[str, Any]] = []
    ids: Set[str] = set()
    for index, raw_task in enumerate(value):
        task_name = "tasks[{}]".format(index)
        task = require_dict(raw_task, task_name)
        reject_unknown(task, allowed, task_name)
        task_id = require_text(task.get("id"), "{}.id".format(task_name))
        if task_id in ids:
            raise ValidationError("duplicate task id: {}".format(task_id))
        ids.add(task_id)
        tasks.append(
            {
                "id": task_id,
                "title": require_text(task.get("title"), "{}.title".format(task_name)),
                "description": require_text(
                    task.get("description"), "{}.description".format(task_name)
                ),
                "dependencies": require_string_list(
                    task.get("dependencies"),
                    "{}.dependencies".format(task_name),
                    allow_empty=True,
                ),
                "acceptance_criteria": require_string_list(
                    task.get("acceptance_criteria"),
                    "{}.acceptance_criteria".format(task_name),
                ),
            }
        )

    for task in tasks:
        for dependency in task["dependencies"]:
            if dependency not in ids:
                raise ValidationError(
                    "task {} depends on unknown task {}".format(task["id"], dependency)
                )
            if dependency == task["id"]:
                raise ValidationError("task {} depends on itself".format(task["id"]))
    ensure_acyclic(tasks)
    return tasks


def normalize_authority(value: Any) -> Dict[str, Any]:
    authority = require_dict(value, "authority")
    allowed = {
        "risk_level",
        "auto_allowed",
        "approval_required",
        "forbidden",
        "credential_policy",
    }
    reject_unknown(authority, allowed, "authority")
    risk_level = require_text(authority.get("risk_level"), "authority.risk_level")
    if risk_level not in RISK_LEVELS:
        raise ValidationError(
            "authority.risk_level must be one of: {}".format(
                ", ".join(sorted(RISK_LEVELS))
            )
        )
    approval_required = require_string_list(
        authority.get("approval_required"),
        "authority.approval_required",
        allow_empty=risk_level == "low",
    )
    return {
        "risk_level": risk_level,
        "auto_allowed": require_string_list(
            authority.get("auto_allowed"), "authority.auto_allowed"
        ),
        "approval_required": approval_required,
        "forbidden": require_string_list(
            authority.get("forbidden"), "authority.forbidden"
        ),
        "credential_policy": require_text(
            authority.get("credential_policy"), "authority.credential_policy"
        ),
    }


def normalize_limits(value: Any) -> Dict[str, Any]:
    limits = require_dict(value, "limits")
    allowed = {"max_iterations", "max_minutes", "max_cost", "cost_currency"}
    reject_unknown(limits, allowed, "limits")
    normalized = {
        "max_iterations": optional_positive_number(
            limits.get("max_iterations"), "limits.max_iterations", integer=True
        ),
        "max_minutes": optional_positive_number(
            limits.get("max_minutes"), "limits.max_minutes"
        ),
        "max_cost": optional_positive_number(limits.get("max_cost"), "limits.max_cost"),
        "cost_currency": limits.get("cost_currency"),
    }
    if all(
        normalized[key] is None
        for key in ("max_iterations", "max_minutes", "max_cost")
    ):
        raise ValidationError("limits must define at least one positive hard limit")
    if normalized["max_cost"] is not None:
        normalized["cost_currency"] = require_text(
            normalized["cost_currency"], "limits.cost_currency"
        )
    elif normalized["cost_currency"] is not None:
        raise ValidationError("limits.cost_currency requires limits.max_cost")
    return normalized


def normalize_checkpoint(value: Any) -> Dict[str, Any]:
    checkpoint = require_dict(value, "checkpoint")
    allowed = {"frequency", "required_evidence"}
    reject_unknown(checkpoint, allowed, "checkpoint")
    return {
        "frequency": require_text(checkpoint.get("frequency"), "checkpoint.frequency"),
        "required_evidence": require_string_list(
            checkpoint.get("required_evidence"), "checkpoint.required_evidence"
        ),
    }


def normalize_v2_spec(raw: Any, default_template_id: str) -> Dict[str, Any]:
    spec = require_dict(raw, "specification")
    allowed = {
        "title",
        "template",
        "language",
        "domain",
        "execution_mode",
        "goal",
        "audience",
        "inputs",
        "input_schema",
        "input_bindings",
        "invariants",
        "done_conditions",
        "tasks",
        "verification",
        "authority",
        "limits",
        "checkpoint",
        "stop_conditions",
    }
    reject_unknown(spec, allowed, "specification")
    domain = require_text(spec.get("domain"), "domain")
    if domain not in DOMAINS:
        raise ValidationError("domain must be one of: {}".format(", ".join(sorted(DOMAINS))))
    execution_mode = require_text(spec.get("execution_mode"), "execution_mode")
    if execution_mode not in EXECUTION_MODES:
        raise ValidationError(
            "execution_mode must be one of: {}".format(", ".join(sorted(EXECUTION_MODES)))
        )
    input_schema = normalize_input_schema(spec.get("input_schema"))
    input_bindings = normalize_input_bindings(spec.get("input_bindings"), input_schema)
    return {
        "schema_version": V2_SCHEMA_VERSION,
        "title": require_text(spec.get("title"), "title"),
        "template": normalize_template(spec.get("template"), default_template_id),
        "language": require_text(spec.get("language"), "language"),
        "domain": domain,
        "execution_mode": execution_mode,
        "goal": require_text(spec.get("goal"), "goal"),
        "audience": require_text(spec.get("audience"), "audience"),
        "inputs": require_string_list(spec.get("inputs"), "inputs"),
        "input_schema": input_schema,
        "input_bindings": input_bindings,
        "input_bindings_sha256": sha256_bytes(canonical_json(input_bindings)),
        "invariants": require_string_list(spec.get("invariants"), "invariants", allow_empty=True),
        "done_conditions": require_string_list(spec.get("done_conditions"), "done_conditions"),
        "tasks": normalize_tasks(spec.get("tasks")),
        "verification": require_string_list(spec.get("verification"), "verification"),
        "authority": normalize_authority(spec.get("authority")),
        "limits": normalize_limits(spec.get("limits")),
        "checkpoint": normalize_checkpoint(spec.get("checkpoint")),
        "stop_conditions": require_string_list(spec.get("stop_conditions"), "stop_conditions"),
    }


def require_stable_id(value: Any, name: str) -> str:
    result = require_text(value, name)
    if len(result) > 64 or not STABLE_ID_RE.fullmatch(result):
        raise ValidationError(
            "{} must be a lowercase stable ID with hyphen-separated segments".format(name)
        )
    return result


def require_positive_integer(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValidationError("{} must be a positive integer".format(name))
    return value


def normalize_evidence_requirements(value: Any) -> List[Dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise ValidationError("evidence_requirements must contain at least one item")
    result: List[Dict[str, Any]] = []
    ids: Set[str] = set()
    for index, raw in enumerate(value):
        name = "evidence_requirements[{}]".format(index)
        item = require_dict(raw, name)
        reject_unknown(item, {"id", "type", "description"}, name)
        item_id = require_stable_id(item.get("id"), "{}.id".format(name))
        if item_id in ids:
            raise ValidationError("duplicate evidence requirement id: {}".format(item_id))
        ids.add(item_id)
        item_type = require_text(item.get("type"), "{}.type".format(name))
        if item_type not in EVIDENCE_TYPES:
            raise ValidationError(
                "{}.type must be one of: {}".format(name, ", ".join(sorted(EVIDENCE_TYPES)))
            )
        result.append(
            {
                "id": item_id,
                "type": item_type,
                "description": require_text(
                    item.get("description"), "{}.description".format(name)
                ),
            }
        )
    return result


def normalize_conditions(
    value: Any, requirements: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise ValidationError("conditions must contain at least one condition")
    requirement_types = {item["id"]: item["type"] for item in requirements}
    result: List[Dict[str, Any]] = []
    ids: Set[str] = set()
    for index, raw in enumerate(value):
        name = "conditions[{}]".format(index)
        item = require_dict(raw, name)
        reject_unknown(item, {"id", "description", "evidence_requirement_ids"}, name)
        item_id = require_stable_id(item.get("id"), "{}.id".format(name))
        if item_id in ids:
            raise ValidationError("duplicate condition id: {}".format(item_id))
        ids.add(item_id)
        requirement_ids = require_string_list(
            item.get("evidence_requirement_ids"),
            "{}.evidence_requirement_ids".format(name),
        )
        if len(requirement_ids) != len(set(requirement_ids)):
            raise ValidationError("{} contains duplicate requirement IDs".format(name))
        unknown = sorted(set(requirement_ids) - set(requirement_types))
        if unknown:
            raise ValidationError(
                "{} references unknown evidence requirement(s): {}".format(
                    name, ", ".join(unknown)
                )
            )
        if not any(
            requirement_types[requirement_id]
            in {"deterministic", "human_attestation"}
            for requirement_id in requirement_ids
        ):
            raise ValidationError(
                "{} must bind at least one deterministic or human_attestation requirement".format(
                    name
                )
            )
        result.append(
            {
                "id": item_id,
                "description": require_text(
                    item.get("description"), "{}.description".format(name)
                ),
                "evidence_requirement_ids": requirement_ids,
            }
        )
    return result


def normalize_ports(value: Any, name: str, *, inputs: bool) -> List[Dict[str, Any]]:
    if not isinstance(value, list):
        raise ValidationError("{} must be an array".format(name))
    result: List[Dict[str, Any]] = []
    ids: Set[str] = set()
    allowed = (
        {"id", "type", "description", "required"}
        if inputs
        else {"id", "type", "description"}
    )
    for index, raw in enumerate(value):
        item_name = "{}[{}]".format(name, index)
        item = require_dict(raw, item_name)
        reject_unknown(item, allowed, item_name)
        port_id = require_stable_id(item.get("id"), "{}.id".format(item_name))
        if port_id in ids:
            raise ValidationError("duplicate port id in {}: {}".format(name, port_id))
        ids.add(port_id)
        port_type = require_text(item.get("type"), "{}.type".format(item_name))
        if port_type not in PORT_TYPES:
            raise ValidationError(
                "{}.type must be one of: {}".format(
                    item_name, ", ".join(sorted(PORT_TYPES))
                )
            )
        normalized = {
            "id": port_id,
            "type": port_type,
            "description": require_text(
                item.get("description"), "{}.description".format(item_name)
            ),
        }
        if inputs:
            if not isinstance(item.get("required"), bool):
                raise ValidationError("{}.required must be a boolean".format(item_name))
            normalized["required"] = item["required"]
        result.append(normalized)
    return result


def ensure_graph_acyclic(node_ids: Set[str], edges: List[Dict[str, Any]]) -> None:
    successors: Dict[str, List[str]] = {node_id: [] for node_id in node_ids}
    for edge in edges:
        successors[edge["from"]["node_id"]].append(edge["to"]["node_id"])
    visiting: Set[str] = set()
    visited: Set[str] = set()

    def visit(node_id: str) -> None:
        if node_id in visiting:
            raise ValidationError("initial_graph contains a cycle")
        if node_id in visited:
            return
        visiting.add(node_id)
        for successor in successors[node_id]:
            visit(successor)
        visiting.remove(node_id)
        visited.add(node_id)

    for node_id in node_ids:
        visit(node_id)


def normalize_initial_graph(value: Any) -> Dict[str, Any]:
    graph = require_dict(value, "initial_graph")
    reject_unknown(graph, {"nodes", "edges"}, "initial_graph")
    raw_nodes = graph.get("nodes")
    if not isinstance(raw_nodes, list) or not raw_nodes:
        raise ValidationError("initial_graph.nodes must contain at least one node")
    nodes: List[Dict[str, Any]] = []
    node_ids: Set[str] = set()
    node_ports: Dict[str, Dict[str, Dict[str, str]]] = {}
    for index, raw in enumerate(raw_nodes):
        name = "initial_graph.nodes[{}]".format(index)
        item = require_dict(raw, name)
        reject_unknown(
            item,
            {
                "id",
                "title",
                "description",
                "input_ports",
                "output_ports",
                "acceptance_criteria",
                "resource_keys",
                "max_attempts",
                "no_progress_limit",
            },
            name,
        )
        node_id = require_stable_id(item.get("id"), "{}.id".format(name))
        if node_id in node_ids:
            raise ValidationError("duplicate graph node id: {}".format(node_id))
        node_ids.add(node_id)
        input_ports = normalize_ports(
            item.get("input_ports", []), "{}.input_ports".format(name), inputs=True
        )
        output_ports = normalize_ports(
            item.get("output_ports", []), "{}.output_ports".format(name), inputs=False
        )
        max_attempts = require_positive_integer(
            item.get("max_attempts", 2), "{}.max_attempts".format(name)
        )
        no_progress_limit = require_positive_integer(
            item.get("no_progress_limit", 2), "{}.no_progress_limit".format(name)
        )
        if no_progress_limit > max_attempts:
            raise ValidationError("{}.no_progress_limit cannot exceed max_attempts".format(name))
        resource_keys = require_string_list(
            item.get("resource_keys", []), "{}.resource_keys".format(name), allow_empty=True
        )
        if len(resource_keys) != len(set(resource_keys)):
            raise ValidationError("{}.resource_keys contains duplicates".format(name))
        node_ports[node_id] = {
            "inputs": {port["id"]: port for port in input_ports},
            "outputs": {port["id"]: port for port in output_ports},
        }
        nodes.append(
            {
                "id": node_id,
                "title": require_text(item.get("title"), "{}.title".format(name)),
                "description": require_text(
                    item.get("description"), "{}.description".format(name)
                ),
                "input_ports": input_ports,
                "output_ports": output_ports,
                "acceptance_criteria": require_string_list(
                    item.get("acceptance_criteria"),
                    "{}.acceptance_criteria".format(name),
                ),
                "resource_keys": resource_keys,
                "max_attempts": max_attempts,
                "no_progress_limit": no_progress_limit,
            }
        )

    raw_edges = graph.get("edges", [])
    if not isinstance(raw_edges, list):
        raise ValidationError("initial_graph.edges must be an array")
    edges: List[Dict[str, Any]] = []
    edge_ids: Set[str] = set()
    occupied_inputs: Set[str] = set()
    for index, raw in enumerate(raw_edges):
        name = "initial_graph.edges[{}]".format(index)
        item = require_dict(raw, name)
        reject_unknown(item, {"id", "from", "to"}, name)
        edge_id = require_stable_id(item.get("id"), "{}.id".format(name))
        if edge_id in edge_ids:
            raise ValidationError("duplicate graph edge id: {}".format(edge_id))
        edge_ids.add(edge_id)
        endpoints: Dict[str, Dict[str, str]] = {}
        for direction, port_kind in (("from", "outputs"), ("to", "inputs")):
            endpoint_name = "{}.{}".format(name, direction)
            endpoint = require_dict(item.get(direction), endpoint_name)
            reject_unknown(endpoint, {"node_id", "port_id"}, endpoint_name)
            node_id = require_stable_id(
                endpoint.get("node_id"), "{}.node_id".format(endpoint_name)
            )
            port_id = require_stable_id(
                endpoint.get("port_id"), "{}.port_id".format(endpoint_name)
            )
            if node_id not in node_ports:
                raise ValidationError("{} references unknown node {}".format(name, node_id))
            if port_id not in node_ports[node_id][port_kind]:
                raise ValidationError(
                    "{} references unknown {} port {}.{}".format(
                        name, direction, node_id, port_id
                    )
                )
            endpoints[direction] = {"node_id": node_id, "port_id": port_id}
        if endpoints["from"]["node_id"] == endpoints["to"]["node_id"]:
            raise ValidationError("{} cannot connect a node to itself".format(name))
        source = node_ports[endpoints["from"]["node_id"]]["outputs"][
            endpoints["from"]["port_id"]
        ]
        target = node_ports[endpoints["to"]["node_id"]]["inputs"][
            endpoints["to"]["port_id"]
        ]
        if source["type"] != target["type"]:
            raise ValidationError("{} connects incompatible port types".format(name))
        input_key = "{}:{}".format(
            endpoints["to"]["node_id"], endpoints["to"]["port_id"]
        )
        if input_key in occupied_inputs:
            raise ValidationError("input port {} has more than one incoming edge".format(input_key))
        occupied_inputs.add(input_key)
        edges.append({"id": edge_id, **endpoints})

    for node in nodes:
        for port in node["input_ports"]:
            if port["required"] and "{}:{}".format(node["id"], port["id"]) not in occupied_inputs:
                raise ValidationError(
                    "required input port {}.{} has no incoming edge".format(
                        node["id"], port["id"]
                    )
                )
    ensure_graph_acyclic(node_ids, edges)
    return {"nodes": nodes, "edges": edges}


def normalize_v3_authority(value: Any) -> Dict[str, Any]:
    authority = require_dict(value, "authority")
    reject_unknown(
        authority,
        {"risk_level", "rules", "credential_policy", "credential_env"},
        "authority",
    )
    risk_level = require_text(authority.get("risk_level"), "authority.risk_level")
    if risk_level not in RISK_LEVELS:
        raise ValidationError("authority.risk_level is invalid")
    raw_rules = authority.get("rules")
    if not isinstance(raw_rules, list) or not raw_rules:
        raise ValidationError("authority.rules must contain at least one rule")
    rules: List[Dict[str, Any]] = []
    ids: Set[str] = set()
    for index, raw in enumerate(raw_rules):
        name = "authority.rules[{}]".format(index)
        item = require_dict(raw, name)
        reject_unknown(item, {"authority_id", "effect", "description"}, name)
        authority_id = require_stable_id(
            item.get("authority_id"), "{}.authority_id".format(name)
        )
        if authority_id in ids:
            raise ValidationError("duplicate authority_id: {}".format(authority_id))
        ids.add(authority_id)
        effect = require_text(item.get("effect"), "{}.effect".format(name))
        if effect not in AUTHORITY_EFFECTS:
            raise ValidationError("{}.effect is invalid".format(name))
        rules.append(
            {
                "authority_id": authority_id,
                "effect": effect,
                "description": require_text(
                    item.get("description"), "{}.description".format(name)
                ),
            }
        )
    if risk_level in {"medium", "high"} and not any(
        rule["effect"] == "approve" for rule in rules
    ):
        raise ValidationError("medium/high risk authority requires an approve rule")
    if not any(rule["effect"] == "deny" for rule in rules):
        raise ValidationError("authority.rules must contain at least one deny rule")
    normalized = {
        "risk_level": risk_level,
        "rules": rules,
        "credential_policy": require_text(
            authority.get("credential_policy"), "authority.credential_policy"
        ),
    }
    if "credential_env" in authority:
        credential_env = require_string_list(
            authority.get("credential_env"), "authority.credential_env", allow_empty=True
        )
        if len(credential_env) != len(set(credential_env)):
            raise ValidationError("authority.credential_env contains duplicates")
        for name in credential_env:
            if not re.fullmatch(r"[A-Z_][A-Z0-9_]*", name):
                raise ValidationError(
                    "invalid authorized credential environment variable name: {}".format(name)
                )
        normalized["credential_env"] = credential_env
    return normalized


def normalize_v3_limits(value: Any) -> Dict[str, Any]:
    limits = require_dict(value, "limits")
    allowed = {
        "max_iterations",
        "max_minutes",
        "max_cost",
        "cost_currency",
        "max_total_tokens",
    }
    reject_unknown(limits, allowed, "limits")
    normalized = {
        "max_iterations": optional_positive_number(
            limits.get("max_iterations"), "limits.max_iterations", integer=True
        ),
        "max_minutes": optional_positive_number(
            limits.get("max_minutes"), "limits.max_minutes"
        ),
        "max_cost": optional_positive_number(limits.get("max_cost"), "limits.max_cost"),
        "cost_currency": limits.get("cost_currency"),
        "max_total_tokens": optional_positive_number(
            limits.get("max_total_tokens"), "limits.max_total_tokens", integer=True
        ),
    }
    if all(
        normalized[key] is None
        for key in ("max_iterations", "max_minutes", "max_cost", "max_total_tokens")
    ):
        raise ValidationError("limits must define at least one positive hard limit")
    if normalized["max_cost"] is not None:
        normalized["cost_currency"] = require_text(
            normalized["cost_currency"], "limits.cost_currency"
        )
    elif normalized["cost_currency"] is not None:
        raise ValidationError("limits.cost_currency requires limits.max_cost")
    return normalized


def normalize_v3_checkpoint(value: Any) -> Dict[str, Any]:
    checkpoint = require_dict(value, "checkpoint")
    reject_unknown(checkpoint, {"required_triggers", "required_evidence"}, "checkpoint")
    triggers = require_string_list(
        checkpoint.get("required_triggers"), "checkpoint.required_triggers"
    )
    if len(triggers) != len(set(triggers)):
        raise ValidationError("checkpoint.required_triggers contains duplicates")
    return {
        "required_triggers": triggers,
        "required_evidence": require_string_list(
            checkpoint.get("required_evidence"), "checkpoint.required_evidence"
        ),
    }


def normalize_circuit_breakers(value: Any) -> List[Dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise ValidationError("circuit_breakers must contain at least one breaker")
    result: List[Dict[str, Any]] = []
    ids: Set[str] = set()
    for index, raw in enumerate(value):
        name = "circuit_breakers[{}]".format(index)
        item = require_dict(raw, name)
        reject_unknown(item, {"id", "signal", "threshold", "action"}, name)
        item_id = require_stable_id(item.get("id"), "{}.id".format(name))
        if item_id in ids:
            raise ValidationError("duplicate circuit breaker id: {}".format(item_id))
        ids.add(item_id)
        signal = require_text(item.get("signal"), "{}.signal".format(name))
        if signal not in BREAKER_SIGNALS:
            raise ValidationError("{}.signal is invalid".format(name))
        action = require_text(item.get("action"), "{}.action".format(name))
        if action not in BREAKER_ACTIONS:
            raise ValidationError("{}.action is invalid".format(name))
        result.append(
            {
                "id": item_id,
                "signal": signal,
                "threshold": require_positive_integer(
                    item.get("threshold"), "{}.threshold".format(name)
                ),
                "action": action,
            }
        )
    return result


def normalize_memory_policy(value: Any) -> Dict[str, Any]:
    policy = require_dict(value, "memory_policy")
    reject_unknown(
        policy,
        {"max_entries", "retrieval_top_k", "max_context_tokens"},
        "memory_policy",
    )
    max_entries = require_positive_integer(policy.get("max_entries"), "memory_policy.max_entries")
    top_k = require_positive_integer(policy.get("retrieval_top_k"), "memory_policy.retrieval_top_k")
    if top_k > max_entries:
        raise ValidationError("memory_policy.retrieval_top_k cannot exceed max_entries")
    return {
        "max_entries": max_entries,
        "retrieval_top_k": top_k,
        "max_context_tokens": require_positive_integer(
            policy.get("max_context_tokens"), "memory_policy.max_context_tokens"
        ),
    }


def normalize_context_policy(value: Any) -> Dict[str, Any]:
    policy = require_dict(value, "context_policy")
    reject_unknown(
        policy,
        {"estimator", "fail_on_required_overflow", "role_token_budgets"},
        "context_policy",
    )
    if policy.get("estimator") != "utf8_bytes":
        raise ValidationError("context_policy.estimator must be utf8_bytes")
    if policy.get("fail_on_required_overflow") is not True:
        raise ValidationError("context_policy.fail_on_required_overflow must be true")
    budgets = require_dict(policy.get("role_token_budgets"), "context_policy.role_token_budgets")
    reject_unknown(budgets, ROLE_NAMES, "context_policy.role_token_budgets")
    if set(budgets) != ROLE_NAMES:
        raise ValidationError("context_policy.role_token_budgets must define all four roles")
    return {
        "estimator": "utf8_bytes",
        "fail_on_required_overflow": True,
        "role_token_budgets": {
            role: require_positive_integer(
                budgets[role], "context_policy.role_token_budgets.{}".format(role)
            )
            for role in sorted(ROLE_NAMES)
        },
    }


def normalize_v3_spec(raw: Any, default_template_id: str) -> Dict[str, Any]:
    spec = require_dict(raw, "specification")
    allowed = {
        "schema_version",
        "title",
        "template",
        "language",
        "domain",
        "execution_mode",
        "goal",
        "audience",
        "inputs",
        "input_schema",
        "input_bindings",
        "invariants",
        "conditions",
        "evidence_requirements",
        "initial_graph",
        "authority",
        "limits",
        "checkpoint",
        "circuit_breakers",
        "memory_policy",
        "context_policy",
        "runtime_recommendation",
    }
    reject_unknown(spec, allowed, "specification")
    if spec.get("schema_version", CURRENT_SCHEMA_VERSION) != CURRENT_SCHEMA_VERSION:
        raise ValidationError("v3 specification schema_version must be 3.0")
    domain = require_text(spec.get("domain"), "domain")
    if domain not in DOMAINS:
        raise ValidationError("domain must be one of: {}".format(", ".join(sorted(DOMAINS))))
    execution_mode = require_text(spec.get("execution_mode"), "execution_mode")
    if execution_mode not in EXECUTION_MODES:
        raise ValidationError("execution_mode is invalid")
    input_schema = normalize_input_schema(spec.get("input_schema"))
    input_bindings = normalize_input_bindings(spec.get("input_bindings"), input_schema)
    requirements = normalize_evidence_requirements(spec.get("evidence_requirements"))
    conditions = normalize_conditions(spec.get("conditions"), requirements)
    auto_default_paths = [
        "/{}".format(field)
        for field in (
            "limits",
            "checkpoint",
            "circuit_breakers",
            "memory_policy",
            "context_policy",
        )
        if field not in spec
    ]
    initial_graph = normalize_initial_graph(spec.get("initial_graph"))
    node_count = len(initial_graph["nodes"])
    edge_count = len(initial_graph["edges"])
    condition_count = len(conditions)
    attempts = sum(node["max_attempts"] for node in initial_graph["nodes"])
    role_budgets = {
        "planner": min(24000, 8000 + 1000 * node_count),
        "worker": min(48000, 16000 + 2000 * node_count),
        "evaluator": min(24000, 8000 + 1000 * condition_count),
        "final_evaluator": min(16000, 8000 + 1000 * condition_count),
    }
    default_limits = {
        "max_iterations": attempts,
        "max_minutes": max(60, min(480, 30 * node_count + 15 * edge_count)),
        "max_cost": None,
        "cost_currency": None,
        "max_total_tokens": attempts
        * (role_budgets["planner"] + role_budgets["worker"] + role_budgets["evaluator"])
        + role_budgets["final_evaluator"],
    }
    raw_limits = require_dict(spec.get("limits", {}), "limits")
    limits = normalize_v3_limits({**default_limits, **raw_limits})
    checkpoint = normalize_v3_checkpoint(
        spec.get(
            "checkpoint",
            {
                "required_triggers": [
                    "task_evaluated",
                    "before_context_reset",
                    "approval_resolved",
                ],
                "required_evidence": [
                    "State transition",
                    "Verifier result",
                    "Next action",
                ],
            },
        )
    )
    circuit_breakers = normalize_circuit_breakers(
        spec.get(
            "circuit_breakers",
            [
                {"id": "no-new-evidence", "signal": "no_new_evidence", "threshold": 2, "action": "block"},
                {"id": "verifier-failures", "signal": "consecutive_verifier_failures", "threshold": 3, "action": "block"},
                {"id": "tool-failures", "signal": "tool_failures", "threshold": 3, "action": "fail"},
                {"id": "approval-denials", "signal": "approval_denials", "threshold": 1, "action": "block"},
            ],
        )
    )
    memory_policy = normalize_memory_policy(
        spec.get(
            "memory_policy",
            {"max_entries": 1000, "retrieval_top_k": 12, "max_context_tokens": 4000},
        )
    )
    context_policy = normalize_context_policy(
        spec.get(
            "context_policy",
            {
                "estimator": "utf8_bytes",
                "fail_on_required_overflow": True,
                "role_token_budgets": role_budgets,
            },
        )
    )
    normalized = {
        "schema_version": CURRENT_SCHEMA_VERSION,
        "title": require_text(spec.get("title"), "title"),
        "template": normalize_template(spec.get("template"), default_template_id),
        "language": require_text(spec.get("language"), "language"),
        "domain": domain,
        "execution_mode": execution_mode,
        "goal": require_text(spec.get("goal"), "goal"),
        "audience": require_text(spec.get("audience"), "audience"),
        "inputs": require_string_list(spec.get("inputs"), "inputs"),
        "input_schema": input_schema,
        "input_bindings": input_bindings,
        "input_bindings_sha256": sha256_bytes(canonical_json(input_bindings)),
        "invariants": require_string_list(spec.get("invariants"), "invariants", allow_empty=True),
        "conditions": conditions,
        "evidence_requirements": requirements,
        "initial_graph": initial_graph,
        "authority": normalize_v3_authority(spec.get("authority")),
        "limits": limits,
        "checkpoint": checkpoint,
        "circuit_breakers": circuit_breakers,
        "memory_policy": memory_policy,
        "context_policy": context_policy,
    }
    normalized["runtime_recommendation"] = spec.get("runtime_recommendation")
    normalized["_auto_default_paths"] = auto_default_paths
    return normalized


def normalize_create_spec(raw: Any, default_template_id: str) -> Dict[str, Any]:
    mapping = require_dict(raw, "specification")
    if mapping.get("schema_version") == V2_SCHEMA_VERSION:
        legacy = dict(mapping)
        legacy.pop("schema_version", None)
        return normalize_v2_spec(legacy, default_template_id)
    return normalize_v3_spec(mapping, default_template_id)


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def progress_chain_next(previous_head: Optional[str], exact_entry: str) -> str:
    prefix = previous_head or ""
    return sha256_bytes((prefix + "\0" + exact_entry).encode("utf-8"))


def markdown_bullets(items: Iterable[str], *, checkboxes: bool = False) -> str:
    prefix = "- [ ] " if checkboxes else "- "
    return "\n".join(prefix + item.replace("\n", "\n  ") for item in items)


def labels(language: str) -> Dict[str, str]:
    if language.lower().startswith("zh"):
        return {
            "title": "Loop 工作流",
            "notice": "此包只定义工作流；必须获得独立指令后才能启动目标任务。",
            "start": "启动或恢复",
            "goal": "目标",
            "audience": "使用者",
            "inputs": "输入与事实来源",
            "input_contract": "可复用输入合同",
            "input_schema": "参数定义",
            "input_bindings": "本实例绑定",
            "done": "完成条件",
            "invariants": "不可变约束",
            "roles": "角色职责",
            "planner": "Planner",
            "worker": "Worker",
            "evaluator": "Evaluator",
            "queue": "任务状态",
            "protocol": "循环协议",
            "verification": "验证证据",
            "authority": "权限边界",
            "automatic": "可自动执行",
            "approval": "逐项审批",
            "forbidden": "禁止事项",
            "credentials": "凭据策略",
            "checkpoint": "检查点与恢复",
            "frequency": "频率",
            "required_evidence": "必需证据",
            "limits": "预算与停止条件",
            "changes": "合同变更",
            "secret_notice": "不得在此工作流包中存储任何秘密值。",
        }
    return {
        "title": "Loop Workflow",
        "notice": "This package defines the workflow only. Start the target task only after a separate instruction.",
        "start": "Start or resume",
        "goal": "Goal",
        "audience": "Audience",
        "inputs": "Inputs and sources of truth",
        "input_contract": "Reusable input contract",
        "input_schema": "Parameter schema",
        "input_bindings": "Instance bindings",
        "done": "Completion conditions",
        "invariants": "Immutable constraints",
        "roles": "Role responsibilities",
        "planner": "Planner",
        "worker": "Worker",
        "evaluator": "Evaluator",
        "queue": "Task state",
        "protocol": "Loop protocol",
        "verification": "Verification evidence",
        "authority": "Authority boundaries",
        "automatic": "Automatically allowed",
        "approval": "Per-action approval",
        "forbidden": "Forbidden",
        "credentials": "Credential policy",
        "checkpoint": "Checkpoint and recovery",
        "frequency": "Frequency",
        "required_evidence": "Required evidence",
        "limits": "Limits and stop conditions",
        "changes": "Contract changes",
        "secret_notice": "Never store secret values in this package.",
    }


def render_v2_workflow(
    spec: Dict[str, Any], slug: str, contract_version: int = 1
) -> str:
    text = labels(spec["language"])
    is_chinese = spec["language"].lower().startswith("zh")
    invariants = spec["invariants"] or [
        "除已确认合同外无其他约束。" if is_chinese else "None beyond the confirmed contract."
    ]
    approval = spec["authority"]["approval_required"] or [
        "此低风险工作流无逐项审批动作。"
        if is_chinese
        else "None for this low-risk workflow."
    ]
    limit_lines = []
    if spec["limits"]["max_iterations"] is not None:
        limit_lines.append("max_iterations: {}".format(spec["limits"]["max_iterations"]))
    if spec["limits"]["max_minutes"] is not None:
        limit_lines.append("max_minutes: {}".format(spec["limits"]["max_minutes"]))
    if spec["limits"]["max_cost"] is not None:
        limit_lines.append(
            "max_cost: {} {}".format(
                spec["limits"]["max_cost"], spec["limits"]["cost_currency"]
            )
        )
    limit_lines.extend(spec["stop_conditions"])

    if is_chinese:
        start_steps = [
            "运行包校验；校验失败时不得开始。",
            "依次读取 `WORKFLOW.md`、`state.json`、`progress.md` 最新记录和 `handoff.md`。",
            "仅在收到独立启动指令后，把状态从 `ready` 转为 `running`。",
            "每轮只执行 planner 选定且依赖满足的任务；并行模式也必须保持隔离所有权。",
        ]
        role_lines = {
            "planner": "选择或调整下一个有界任务；不得执行任务或宣布总目标完成。",
            "worker": "只执行已选任务并收集证据；不得评价自己的完成度。",
            "evaluator": "依据完成条件和外部证据返回 pass、retry、replan、block 或 complete。",
        }
        protocol = [
            "载入并校验合同、状态和最近交接。",
            "Planner 选择依赖已满足的任务并记录选择理由。",
            "Worker 在已授权范围内执行一个任务，随后转为 `awaiting_evaluation`。",
            "Evaluator 独立检查证据并决定完成、重试、重规划或阻塞。",
            "追加进度记录，写入检查点，刷新交接文件，再决定停止或开启新上下文。",
        ]
        queue_note = "以 `state.json` 为唯一机器任务状态；不得在此文件复制可变任务队列。"
        checkpoint_note = "在指定频率写入检查点；上下文重置前必须保存状态、追加进度并刷新交接。"
        change_note = "目标、完成条件、约束、权限、审批门或预算的变化需要用户明确批准、合同版本递增、两个哈希更新，并在进度账本记录批准依据。"
    else:
        start_steps = [
            "Run package validation and do not start when validation fails.",
            "Read `WORKFLOW.md`, `state.json`, the latest `progress.md` entry, and `handoff.md` in that order.",
            "Move `ready` to `running` only after a separate start instruction.",
            "Run only dependency-ready tasks selected by the planner; parallel mode still requires isolated ownership.",
        ]
        role_lines = {
            "planner": "Select or revise the next bounded task; do not execute it or declare the overall goal complete.",
            "worker": "Execute only the selected task and collect evidence; do not grade your own completion.",
            "evaluator": "Use the completion conditions and external evidence to return pass, retry, replan, block, or complete.",
        }
        protocol = [
            "Load and validate the contract, state, and latest handoff.",
            "Have the planner select a dependency-ready task and record why.",
            "Have the worker act within authority, then move the task to `awaiting_evaluation`.",
            "Have the evaluator independently decide complete, retry, replan, or block.",
            "Append progress, checkpoint state, refresh the handoff, then stop or start a clean iteration.",
        ]
        queue_note = "Treat `state.json` as the only machine task state; do not duplicate the mutable queue here."
        checkpoint_note = "Checkpoint at the configured frequency. Before a context reset, save state, append progress, and refresh the handoff."
        change_note = "Changes to the goal, completion conditions, constraints, authority, approval gates, or limits require explicit user approval, a contract-version increase, both hashes updated, and approval evidence appended to progress."

    sections = [
        "# {}: {}".format(text["title"], spec["title"]),
        "- Schema version: `{}`\n- Template: `{}@{}`\n- Instance ID: `{}`\n- Domain: `{}`\n- Execution mode: `{}`\n- Contract version: `{}`\n- Input bindings SHA-256: `{}`\n\n> {}".format(
            spec["schema_version"],
            spec["template"]["id"],
            spec["template"]["version"],
            slug,
            spec["domain"],
            spec["execution_mode"],
            contract_version,
            spec["input_bindings_sha256"],
            text["notice"],
        ),
        "## {}\n\n{}".format(text["start"], markdown_bullets(start_steps)),
        "## {}\n\n{}".format(text["goal"], spec["goal"]),
        "## {}\n\n{}".format(text["audience"], spec["audience"]),
        "## {}\n\n{}".format(text["inputs"], markdown_bullets(spec["inputs"])),
        "## {}\n\n### {}\n\n```json\n{}\n```\n\n### {}\n\n```json\n{}\n```".format(
            text["input_contract"],
            text["input_schema"],
            json.dumps(spec["input_schema"], ensure_ascii=False, indent=2),
            text["input_bindings"],
            json.dumps(spec["input_bindings"], ensure_ascii=False, indent=2),
        ),
        "## {}\n\n{}".format(
            text["done"], markdown_bullets(spec["done_conditions"], checkboxes=True)
        ),
        "## {}\n\n{}".format(text["invariants"], markdown_bullets(invariants)),
        "## {}\n\n### {}\n\n{}\n\n### {}\n\n{}\n\n### {}\n\n{}".format(
            text["roles"],
            text["planner"],
            role_lines["planner"],
            text["worker"],
            role_lines["worker"],
            text["evaluator"],
            role_lines["evaluator"],
        ),
        "## {}\n\n{}".format(text["queue"], queue_note),
        "## {}\n\n{}".format(text["protocol"], markdown_bullets(protocol)),
        "## {}\n\n{}".format(
            text["verification"], markdown_bullets(spec["verification"])
        ),
        "## {}\n\n- risk_level: `{}`\n\n### {}\n\n{}\n\n### {}\n\n{}\n\n### {}\n\n{}\n\n### {}\n\n{}\n\n{}".format(
            text["authority"],
            spec["authority"]["risk_level"],
            text["automatic"],
            markdown_bullets(spec["authority"]["auto_allowed"]),
            text["approval"],
            markdown_bullets(approval),
            text["forbidden"],
            markdown_bullets(spec["authority"]["forbidden"]),
            text["credentials"],
            spec["authority"]["credential_policy"],
            text["secret_notice"],
        ),
        "## {}\n\n- {}: {}\n- {}:\n{}\n\n{}".format(
            text["checkpoint"],
            text["frequency"],
            spec["checkpoint"]["frequency"],
            text["required_evidence"],
            markdown_bullets(spec["checkpoint"]["required_evidence"]),
            checkpoint_note,
        ),
        "## {}\n\n{}".format(text["limits"], markdown_bullets(limit_lines)),
        "## {}\n\n{}".format(text["changes"], change_note),
    ]
    return "\n\n".join(sections).rstrip() + "\n"


def render_v3_workflow(
    spec: Dict[str, Any], slug: str, contract_version: int = 1
) -> str:
    chinese = spec["language"].lower().startswith("zh")
    notice = (
        "此包只定义工作流；创建或更新批准不构成启动目标任务的授权。"
        if chinese
        else "This package defines a workflow only; creation or update approval does not authorize starting its target task."
    )
    role_text = (
        "Planner 只选择有界节点；Worker 只执行所选节点并收集证据；Evaluator 只评价节点证据；Final Evaluator 只按全局条件覆盖决定完成。"
        if chinese
        else "The Planner selects one bounded node; the Worker executes it and collects evidence; the Evaluator grades node evidence; the Final Evaluator decides completion only from global condition coverage."
    )
    memory_text = (
        "Runtime 只能从 planner 决议、verifier 结果、用户 resolution、checkpoint 和错误生成工作流局部记录。模型不得自由写入事实；外部 MemoryProvider 候选只读且不得自动持久化。"
        if chinese
        else "Runtime memory is workflow-local and may be derived only from planner decisions, verifier results, user resolutions, checkpoints, and errors. Models cannot freely write facts; external MemoryProvider candidates are read-only and are never persisted automatically."
    )
    context_text = (
        "按 planner、worker、evaluator、final_evaluator 分别组装最小上下文。按每个 UTF-8 字节计一个 token 做保守估算；合同、权限或必需证据超预算时必须失败，不得静默裁剪。"
        if chinese
        else "Assemble separate minimal contexts for planner, worker, evaluator, and final_evaluator. Estimate tokens conservatively as one token per UTF-8 byte; fail closed rather than silently truncating contract, authority, or required evidence."
    )
    sections = [
        "# Loop Workflow: {}".format(spec["title"]),
        "- Schema version: `{}`\n- Template: `{}@{}`\n- Instance ID: `{}`\n- Domain: `{}`\n- Execution mode: `{}`\n- Contract version: `{}`\n- Input bindings SHA-256: `{}`\n\n> {}".format(
            CURRENT_SCHEMA_VERSION,
            spec["template"]["id"],
            spec["template"]["version"],
            slug,
            spec["domain"],
            spec["execution_mode"],
            contract_version,
            spec["input_bindings_sha256"],
            notice,
        ),
        "## Goal\n\n{}".format(spec["goal"]),
        "## Audience\n\n{}".format(spec["audience"]),
        "## Inputs and bindings\n\n{}\n\n```json\n{}\n```\n\n```json\n{}\n```".format(
            markdown_bullets(spec["inputs"]),
            json.dumps(spec["input_schema"], ensure_ascii=False, indent=2),
            json.dumps(spec["input_bindings"], ensure_ascii=False, indent=2),
        ),
        "## Invariants\n\n{}".format(
            markdown_bullets(spec["invariants"] or ["No additional invariant."])
        ),
        "## Completion contract\n\n### Conditions\n\n```json\n{}\n```\n\n### Evidence requirements\n\n```json\n{}\n```".format(
            json.dumps(spec["conditions"], ensure_ascii=False, indent=2),
            json.dumps(spec["evidence_requirements"], ensure_ascii=False, indent=2),
        ),
        "## Typed initial graph\n\n```json\n{}\n```".format(
            json.dumps(spec["initial_graph"], ensure_ascii=False, indent=2)
        ),
        "## Role separation\n\n{}".format(role_text),
        "## Authority\n\n```json\n{}\n```\n\nNever store secret values in this package.".format(
            json.dumps(spec["authority"], ensure_ascii=False, indent=2)
        ),
        "## Limits, checkpoints, and circuit breakers\n\n```json\n{}\n```\n\n```json\n{}\n```\n\n```json\n{}\n```".format(
            json.dumps(spec["limits"], ensure_ascii=False, indent=2),
            json.dumps(spec["checkpoint"], ensure_ascii=False, indent=2),
            json.dumps(spec["circuit_breakers"], ensure_ascii=False, indent=2),
        ),
        "## Memory policy\n\n{}\n\n```json\n{}\n```".format(
            memory_text, json.dumps(spec["memory_policy"], ensure_ascii=False, indent=2)
        ),
        "## Context policy\n\n{}\n\n```json\n{}\n```".format(
            context_text, json.dumps(spec["context_policy"], ensure_ascii=False, indent=2)
        ),
        "## Start, checkpoint, and change protocol\n\n{}".format(
            markdown_bullets(
                [
                    "Validate all four core files before a separate start instruction.",
                    "A node is runnable only when every required input has a typed upstream output reference with digest and summary.",
                    "Record node evidence, evaluate it independently, update condition coverage and breaker counters, then checkpoint on every required trigger.",
                    "Before context reset, append progress, update its hash-chain head, refresh handoff.md, and update its SHA-256.",
                    "Goal, conditions, invariants, authority, gates, graph blueprint, or limits may change only through an explicitly approved versioned update.",
                ]
            )
        ),
    ]
    return "\n\n".join(sections).rstrip() + "\n"


def render_workflow(
    spec: Dict[str, Any], slug: str, contract_version: int = 1
) -> str:
    if spec["schema_version"] == CURRENT_SCHEMA_VERSION:
        return render_v3_workflow(spec, slug, contract_version)
    return render_v2_workflow(spec, slug, contract_version)


def immutable_v2_definition(spec: Dict[str, Any]) -> Dict[str, Any]:
    definition = {
        key: spec[key]
        for key in (
            "title",
            "template",
            "language",
            "domain",
            "execution_mode",
            "goal",
            "audience",
            "inputs",
            "input_schema",
            "input_bindings",
            "input_bindings_sha256",
            "invariants",
            "done_conditions",
            "verification",
            "authority",
            "limits",
            "checkpoint",
            "stop_conditions",
        )
    }
    definition["initial_tasks"] = spec["tasks"]
    return definition


def immutable_v3_definition(spec: Dict[str, Any]) -> Dict[str, Any]:
    return {
        key: spec[key]
        for key in (
            "title",
            "template",
            "language",
            "domain",
            "execution_mode",
            "goal",
            "audience",
            "inputs",
            "input_schema",
            "input_bindings",
            "input_bindings_sha256",
            "invariants",
            "conditions",
            "evidence_requirements",
            "initial_graph",
            "authority",
            "limits",
            "checkpoint",
            "circuit_breakers",
            "memory_policy",
            "context_policy",
        )
    }


def auto_budget(spec: Dict[str, Any]) -> Dict[str, Any]:
    nodes = spec["initial_graph"]["nodes"]
    node_count = len(nodes)
    edge_count = len(spec["initial_graph"]["edges"])
    condition_count = len(spec["conditions"])
    attempts = sum(node["max_attempts"] for node in nodes)
    budgets = {
        "planner": min(24000, 8000 + 1000 * node_count),
        "worker": min(48000, 16000 + 2000 * node_count),
        "evaluator": min(24000, 8000 + 1000 * condition_count),
        "final_evaluator": min(16000, 8000 + 1000 * condition_count),
    }
    return {
        "role_token_budgets": budgets,
        "max_iterations": attempts,
        "max_minutes": max(60, min(480, 30 * node_count + 15 * edge_count)),
        "max_total_tokens": attempts
        * (budgets["planner"] + budgets["worker"] + budgets["evaluator"])
        + budgets["final_evaluator"],
    }


def normalize_runtime_policy_rule(value: Any, name: str) -> Dict[str, Any]:
    rule = require_dict(value, name)
    allowed = {"authority_id", "tool", "capability", "targets", "argv_prefix", "methods", "hosts"}
    reject_unknown(rule, allowed, name)
    result: Dict[str, Any] = {
        "authority_id": require_stable_id(rule.get("authority_id"), name + ".authority_id"),
        "tool": require_text(rule.get("tool"), name + ".tool"),
    }
    if result["tool"] not in RUNTIME_TOOLS:
        raise ValidationError("{}.tool is unsupported".format(name))
    for field in ("targets", "argv_prefix", "methods", "hosts"):
        if field in rule:
            result[field] = require_string_list(rule[field], name + "." + field)
    if "methods" in result:
        result["methods"] = [item.upper() for item in result["methods"]]
    if "hosts" in result:
        result["hosts"] = [item.lower() for item in result["hosts"]]
    if "capability" in rule:
        result["capability"] = require_text(rule["capability"], name + ".capability")
    return result


def normalize_runtime_verifier(value: Any, name: str) -> Dict[str, Any]:
    verifier = require_dict(value, name)
    allowed = {
        "id", "type", "requirement_id", "condition_id", "task_id", "argv", "cwd", "path",
        "schema_path", "contains", "url", "method", "expected_status", "timeout_seconds",
        "environment", "host", "target",
    }
    reject_unknown(verifier, allowed, name)
    verifier_type = require_text(verifier.get("type"), name + ".type")
    if verifier_type not in VERIFIER_TYPES:
        raise ValidationError("{}.type is unsupported".format(name))
    result: Dict[str, Any] = {
        "id": require_stable_id(verifier.get("id"), name + ".id"),
        "type": verifier_type,
        "requirement_id": require_stable_id(
            verifier.get("requirement_id"), name + ".requirement_id"
        ),
    }
    for field in ("condition_id", "task_id"):
        if field in verifier:
            result[field] = require_stable_id(verifier[field], name + "." + field)
    for field in ("cwd", "path", "schema_path", "contains", "url", "method", "host", "target"):
        if field in verifier:
            result[field] = require_text(verifier[field], name + "." + field)
    for field in ("argv", "environment"):
        if field in verifier:
            result[field] = require_string_list(verifier[field], name + "." + field)
    if "expected_status" in verifier:
        status = verifier["expected_status"]
        if isinstance(status, bool) or not isinstance(status, int) or not 100 <= status <= 599:
            raise ValidationError("{}.expected_status must be 100..599".format(name))
        result["expected_status"] = status
    if "timeout_seconds" in verifier:
        result["timeout_seconds"] = optional_positive_number(
            verifier["timeout_seconds"], name + ".timeout_seconds"
        )
    return result


def build_runtime_recommendation(
    spec: Dict[str, Any], slug: str, contract_sha256: str, raw: Any = None
) -> Dict[str, Any]:
    supplied = {} if raw is None else require_dict(raw, "runtime_recommendation")
    allowed = {"models", "execution", "policy", "verifiers", "credentials", "inference_manifest", "review"}
    reject_unknown(supplied, allowed, "runtime_recommendation")
    budget = auto_budget(spec)

    raw_models = require_dict(supplied.get("models", {}), "runtime_recommendation.models")
    reject_unknown(raw_models, set(RUNTIME_ROLES), "runtime_recommendation.models")
    models: Dict[str, Any] = {}
    for role in RUNTIME_ROLES:
        raw_model = require_dict(raw_models.get(role, {}), "runtime_recommendation.models." + role)
        reject_unknown(
            raw_model,
            {"reasoning_required", "min_context_tokens", "cost_preference"},
            "runtime_recommendation.models." + role,
        )
        models[role] = {
            "reasoning_required": raw_model.get("reasoning_required", role != "worker"),
            "min_context_tokens": require_positive_integer(
                raw_model.get("min_context_tokens", budget["role_token_budgets"][role] + 4096),
                "runtime_recommendation.models.{}.min_context_tokens".format(role),
            ),
            "cost_preference": require_text(
                raw_model.get("cost_preference", "lowest_known"),
                "runtime_recommendation.models.{}.cost_preference".format(role),
            ),
        }
        if not isinstance(models[role]["reasoning_required"], bool):
            raise ValidationError(
                "runtime_recommendation.models.{}.reasoning_required must be boolean".format(role)
            )
        if models[role]["cost_preference"] != "lowest_known":
            raise ValidationError(
                "runtime_recommendation.models.{}.cost_preference must be lowest_known".format(role)
            )
        minimum_context = spec["context_policy"]["role_token_budgets"][role] + 4096
        if models[role]["min_context_tokens"] < minimum_context:
            raise ValidationError(
                "runtime_recommendation.models.{}.min_context_tokens must reserve 4096 output tokens".format(role)
            )

    execution = {
        "max_concurrency": 1 if spec["execution_mode"] == "sequential" else min(4, len(spec["initial_graph"]["nodes"])),
        "role_timeout_seconds": 900,
        "max_provider_retries": 3,
        "max_output_repairs": 2,
        "git_worktrees": spec["domain"] == "coding",
    }
    raw_execution = require_dict(
        supplied.get("execution", {}), "runtime_recommendation.execution"
    )
    reject_unknown(raw_execution, set(execution), "runtime_recommendation.execution")
    execution.update(raw_execution)
    execution["max_concurrency"] = require_positive_integer(
        execution["max_concurrency"], "runtime_recommendation.execution.max_concurrency"
    )
    if execution["max_concurrency"] > 64:
        raise ValidationError("runtime_recommendation.execution.max_concurrency must be at most 64")
    execution["role_timeout_seconds"] = optional_positive_number(
        execution["role_timeout_seconds"],
        "runtime_recommendation.execution.role_timeout_seconds",
    )
    for field, maximum in (("max_provider_retries", 3), ("max_output_repairs", 2)):
        value = execution[field]
        if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= maximum:
            raise ValidationError(
                "runtime_recommendation.execution.{} must be an integer from 0 to {}".format(
                    field, maximum
                )
            )
    if not isinstance(execution["git_worktrees"], bool):
        raise ValidationError("runtime_recommendation.execution.git_worktrees must be boolean")

    raw_policy = require_dict(supplied.get("policy", {}), "runtime_recommendation.policy")
    reject_unknown(raw_policy, {"allow", "approve", "deny"}, "runtime_recommendation.policy")
    policy: Dict[str, List[Dict[str, Any]]] = {}
    for effect in ("allow", "approve", "deny"):
        raw_rules = raw_policy.get(effect)
        if raw_rules is None:
            raw_rules = [
                {"authority_id": rule["authority_id"], "tool": "*"}
                for rule in spec["authority"]["rules"]
                if rule["effect"] == effect and effect == "deny"
            ]
        if not isinstance(raw_rules, list):
            raise ValidationError("runtime_recommendation.policy.{} must be an array".format(effect))
        policy[effect] = [
            normalize_runtime_policy_rule(item, "runtime_recommendation.policy.{}[{}]".format(effect, index))
            for index, item in enumerate(raw_rules)
        ]

    raw_verifiers = supplied.get("verifiers", [])
    if not isinstance(raw_verifiers, list):
        raise ValidationError("runtime_recommendation.verifiers must be an array")
    verifiers = [
        normalize_runtime_verifier(item, "runtime_recommendation.verifiers[{}]".format(index))
        for index, item in enumerate(raw_verifiers)
    ]
    requirement_ids = {item["id"] for item in spec["evidence_requirements"]}
    condition_ids = {item["id"] for item in spec["conditions"]}
    authority = {item["authority_id"]: item["effect"] for item in spec["authority"]["rules"]}
    for effect, rules in policy.items():
        for rule in rules:
            if authority.get(rule["authority_id"]) != effect:
                raise ValidationError(
                    "runtime recommendation cannot expand authority {}".format(rule["authority_id"])
                )
            if effect in {"allow", "approve"}:
                if rule["tool"] == "*":
                    raise ValidationError("runtime recommendation allow/approve rules require an exact tool")
                if not any(rule.get(field) for field in ("targets", "argv_prefix", "methods", "hosts", "capability")):
                    raise ValidationError("runtime recommendation allow/approve rules require narrowed scope")
                if rule["tool"] == "shell_argv" and not rule.get("argv_prefix"):
                    raise ValidationError("runtime recommendation shell_argv rules require argv_prefix")
                if rule["tool"] in {"http_fetch", "web_search"} and not rule.get("hosts"):
                    raise ValidationError("runtime recommendation network rules require hosts")
                if rule["tool"] == "http_fetch" and not rule.get("methods"):
                    raise ValidationError("runtime recommendation http_fetch rules require methods")
                if rule["tool"] in {"read", "grep", "find", "ls", "edit", "write"} and not rule.get("targets"):
                    raise ValidationError("runtime recommendation filesystem rules require targets")
    requirement_by_id = {item["id"]: item for item in spec["evidence_requirements"]}
    condition_by_id = {item["id"]: item for item in spec["conditions"]}
    verifier_ids: Set[str] = set()
    for verifier in verifiers:
        if verifier["requirement_id"] not in requirement_ids:
            raise ValidationError("runtime recommendation verifier references unknown requirement")
        if "condition_id" in verifier and verifier["condition_id"] not in condition_ids:
            raise ValidationError("runtime recommendation verifier references unknown condition")
        if verifier["id"] in verifier_ids:
            raise ValidationError("runtime recommendation contains duplicate verifier IDs")
        verifier_ids.add(verifier["id"])
        verifier_type = verifier["type"]
        if verifier_type == "command" and not verifier.get("argv"):
            raise ValidationError("runtime recommendation command verifier requires argv")
        if verifier_type in {"file", "schema"} and not verifier.get("path"):
            raise ValidationError("runtime recommendation file/schema verifier requires path")
        if verifier_type == "schema" and not verifier.get("schema_path"):
            raise ValidationError("runtime recommendation schema verifier requires schema_path")
        if verifier_type == "http":
            if not all(verifier.get(field) for field in ("url", "host", "method", "target")):
                raise ValidationError("runtime recommendation HTTP verifier requires url, host, method, and target")
            parsed = urlparse(verifier["url"])
            if parsed.scheme not in {"http", "https"} or parsed.hostname != verifier["host"].lower():
                raise ValidationError("runtime recommendation HTTP verifier URL does not match host")
            target = verifier["target"]
            if not target.startswith("/") or not (
                parsed.path == target or parsed.path.startswith(target + "/")
            ):
                raise ValidationError("runtime recommendation HTTP verifier is outside target scope")
            if not re.fullmatch(r"[A-Z]+", verifier["method"]):
                raise ValidationError("runtime recommendation HTTP verifier method must be uppercase")
        requirement = requirement_by_id[verifier["requirement_id"]]
        if (requirement["type"] == "human_attestation") != (verifier_type == "human_attestation"):
            raise ValidationError("runtime recommendation verifier type does not match requirement")
        if requirement["type"] == "independent_evaluator":
            raise ValidationError("independent evaluator requirements cannot bind verifiers")
        if verifier_type == "human_attestation":
            condition_id = verifier.get("condition_id")
            if not condition_id:
                raise ValidationError("human attestation verifier requires condition_id")
            if verifier["requirement_id"] not in condition_by_id[condition_id]["evidence_requirement_ids"]:
                raise ValidationError("human attestation condition does not bind its requirement")

    raw_credentials = require_dict(
        supplied.get("credentials", {"environment": spec["authority"].get("credential_env", [])}),
        "runtime_recommendation.credentials",
    )
    reject_unknown(raw_credentials, {"environment"}, "runtime_recommendation.credentials")
    environment = require_string_list(
        raw_credentials.get("environment", []),
        "runtime_recommendation.credentials.environment",
        allow_empty=True,
    )
    if not set(environment).issubset(set(spec["authority"].get("credential_env", []))):
        raise ValidationError("runtime recommendation credentials exceed contract authority")
    if len(environment) != len(set(environment)):
        raise ValidationError("runtime recommendation credential environment names must be unique")
    for verifier in verifiers:
        selected = verifier.get("environment", [])
        if len(selected) != len(set(selected)) or not set(selected).issubset(set(environment)):
            raise ValidationError("runtime recommendation verifier environment is not declared")

    raw_manifest = supplied.get("inference_manifest", [])
    if not isinstance(raw_manifest, list):
        raise ValidationError("runtime_recommendation.inference_manifest must be an array")
    manifest = []
    for index, raw_entry in enumerate(raw_manifest):
        name = "runtime_recommendation.inference_manifest[{}]".format(index)
        entry = require_dict(raw_entry, name)
        reject_unknown(entry, {"path", "status", "confidence", "source_refs", "rationale"}, name)
        status = require_text(entry.get("status"), name + ".status")
        confidence = require_text(entry.get("confidence"), name + ".confidence")
        if status not in INFERENCE_STATUSES or confidence not in CONFIDENCE_LEVELS:
            raise ValidationError("{} has invalid status or confidence".format(name))
        raw_source_refs = entry.get("source_refs", [])
        if not isinstance(raw_source_refs, list):
            raise ValidationError(name + ".source_refs must be an array")
        source_refs = []
        for source_index, raw_source in enumerate(raw_source_refs):
            source_name = "{}.source_refs[{}]".format(name, source_index)
            source = require_dict(raw_source, source_name)
            reject_unknown(source, {"uri", "digest"}, source_name)
            digest = require_text(source.get("digest"), source_name + ".digest")
            if not re.fullmatch(r"[a-f0-9]{64}", digest):
                raise ValidationError(source_name + ".digest must be a SHA-256 hex digest")
            source_refs.append(
                {
                    "uri": require_text(source.get("uri"), source_name + ".uri"),
                    "digest": digest,
                }
            )
        if status == "inferred" and not source_refs:
            raise ValidationError(name + ".source_refs must prove inferred fields")
        manifest.append(
            {
                "path": require_text(entry.get("path"), name + ".path"),
                "status": status,
                "confidence": confidence,
                "source_refs": source_refs,
                "rationale": require_text(entry.get("rationale"), name + ".rationale"),
            }
        )

    manifest_paths = {entry["path"] for entry in manifest}
    for path in spec.get("_auto_default_paths", []):
        if path not in manifest_paths:
            manifest.append(
                {
                    "path": path,
                    "status": "defaulted",
                    "confidence": "high",
                    "source_refs": [],
                    "rationale": "Applied the published deterministic create-loop default.",
                }
            )
            manifest_paths.add(path)
    if "models" not in supplied:
        for role in RUNTIME_ROLES:
            path = "/models/{}".format(role)
            if path not in manifest_paths:
                manifest.append(
                    {
                        "path": path,
                        "status": "defaulted",
                        "confidence": "high",
                        "source_refs": [],
                        "rationale": "Derived from the role budget plus the 4096-token output reserve.",
                    }
                )
                manifest_paths.add(path)
    for field in ("execution", "credentials"):
        path = "/{}".format(field)
        if field not in supplied and path not in manifest_paths:
            manifest.append(
                {
                    "path": path,
                    "status": "defaulted",
                    "confidence": "high",
                    "source_refs": [],
                    "rationale": "Applied a deterministic contract-derived runtime default.",
                }
            )
            manifest_paths.add(path)

    covered = {
        verifier["requirement_id"] for verifier in verifiers if "task_id" not in verifier
    }
    for verifier in verifiers:
        path = "/verifiers/{}".format(verifier["requirement_id"])
        if path not in manifest_paths:
            manifest.append(
                {
                    "path": path,
                    "status": "needs_input",
                    "confidence": "low",
                    "source_refs": [],
                    "rationale": "Verifier mapping has no repository provenance and requires confirmation.",
                }
            )
            manifest_paths.add(path)
    for requirement in spec["evidence_requirements"]:
        if requirement["type"] == "independent_evaluator":
            continue
        path = "/verifiers/{}".format(requirement["id"])
        if requirement["id"] not in covered and path not in manifest_paths:
            manifest.append(
                {
                    "path": path,
                    "status": "needs_input",
                    "confidence": "low",
                    "source_refs": [],
                    "rationale": "No safe global verifier could be inferred for this requirement.",
                }
            )
            manifest_paths.add(path)
    mapped_authority = {
        rule["authority_id"] for effect in ("allow", "approve") for rule in policy[effect]
    }
    for effect in ("allow", "approve"):
        for rule in policy[effect]:
            path = "/policy/{}/{}".format(effect, rule["authority_id"])
            if path not in manifest_paths:
                manifest.append(
                    {
                        "path": path,
                        "status": "needs_input",
                        "confidence": "low",
                        "source_refs": [],
                        "rationale": "Runtime scope mapping has no repository provenance and requires confirmation.",
                    }
                )
                manifest_paths.add(path)
    for rule in spec["authority"]["rules"]:
        path = "/policy/{}/{}".format(rule["effect"], rule["authority_id"])
        if (
            rule["effect"] in {"allow", "approve"}
            and rule["authority_id"] not in mapped_authority
            and path not in manifest_paths
        ):
            manifest.append(
                {
                    "path": path,
                    "status": "needs_input",
                    "confidence": "low",
                    "source_refs": [],
                    "rationale": "No safely scoped runtime tool mapping could be inferred.",
                }
            )

    review = {
        "goal": spec["goal"],
        "steps": [node["title"] for node in spec["initial_graph"]["nodes"]],
        "completion": [condition["description"] for condition in spec["conditions"]],
        "permissions": [rule["description"] for rule in spec["authority"]["rules"]],
        "budget": {
            "max_minutes": spec["limits"]["max_minutes"],
            "max_total_tokens": spec["limits"]["max_total_tokens"],
            "max_cost": spec["limits"]["max_cost"],
            "cost_currency": spec["limits"]["cost_currency"],
        },
    }
    raw_review = require_dict(supplied.get("review", {}), "runtime_recommendation.review")
    reject_unknown(raw_review, set(review), "runtime_recommendation.review")
    review.update(raw_review)
    for field in ("goal",):
        review[field] = require_text(review[field], "runtime_recommendation.review." + field)
    for field in ("steps", "completion", "permissions"):
        review[field] = require_string_list(
            review[field], "runtime_recommendation.review." + field, allow_empty=True
        )
    raw_budget = require_dict(review["budget"], "runtime_recommendation.review.budget")
    reject_unknown(
        raw_budget,
        {"max_minutes", "max_total_tokens", "max_cost", "cost_currency"},
        "runtime_recommendation.review.budget",
    )
    review["budget"] = {
        "max_minutes": optional_positive_number(
            raw_budget.get("max_minutes"), "runtime_recommendation.review.budget.max_minutes"
        ),
        "max_total_tokens": optional_positive_number(
            raw_budget.get("max_total_tokens"),
            "runtime_recommendation.review.budget.max_total_tokens",
            integer=True,
        ),
        "max_cost": optional_positive_number(
            raw_budget.get("max_cost"), "runtime_recommendation.review.budget.max_cost"
        ),
        "cost_currency": None
        if raw_budget.get("cost_currency") is None
        else require_text(
            raw_budget.get("cost_currency"),
            "runtime_recommendation.review.budget.cost_currency",
        ),
    }
    return {
        "schema_version": RECOMMENDATION_SCHEMA_VERSION,
        "loop_id": slug,
        "contract_sha256": contract_sha256,
        "template": spec["template"],
        "status": "needs_input"
        if any(entry["status"] == "needs_input" for entry in manifest)
        else "complete",
        "models": models,
        "execution": execution,
        "policy": policy,
        "verifiers": verifiers,
        "credentials": {"environment": environment},
        "inference_manifest": manifest,
        "review": review,
    }


def validate_runtime_recommendation(value: Any, state: Dict[str, Any]) -> Dict[str, Any]:
    envelope = require_dict(value, "runtime recommendation")
    allowed = {
        "schema_version", "loop_id", "contract_sha256", "template", "status", "models",
        "execution", "policy", "verifiers", "credentials", "inference_manifest", "review",
    }
    reject_unknown(envelope, allowed, "runtime recommendation")
    required = allowed
    missing = sorted(required - set(envelope))
    if missing:
        raise ValidationError(
            "runtime recommendation is missing fields: {}".format(", ".join(missing))
        )
    definition = normalize_v3_definition(state["contract"]["definition"])
    spec = {"schema_version": CURRENT_SCHEMA_VERSION, **definition}
    raw = {key: envelope[key] for key in (
        "models", "execution", "policy", "verifiers", "credentials", "inference_manifest", "review"
    )}
    normalized = build_runtime_recommendation(
        spec, state["loop_id"], state["contract"]["sha256"], raw
    )
    if envelope.get("schema_version") != RECOMMENDATION_SCHEMA_VERSION:
        raise ValidationError("runtime recommendation schema_version must be 1.0")
    if envelope.get("loop_id") != state["loop_id"]:
        raise ValidationError("runtime recommendation loop_id is stale")
    if envelope.get("contract_sha256") != state["contract"]["sha256"]:
        raise ValidationError("runtime recommendation contract_sha256 is stale")
    if envelope.get("template") != definition["template"]:
        raise ValidationError("runtime recommendation template is stale")
    # Generated envelope fields are authoritative; compare the normalized payload.
    if envelope != normalized:
        raise ValidationError("runtime recommendation is not canonical")
    return normalized


def build_v2_state(spec: Dict[str, Any], slug: str, workflow: str, now: str) -> Dict[str, Any]:
    definition = immutable_v2_definition(spec)
    return {
        "schema_version": spec["schema_version"],
        "loop_id": slug,
        "status": "ready",
        "contract": {
            "version": 1,
            "sha256": sha256_bytes(canonical_json(definition)),
            "workflow_sha256": sha256_bytes(workflow.encode("utf-8")),
            "definition": definition,
        },
        "iteration": {
            "current": 0,
            "max": spec["limits"]["max_iterations"],
        },
        "usage": {"elapsed_minutes": 0, "cost": 0},
        "active_task_ids": [],
        "tasks": [
            {
                "id": task["id"],
                "title": task["title"],
                "description": task["description"],
                "status": "pending",
                "dependencies": task["dependencies"],
                "acceptance_criteria": task["acceptance_criteria"],
                "evidence": [],
            }
            for task in spec["tasks"]
        ],
        "completion_evidence": [],
        "pending_approval": None,
        "last_checkpoint": None,
        "started_at": None,
        "updated_at": now,
    }


def build_v3_state(
    spec: Dict[str, Any], slug: str, workflow: str, progress: str, handoff: str, now: str
) -> Dict[str, Any]:
    definition = immutable_v3_definition(spec)
    dependencies: Dict[str, List[str]] = {
        node["id"]: [] for node in spec["initial_graph"]["nodes"]
    }
    for edge in spec["initial_graph"]["edges"]:
        dependency = edge["from"]["node_id"]
        target = edge["to"]["node_id"]
        if dependency not in dependencies[target]:
            dependencies[target].append(dependency)
    return {
        "schema_version": CURRENT_SCHEMA_VERSION,
        "loop_id": slug,
        "status": "ready",
        "contract": {
            "version": 1,
            "sha256": sha256_bytes(canonical_json(definition)),
            "workflow_sha256": sha256_bytes(workflow.encode("utf-8")),
            "definition": definition,
        },
        "iteration": {"current": 0, "max": spec["limits"]["max_iterations"]},
        "usage": {"elapsed_minutes": 0, "cost": 0, "total_tokens": 0},
        "active_task_ids": [],
        "tasks": [
            {
                "id": node["id"],
                "title": node["title"],
                "description": node["description"],
                "status": "pending",
                "dependencies": dependencies[node["id"]],
                "acceptance_criteria": node["acceptance_criteria"],
                "evidence": [],
            }
            for node in spec["initial_graph"]["nodes"]
        ],
        "completion_evidence": [],
        "node_outputs": [],
        "condition_coverage": [
            {
                "condition_id": condition["id"],
                "requirement_results": [
                    {"requirement_id": requirement_id, "result": "pending", "evidence": []}
                    for requirement_id in condition["evidence_requirement_ids"]
                ],
            }
            for condition in spec["conditions"]
        ],
        "breaker_counters": {
            breaker["id"]: 0 for breaker in spec["circuit_breakers"]
        },
        "memory_index_head": None,
        "progress_hash_chain": {
            "head_sha256": progress_chain_next(None, progress),
            "entries": 1,
        },
        "handoff_sha256": sha256_bytes(handoff.encode("utf-8")),
        "pending_approval": None,
        "last_checkpoint": None,
        "started_at": None,
        "updated_at": now,
    }


def render_progress(slug: str, now: str, language: str) -> str:
    if language.lower().startswith("zh"):
        return """# Progress Ledger

> 只追加记录。不要编辑或删除历史条目；更正请追加新条目。

## Created {now}

- Loop ID: `{slug}`
- Transition: `uninitialized -> ready`
- Evidence: 工作流包已创建并通过结构校验。
- Next: 等待独立启动指令。

<!-- 每轮追加：时间、迭代、任务、动作、证据、Evaluator 结论、状态迁移、失败/阻塞和下一步。 -->
""".format(now=now, slug=slug)
    return """# Progress Ledger

> Append only. Do not edit or delete historical entries; append corrections.

## Created {now}

- Loop ID: `{slug}`
- Transition: `uninitialized -> ready`
- Evidence: Workflow package created and structurally validated.
- Next: Wait for a separate start instruction.

<!-- Append each iteration's timestamp, number, task, actions, evidence, evaluator result, state transition, failure or blocker, and next action. -->
""".format(now=now, slug=slug)


def render_handoff(spec: Dict[str, Any], slug: str, now: str) -> str:
    if spec["language"].lower().startswith("zh"):
        return """# Loop Handoff

- Updated: {now}
- Loop ID: `{slug}`
- Status: `ready`

## 目标与约束

{goal}

读取 `WORKFLOW.md` 获取不可变完成条件、权限和预算。

## 已验证进度

- 工作流包已创建并通过结构校验。
- 尚未执行任何目标任务。

## 待处理

- 等待用户发出独立启动指令。
- 启动前重新运行包校验。

## 下一动作

读取 `WORKFLOW.md` 和 `state.json`；不得把创建确认解释为启动授权。
""".format(now=now, slug=slug, goal=spec["goal"])
    return """# Loop Handoff

- Updated: {now}
- Loop ID: `{slug}`
- Status: `ready`

## Goal and constraints

{goal}

Read `WORKFLOW.md` for immutable completion, authority, and limit rules.

## Verified progress

- The workflow package was created and structurally validated.
- No target task has been executed.

## Pending

- Wait for a separate user instruction to start.
- Re-run package validation before starting.

## Next action

Read `WORKFLOW.md` and `state.json`. Do not interpret creation confirmation as start authorization.
""".format(now=now, slug=slug, goal=spec["goal"])


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def load_state(path: Path) -> Dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError("cannot read state.json: {}".format(exc))
    return require_dict(value, "state.json")


def validate_legacy_state(state: Dict[str, Any], workflow: bytes) -> None:
    required = {
        "schema_version",
        "loop_id",
        "status",
        "contract",
        "iteration",
        "usage",
        "active_task_ids",
        "tasks",
        "completion_evidence",
        "pending_approval",
        "last_checkpoint",
        "started_at",
        "updated_at",
    }
    missing = sorted(required - set(state))
    if missing:
        raise ValidationError("state.json missing field(s): {}".format(", ".join(missing)))
    reject_unknown(state, required, "state.json")
    schema_version = state["schema_version"]
    if schema_version not in SUPPORTED_SCHEMA_VERSIONS:
        raise ValidationError("unsupported state schema_version")
    validate_slug(require_text(state["loop_id"], "state.loop_id"))
    status = require_text(state["status"], "state.status")
    if status not in LOOP_STATES:
        raise ValidationError("invalid loop status: {}".format(status))

    contract = require_dict(state["contract"], "state.contract")
    reject_unknown(
        contract,
        {"version", "sha256", "workflow_sha256", "definition"},
        "state.contract",
    )
    version = contract.get("version")
    if isinstance(version, bool) or not isinstance(version, int) or version < 1:
        raise ValidationError("state.contract.version must be a positive integer")
    definition = normalize_legacy_definition(contract.get("definition"), schema_version)
    if contract.get("sha256") != sha256_bytes(canonical_json(definition)):
        raise ValidationError("state contract SHA-256 does not match its definition")
    if contract.get("workflow_sha256") != sha256_bytes(workflow):
        raise ValidationError("WORKFLOW.md SHA-256 does not match state contract")
    if schema_version == V2_SCHEMA_VERSION:
        expected_workflow = render_v2_workflow(
            legacy_definition_to_spec(definition), state["loop_id"], version
        ).encode("utf-8")
        if workflow != expected_workflow:
            raise ValidationError(
                "WORKFLOW.md content does not match the canonical state contract"
            )

    iteration = require_dict(state["iteration"], "state.iteration")
    reject_unknown(iteration, {"current", "max"}, "state.iteration")
    current = iteration.get("current")
    if isinstance(current, bool) or not isinstance(current, int) or current < 0:
        raise ValidationError("state.iteration.current must be a nonnegative integer")
    expected_max = definition["limits"]["max_iterations"]
    if iteration.get("max") != expected_max:
        raise ValidationError("state.iteration.max does not match the contract")
    if expected_max is not None and current > expected_max:
        raise ValidationError("state iteration exceeds max_iterations")

    usage = require_dict(state["usage"], "state.usage")
    reject_unknown(usage, {"elapsed_minutes", "cost"}, "state.usage")
    for key in ("elapsed_minutes", "cost"):
        value = usage.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
            raise ValidationError("state.usage.{} must be nonnegative".format(key))
    max_minutes = definition["limits"]["max_minutes"]
    if max_minutes is not None and usage["elapsed_minutes"] > max_minutes:
        raise ValidationError("state elapsed time exceeds max_minutes")
    max_cost = definition["limits"]["max_cost"]
    if max_cost is not None and usage["cost"] > max_cost:
        raise ValidationError("state cost exceeds max_cost")

    tasks = validate_state_tasks(state.get("tasks"))
    if (
        schema_version == V2_SCHEMA_VERSION
        and status == "ready"
        and current == 0
        and state["started_at"] is None
    ):
        expected_tasks = [
            {
                **task,
                "status": "pending",
                "evidence": [],
            }
            for task in definition["initial_tasks"]
        ]
        if tasks != expected_tasks:
            raise ValidationError(
                "ready schema v2 tasks do not match the immutable initial task blueprint"
            )
    ids = {task["id"] for task in tasks}
    active = require_string_list(
        state["active_task_ids"], "state.active_task_ids", allow_empty=True
    )
    if len(active) != len(set(active)):
        raise ValidationError("state.active_task_ids contains duplicates")
    if any(task_id not in ids for task_id in active):
        raise ValidationError("state.active_task_ids contains an unknown task")
    active_by_status = {
        task["id"]
        for task in tasks
        if task["status"] in {"in_progress", "awaiting_evaluation"}
    }
    if set(active) != active_by_status:
        raise ValidationError("active_task_ids does not match active task statuses")
    if definition["execution_mode"] == "sequential" and len(active) > 1:
        raise ValidationError("sequential workflows may have at most one active task")
    if status == "ready" and active:
        raise ValidationError("ready workflows cannot have active tasks")

    completion_evidence = validate_completion_evidence(
        state["completion_evidence"], definition["done_conditions"]
    )

    pending = state["pending_approval"]
    if status == "waiting_approval":
        pending_obj = require_dict(pending, "state.pending_approval")
        reject_unknown(
            pending_obj,
            {"action", "target", "reason", "rollback", "requested_at"},
            "state.pending_approval",
        )
        for key in ("action", "target", "reason", "rollback", "requested_at"):
            require_text(pending_obj.get(key), "state.pending_approval.{}".format(key))
    elif pending is not None:
        raise ValidationError("pending_approval requires waiting_approval status")
    last_checkpoint = state["last_checkpoint"]
    if last_checkpoint is not None:
        checkpoint = require_dict(last_checkpoint, "state.last_checkpoint")
        reject_unknown(
            checkpoint,
            {"at", "iteration", "summary", "evidence"},
            "state.last_checkpoint",
        )
        require_text(checkpoint.get("at"), "state.last_checkpoint.at")
        checkpoint_iteration = checkpoint.get("iteration")
        if (
            isinstance(checkpoint_iteration, bool)
            or not isinstance(checkpoint_iteration, int)
            or checkpoint_iteration < 0
            or checkpoint_iteration > current
        ):
            raise ValidationError("state.last_checkpoint.iteration is invalid")
        require_text(checkpoint.get("summary"), "state.last_checkpoint.summary")
        require_string_list(
            checkpoint.get("evidence"), "state.last_checkpoint.evidence"
        )

    if state["started_at"] is not None:
        require_text(state["started_at"], "state.started_at")
    require_text(state["updated_at"], "state.updated_at")

    if status == "completed":
        passed_conditions = {
            entry["condition"]
            for entry in completion_evidence
            if entry["result"] == "pass"
        }
        if (
            active
            or any(task["status"] != "completed" for task in tasks)
            or passed_conditions != set(definition["done_conditions"])
        ):
            raise ValidationError("completed workflow contains unfinished tasks")


def validate_completion_evidence(
    value: Any, done_conditions: List[str]
) -> List[Dict[str, Any]]:
    if not isinstance(value, list):
        raise ValidationError("state.completion_evidence must be an array")
    allowed = {"condition", "result", "evidence", "evaluator", "evaluated_at"}
    conditions = set(done_conditions)
    seen: Set[str] = set()
    result: List[Dict[str, Any]] = []
    for index, raw_entry in enumerate(value):
        name = "state.completion_evidence[{}]".format(index)
        entry = require_dict(raw_entry, name)
        reject_unknown(entry, allowed, name)
        condition = require_text(entry.get("condition"), "{}.condition".format(name))
        if condition not in conditions:
            raise ValidationError("completion evidence references an unknown condition")
        if condition in seen:
            raise ValidationError("completion evidence contains duplicate conditions")
        seen.add(condition)
        evaluation_result = require_text(entry.get("result"), "{}.result".format(name))
        if evaluation_result not in {"pass", "fail"}:
            raise ValidationError("completion evidence result must be pass or fail")
        result.append(
            {
                "condition": condition,
                "result": evaluation_result,
                "evidence": require_string_list(
                    entry.get("evidence"), "{}.evidence".format(name)
                ),
                "evaluator": require_text(
                    entry.get("evaluator"), "{}.evaluator".format(name)
                ),
                "evaluated_at": require_text(
                    entry.get("evaluated_at"), "{}.evaluated_at".format(name)
                ),
            }
        )
    return result


def normalize_legacy_definition(value: Any, schema_version: str) -> Dict[str, Any]:
    definition = require_dict(value, "state.contract.definition")
    base_allowed = {
        "language",
        "domain",
        "execution_mode",
        "goal",
        "audience",
        "inputs",
        "invariants",
        "done_conditions",
        "verification",
        "authority",
        "limits",
        "checkpoint",
        "stop_conditions",
    }
    v2_allowed = base_allowed | {
        "title",
        "template",
        "input_schema",
        "input_bindings",
        "input_bindings_sha256",
        "initial_tasks",
    }
    allowed = v2_allowed if schema_version == V2_SCHEMA_VERSION else base_allowed
    reject_unknown(definition, allowed, "state.contract.definition")
    domain = require_text(definition.get("domain"), "contract.domain")
    if domain not in DOMAINS:
        raise ValidationError("invalid contract domain")
    execution_mode = require_text(
        definition.get("execution_mode"), "contract.execution_mode"
    )
    if execution_mode not in EXECUTION_MODES:
        raise ValidationError("invalid contract execution_mode")
    normalized = {
        "language": require_text(definition.get("language"), "contract.language"),
        "domain": domain,
        "execution_mode": execution_mode,
        "goal": require_text(definition.get("goal"), "contract.goal"),
        "audience": require_text(definition.get("audience"), "contract.audience"),
        "inputs": require_string_list(definition.get("inputs"), "contract.inputs"),
        "invariants": require_string_list(
            definition.get("invariants"), "contract.invariants", allow_empty=True
        ),
        "done_conditions": require_string_list(
            definition.get("done_conditions"), "contract.done_conditions"
        ),
        "verification": require_string_list(
            definition.get("verification"), "contract.verification"
        ),
        "authority": normalize_authority(definition.get("authority")),
        "limits": normalize_limits(definition.get("limits")),
        "checkpoint": normalize_checkpoint(definition.get("checkpoint")),
        "stop_conditions": require_string_list(
            definition.get("stop_conditions"), "contract.stop_conditions"
        ),
    }
    if schema_version == V2_SCHEMA_VERSION:
        if definition.get("template") is None:
            raise ValidationError("contract.template is required for schema v2")
        input_schema = normalize_input_schema(definition.get("input_schema"))
        input_bindings = normalize_input_bindings(
            definition.get("input_bindings"), input_schema
        )
        bindings_sha256 = require_text(
            definition.get("input_bindings_sha256"),
            "contract.input_bindings_sha256",
        )
        if bindings_sha256 != sha256_bytes(canonical_json(input_bindings)):
            raise ValidationError(
                "contract input_bindings SHA-256 does not match its bindings"
            )
        normalized = {
            "title": require_text(definition.get("title"), "contract.title"),
            "template": normalize_template(definition.get("template"), "unused"),
            **normalized,
            "input_schema": input_schema,
            "input_bindings": input_bindings,
            "input_bindings_sha256": bindings_sha256,
            "initial_tasks": normalize_tasks(definition.get("initial_tasks")),
        }
    return normalized


def legacy_definition_to_spec(definition: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "schema_version": V2_SCHEMA_VERSION,
        "title": definition["title"],
        "template": definition["template"],
        "language": definition["language"],
        "domain": definition["domain"],
        "execution_mode": definition["execution_mode"],
        "goal": definition["goal"],
        "audience": definition["audience"],
        "inputs": definition["inputs"],
        "input_schema": definition["input_schema"],
        "input_bindings": definition["input_bindings"],
        "input_bindings_sha256": definition["input_bindings_sha256"],
        "invariants": definition["invariants"],
        "done_conditions": definition["done_conditions"],
        "tasks": definition["initial_tasks"],
        "verification": definition["verification"],
        "authority": definition["authority"],
        "limits": definition["limits"],
        "checkpoint": definition["checkpoint"],
        "stop_conditions": definition["stop_conditions"],
    }


def validate_state_tasks(value: Any) -> List[Dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise ValidationError("state.tasks must contain at least one task")
    allowed = {
        "id",
        "title",
        "description",
        "status",
        "dependencies",
        "acceptance_criteria",
        "evidence",
    }
    tasks: List[Dict[str, Any]] = []
    ids: Set[str] = set()
    for index, raw_task in enumerate(value):
        name = "state.tasks[{}]".format(index)
        task = require_dict(raw_task, name)
        reject_unknown(task, allowed, name)
        task_id = require_text(task.get("id"), "{}.id".format(name))
        if task_id in ids:
            raise ValidationError("duplicate state task id: {}".format(task_id))
        ids.add(task_id)
        task_status = require_text(task.get("status"), "{}.status".format(name))
        if task_status not in TASK_STATES:
            raise ValidationError("invalid task status: {}".format(task_status))
        tasks.append(
            {
                "id": task_id,
                "title": require_text(task.get("title"), "{}.title".format(name)),
                "description": require_text(
                    task.get("description"), "{}.description".format(name)
                ),
                "status": task_status,
                "dependencies": require_string_list(
                    task.get("dependencies"),
                    "{}.dependencies".format(name),
                    allow_empty=True,
                ),
                "acceptance_criteria": require_string_list(
                    task.get("acceptance_criteria"),
                    "{}.acceptance_criteria".format(name),
                ),
                "evidence": require_string_list(
                    task.get("evidence"), "{}.evidence".format(name), allow_empty=True
                ),
            }
        )
        if task_status == "completed" and not tasks[-1]["evidence"]:
            raise ValidationError("completed task {} has no evidence".format(task_id))
    for task in tasks:
        for dependency in task["dependencies"]:
            if dependency not in ids:
                raise ValidationError(
                    "state task {} depends on unknown task {}".format(
                        task["id"], dependency
                    )
                )
            if dependency == task["id"]:
                raise ValidationError("state task {} depends on itself".format(task["id"]))
    ensure_acyclic(tasks)
    return tasks


def normalize_v3_definition(value: Any) -> Dict[str, Any]:
    definition = require_dict(value, "state.contract.definition")
    allowed = {
        "title",
        "template",
        "language",
        "domain",
        "execution_mode",
        "goal",
        "audience",
        "inputs",
        "input_schema",
        "input_bindings",
        "input_bindings_sha256",
        "invariants",
        "conditions",
        "evidence_requirements",
        "initial_graph",
        "authority",
        "limits",
        "checkpoint",
        "circuit_breakers",
        "memory_policy",
        "context_policy",
    }
    reject_unknown(definition, allowed, "state.contract.definition")
    missing = sorted(allowed - set(definition))
    if missing:
        raise ValidationError(
            "state.contract.definition missing field(s): {}".format(", ".join(missing))
        )
    raw = dict(definition)
    claimed_bindings_hash = require_text(
        raw.pop("input_bindings_sha256"), "contract.input_bindings_sha256"
    )
    raw["schema_version"] = CURRENT_SCHEMA_VERSION
    spec = normalize_v3_spec(raw, "unused")
    if claimed_bindings_hash != spec["input_bindings_sha256"]:
        raise ValidationError("contract input_bindings SHA-256 does not match its bindings")
    return immutable_v3_definition(spec)


def validate_node_outputs(value: Any, definition: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not isinstance(value, list):
        raise ValidationError("state.node_outputs must be an array")
    ports = {
        (node["id"], port["id"])
        for node in definition["initial_graph"]["nodes"]
        for port in node["output_ports"]
    }
    result: List[Dict[str, Any]] = []
    seen: Set[Any] = set()
    for index, raw in enumerate(value):
        name = "state.node_outputs[{}]".format(index)
        item = require_dict(raw, name)
        allowed = {
            "node_id",
            "port_id",
            "uri",
            "digest",
            "evidence_refs",
            "summary",
            "produced_at",
        }
        reject_unknown(item, allowed, name)
        node_id = require_stable_id(item.get("node_id"), "{}.node_id".format(name))
        port_id = require_stable_id(item.get("port_id"), "{}.port_id".format(name))
        key = (node_id, port_id)
        if key not in ports or key in seen:
            raise ValidationError("{} references duplicate or unknown output port".format(name))
        seen.add(key)
        digest = require_text(item.get("digest"), "{}.digest".format(name))
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValidationError("{}.digest must be a lowercase SHA-256".format(name))
        result.append(
            {
                "node_id": node_id,
                "port_id": port_id,
                "uri": require_text(item.get("uri"), "{}.uri".format(name)),
                "digest": digest,
                "evidence_refs": require_string_list(
                    item.get("evidence_refs"), "{}.evidence_refs".format(name), allow_empty=True
                ),
                "summary": require_text(item.get("summary"), "{}.summary".format(name)),
                "produced_at": require_text(
                    item.get("produced_at"), "{}.produced_at".format(name)
                ),
            }
        )
    return result


def validate_condition_coverage(value: Any, definition: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not isinstance(value, list):
        raise ValidationError("state.condition_coverage must be an array")
    expected = {
        condition["id"]: condition["evidence_requirement_ids"]
        for condition in definition["conditions"]
    }
    result: List[Dict[str, Any]] = []
    seen: Set[str] = set()
    for index, raw in enumerate(value):
        name = "state.condition_coverage[{}]".format(index)
        item = require_dict(raw, name)
        reject_unknown(item, {"condition_id", "requirement_results"}, name)
        condition_id = require_stable_id(
            item.get("condition_id"), "{}.condition_id".format(name)
        )
        if condition_id in seen or condition_id not in expected:
            raise ValidationError("condition_coverage contains duplicate or unknown condition")
        seen.add(condition_id)
        raw_results = item.get("requirement_results")
        if not isinstance(raw_results, list):
            raise ValidationError("{}.requirement_results must be an array".format(name))
        requirement_results: List[Dict[str, Any]] = []
        requirement_ids: Set[str] = set()
        for result_index, raw_result in enumerate(raw_results):
            result_name = "{}.requirement_results[{}]".format(name, result_index)
            entry = require_dict(raw_result, result_name)
            reject_unknown(entry, {"requirement_id", "result", "evidence"}, result_name)
            requirement_id = require_stable_id(
                entry.get("requirement_id"), "{}.requirement_id".format(result_name)
            )
            if requirement_id in requirement_ids:
                raise ValidationError("{} has duplicate requirement results".format(name))
            requirement_ids.add(requirement_id)
            result_value = require_text(entry.get("result"), "{}.result".format(result_name))
            if result_value not in {"pending", "pass", "fail"}:
                raise ValidationError("{}.result is invalid".format(result_name))
            evidence = require_string_list(
                entry.get("evidence"), "{}.evidence".format(result_name), allow_empty=True
            )
            if result_value == "pass" and not evidence:
                raise ValidationError("passing requirement result must include evidence")
            requirement_results.append(
                {"requirement_id": requirement_id, "result": result_value, "evidence": evidence}
            )
        if requirement_ids != set(expected[condition_id]):
            raise ValidationError("{} does not exactly cover its condition requirements".format(name))
        result.append(
            {"condition_id": condition_id, "requirement_results": requirement_results}
        )
    if seen != set(expected):
        raise ValidationError("condition_coverage does not cover every condition")
    return result


def validate_v3_state(
    state: Dict[str, Any], workflow: bytes, progress: bytes, handoff: bytes
) -> None:
    required = {
        "schema_version",
        "loop_id",
        "status",
        "contract",
        "iteration",
        "usage",
        "active_task_ids",
        "tasks",
        "completion_evidence",
        "node_outputs",
        "condition_coverage",
        "breaker_counters",
        "memory_index_head",
        "progress_hash_chain",
        "handoff_sha256",
        "pending_approval",
        "last_checkpoint",
        "started_at",
        "updated_at",
    }
    reject_unknown(state, required, "state.json")
    missing = sorted(required - set(state))
    if missing:
        raise ValidationError("state.json missing field(s): {}".format(", ".join(missing)))
    if state["schema_version"] != CURRENT_SCHEMA_VERSION:
        raise ValidationError("v3 validator received a non-v3 state")
    loop_id = validate_slug(require_text(state["loop_id"], "state.loop_id"))
    status = require_text(state["status"], "state.status")
    if status not in LOOP_STATES:
        raise ValidationError("invalid loop status: {}".format(status))
    contract = require_dict(state["contract"], "state.contract")
    reject_unknown(contract, {"version", "sha256", "workflow_sha256", "definition"}, "state.contract")
    contract_version = require_positive_integer(contract.get("version"), "state.contract.version")
    definition = normalize_v3_definition(contract.get("definition"))
    if contract.get("sha256") != sha256_bytes(canonical_json(definition)):
        raise ValidationError("state contract SHA-256 does not match its definition")
    if contract.get("workflow_sha256") != sha256_bytes(workflow):
        raise ValidationError("WORKFLOW.md SHA-256 does not match state contract")
    expected_workflow = render_v3_workflow(
        {"schema_version": CURRENT_SCHEMA_VERSION, **definition}, loop_id, contract_version
    ).encode("utf-8")
    if workflow != expected_workflow:
        raise ValidationError("WORKFLOW.md content does not match canonical v3 contract")

    iteration = require_dict(state["iteration"], "state.iteration")
    reject_unknown(iteration, {"current", "max"}, "state.iteration")
    current = iteration.get("current")
    if isinstance(current, bool) or not isinstance(current, int) or current < 0:
        raise ValidationError("state.iteration.current must be a nonnegative integer")
    if iteration.get("max") != definition["limits"]["max_iterations"]:
        raise ValidationError("state.iteration.max does not match the contract")
    if iteration["max"] is not None and current > iteration["max"]:
        raise ValidationError("state iteration exceeds max_iterations")
    usage = require_dict(state["usage"], "state.usage")
    reject_unknown(usage, {"elapsed_minutes", "cost", "total_tokens"}, "state.usage")
    for key in ("elapsed_minutes", "cost", "total_tokens"):
        item = usage.get(key)
        if isinstance(item, bool) or not isinstance(item, (int, float)) or item < 0:
            raise ValidationError("state.usage.{} must be nonnegative".format(key))
    if (
        definition["limits"]["max_total_tokens"] is not None
        and usage["total_tokens"] > definition["limits"]["max_total_tokens"]
    ):
        raise ValidationError("state token usage exceeds max_total_tokens")
    if definition["limits"]["max_minutes"] is not None and usage["elapsed_minutes"] > definition["limits"]["max_minutes"]:
        raise ValidationError("state elapsed time exceeds max_minutes")
    if definition["limits"]["max_cost"] is not None and usage["cost"] > definition["limits"]["max_cost"]:
        raise ValidationError("state cost exceeds max_cost")

    tasks = validate_state_tasks(state["tasks"])
    dependencies: Dict[str, List[str]] = {
        node["id"]: [] for node in definition["initial_graph"]["nodes"]
    }
    for edge in definition["initial_graph"]["edges"]:
        dependency = edge["from"]["node_id"]
        target = edge["to"]["node_id"]
        if dependency not in dependencies[target]:
            dependencies[target].append(dependency)
    expected_tasks = [
        {
            "id": node["id"],
            "title": node["title"],
            "description": node["description"],
            "dependencies": dependencies[node["id"]],
            "acceptance_criteria": node["acceptance_criteria"],
        }
        for node in definition["initial_graph"]["nodes"]
    ]
    actual_tasks = [
        {key: task[key] for key in ("id", "title", "description", "dependencies", "acceptance_criteria")}
        for task in tasks
    ]
    if actual_tasks != expected_tasks:
        raise ValidationError("schema v3 tasks do not match the immutable initial graph")
    active = require_string_list(state["active_task_ids"], "state.active_task_ids", allow_empty=True)
    if len(active) != len(set(active)):
        raise ValidationError("state.active_task_ids contains duplicates")
    active_by_status = {task["id"] for task in tasks if task["status"] in {"in_progress", "awaiting_evaluation"}}
    if set(active) != active_by_status:
        raise ValidationError("active_task_ids does not match active task statuses")
    if definition["execution_mode"] == "sequential" and len(active) > 1:
        raise ValidationError("sequential workflows may have at most one active task")
    if status == "ready" and active:
        raise ValidationError("ready workflows cannot have active tasks")
    outputs = validate_node_outputs(state["node_outputs"], definition)
    output_keys = {(item["node_id"], item["port_id"]) for item in outputs}
    incoming = {
        (edge["to"]["node_id"], edge["to"]["port_id"]): (
            edge["from"]["node_id"],
            edge["from"]["port_id"],
        )
        for edge in definition["initial_graph"]["edges"]
    }
    contract_nodes = {node["id"]: node for node in definition["initial_graph"]["nodes"]}
    for task in tasks:
        node = contract_nodes[task["id"]]
        if task["status"] not in {"in_progress", "awaiting_evaluation", "completed"}:
            continue
        for port in node["input_ports"]:
            if port["required"] and incoming[(node["id"], port["id"])] not in output_keys:
                raise ValidationError(
                    "node {} cannot run without a digested upstream output for {}".format(
                        node["id"], port["id"]
                    )
                )
        if task["status"] == "completed":
            for port in node["output_ports"]:
                if (node["id"], port["id"]) not in output_keys:
                    raise ValidationError(
                        "completed graph node {} is missing output {}".format(
                            node["id"], port["id"]
                        )
                    )
    active_resources: Set[str] = set()
    for task_id in active:
        for resource_key in contract_nodes[task_id]["resource_keys"]:
            if resource_key in active_resources:
                raise ValidationError(
                    "parallel active graph nodes share resource key {}".format(resource_key)
                )
            active_resources.add(resource_key)
    coverage = validate_condition_coverage(state["condition_coverage"], definition)
    completion_evidence = validate_completion_evidence(
        state["completion_evidence"], [condition["id"] for condition in definition["conditions"]]
    )

    counters = require_dict(state["breaker_counters"], "state.breaker_counters")
    breaker_ids = {item["id"] for item in definition["circuit_breakers"]}
    reject_unknown(counters, breaker_ids, "state.breaker_counters")
    if set(counters) != breaker_ids:
        raise ValidationError("breaker_counters must cover every circuit breaker")
    for breaker_id, count in counters.items():
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            raise ValidationError("breaker counter {} must be nonnegative".format(breaker_id))
    if state["memory_index_head"] is not None:
        require_text(state["memory_index_head"], "state.memory_index_head")
    chain = require_dict(state["progress_hash_chain"], "state.progress_hash_chain")
    reject_unknown(chain, {"head_sha256", "entries"}, "state.progress_hash_chain")
    head = chain.get("head_sha256")
    if head is not None and not re.fullmatch(r"[0-9a-f]{64}", require_text(head, "progress_hash_chain.head_sha256")):
        raise ValidationError("progress_hash_chain.head_sha256 must be a lowercase SHA-256 or null")
    entries = chain.get("entries")
    if isinstance(entries, bool) or not isinstance(entries, int) or entries < 0:
        raise ValidationError("progress_hash_chain.entries must be nonnegative")
    if entries == 0 and head is not None:
        raise ValidationError("an empty progress hash chain must have a null head")
    if entries > 0 and head is None:
        raise ValidationError("a nonempty progress hash chain must have a SHA-256 head")
    if (
        entries == 1
        and contract_version == 1
        and current == 0
        and head != progress_chain_next(None, progress.decode("utf-8"))
    ):
        raise ValidationError("initial progress.md does not match progress_hash_chain head")
    handoff_hash = require_text(state["handoff_sha256"], "state.handoff_sha256")
    if not re.fullmatch(r"[0-9a-f]{64}", handoff_hash) or handoff_hash != sha256_bytes(handoff):
        raise ValidationError("handoff.md SHA-256 does not match state")

    pending = state["pending_approval"]
    if pending is not None:
        pending_obj = require_dict(pending, "state.pending_approval")
        reject_unknown(
            pending_obj,
            {"action", "target", "reason", "rollback", "requested_at"},
            "state.pending_approval",
        )
        for key in ("action", "target", "reason", "rollback", "requested_at"):
            require_text(pending_obj.get(key), "state.pending_approval.{}".format(key))
    if status == "waiting_approval" and pending is None:
        raise ValidationError("waiting_approval requires pending_approval")
    if status != "waiting_approval" and pending is not None:
        raise ValidationError("pending_approval requires waiting_approval status")
    if state["last_checkpoint"] is not None:
        checkpoint = require_dict(state["last_checkpoint"], "state.last_checkpoint")
        reject_unknown(
            checkpoint,
            {"at", "iteration", "summary", "evidence"},
            "state.last_checkpoint",
        )
        require_text(checkpoint.get("at"), "state.last_checkpoint.at")
        checkpoint_iteration = checkpoint.get("iteration")
        if (
            isinstance(checkpoint_iteration, bool)
            or not isinstance(checkpoint_iteration, int)
            or checkpoint_iteration < 0
            or checkpoint_iteration > current
        ):
            raise ValidationError("state.last_checkpoint.iteration is invalid")
        require_text(checkpoint.get("summary"), "state.last_checkpoint.summary")
        require_string_list(
            checkpoint.get("evidence"), "state.last_checkpoint.evidence", allow_empty=True
        )
    if state["started_at"] is not None:
        require_text(state["started_at"], "state.started_at")
    require_text(state["updated_at"], "state.updated_at")

    if status == "completed":
        if active or pending is not None:
            raise ValidationError("completed workflow cannot have active or pending work")
        if any(task["status"] != "completed" for task in tasks):
            raise ValidationError("completed workflow contains unfinished tasks")
        if any(
            result["result"] != "pass"
            for condition in coverage
            for result in condition["requirement_results"]
        ):
            raise ValidationError("completed workflow lacks passing condition evidence")


def validate_state(
    state: Dict[str, Any], workflow: bytes, progress: bytes, handoff: bytes
) -> None:
    schema_version = state.get("schema_version")
    if schema_version == CURRENT_SCHEMA_VERSION:
        validate_v3_state(state, workflow, progress, handoff)
        return
    if schema_version not in {"1.0", V2_SCHEMA_VERSION}:
        raise ValidationError("unsupported state schema_version")
    validate_legacy_state(state, workflow)


def validate_package(path: Path) -> None:
    if not path.is_dir():
        raise ValidationError("loop path is not a directory: {}".format(path))
    missing = sorted(name for name in REQUIRED_FILES if not (path / name).is_file())
    if missing:
        raise ValidationError("loop package missing file(s): {}".format(", ".join(missing)))
    try:
        workflow = (path / "WORKFLOW.md").read_bytes()
        progress_bytes = (path / "progress.md").read_bytes()
        handoff_bytes = (path / "handoff.md").read_bytes()
        progress = progress_bytes.decode("utf-8")
        handoff = handoff_bytes.decode("utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise ValidationError("cannot read loop package: {}".format(exc))
    if not workflow.strip():
        raise ValidationError("WORKFLOW.md is empty")
    if not progress.startswith("# Progress Ledger"):
        raise ValidationError("progress.md must start with '# Progress Ledger'")
    if not handoff.startswith("# Loop Handoff"):
        raise ValidationError("handoff.md must start with '# Loop Handoff'")
    state = load_state(path / "state.json")
    validate_state(state, workflow, progress_bytes, handoff_bytes)
    recommendation_path = path / RECOMMENDATION_FILE
    if recommendation_path.exists():
        if state.get("schema_version") != CURRENT_SCHEMA_VERSION:
            raise ValidationError("runtime recommendation requires a schema v3 package")
        try:
            recommendation = json.loads(recommendation_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValidationError("cannot read runtime recommendation: {}".format(exc))
        validate_runtime_recommendation(recommendation, state)


def remove_empty_parents(loops_root: Path, workspace: Path) -> None:
    candidates = [loops_root, loops_root.parent]
    for candidate in candidates:
        if candidate == workspace or not candidate.exists():
            continue
        try:
            candidate.rmdir()
        except OSError:
            break


def is_within(candidate: Path, root: Path) -> bool:
    try:
        return os.path.commonpath([str(candidate), str(root)]) == str(root)
    except ValueError:
        return False


def rename_no_replace(source: Path, target: Path) -> None:
    """Atomically rename a directory without replacing an existing target."""
    libc = ctypes.CDLL(None, use_errno=True)
    source_bytes = os.fsencode(str(source))
    target_bytes = os.fsencode(str(target))
    result: Optional[int] = None

    if sys.platform == "darwin" and hasattr(libc, "renamex_np"):
        renamex_np = libc.renamex_np
        renamex_np.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint]
        renamex_np.restype = ctypes.c_int
        result = renamex_np(source_bytes, target_bytes, 0x00000004)
    elif sys.platform.startswith("linux") and hasattr(libc, "renameat2"):
        renameat2 = libc.renameat2
        renameat2.argtypes = [
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_uint,
        ]
        renameat2.restype = ctypes.c_int
        result = renameat2(-100, source_bytes, -100, target_bytes, 0x00000001)

    if result is not None:
        if result == 0:
            return
        error_number = ctypes.get_errno()
        if error_number in {errno.EEXIST, errno.ENOTEMPTY}:
            raise ValidationError("target loop already exists: {}".format(target))
        raise OSError(error_number, os.strerror(error_number), str(target))

    # Conservative fallback for platforms without an exclusive rename primitive.
    # It preserves no-overwrite behavior and removes partial output on failure,
    # though the final directory is not atomically visible during this fallback.
    try:
        target.mkdir()
    except FileExistsError:
        raise ValidationError("target loop already exists: {}".format(target))
    try:
        for child in source.iterdir():
            os.rename(str(child), str(target / child.name))
        source.rmdir()
    except Exception:
        shutil.rmtree(str(target))
        raise


def create_package(workspace: Path, slug: str, raw_spec: Any) -> Path:
    workspace = workspace.resolve()
    if not workspace.is_dir():
        raise ValidationError("workspace is not a directory: {}".format(workspace))
    slug = validate_slug(slug)
    spec = normalize_create_spec(raw_spec, slug)
    loops_root = workspace / ".agent" / "loops"
    resolved_loops_root = loops_root.resolve()
    if not is_within(resolved_loops_root, workspace):
        raise ValidationError(".agent/loops resolves outside the workspace")
    target = loops_root / slug
    if target.exists():
        raise ValidationError("target loop already exists: {}".format(target))

    created_loops_root = not loops_root.exists()
    loops_root.mkdir(parents=True, exist_ok=True)
    temporary: Optional[Path] = None
    try:
        temporary = Path(tempfile.mkdtemp(prefix=".{}-tmp-".format(slug), dir=str(loops_root)))
        now = utc_now()
        workflow = render_workflow(spec, slug)
        progress = render_progress(slug, now, spec["language"])
        handoff = render_handoff(spec, slug, now)
        state = (
            build_v3_state(spec, slug, workflow, progress, handoff, now)
            if spec["schema_version"] == CURRENT_SCHEMA_VERSION
            else build_v2_state(spec, slug, workflow, now)
        )
        write_text(temporary / "WORKFLOW.md", workflow)
        write_text(
            temporary / "state.json",
            json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        )
        write_text(temporary / "progress.md", progress)
        write_text(temporary / "handoff.md", handoff)
        if spec["schema_version"] == CURRENT_SCHEMA_VERSION:
            recommendation = build_runtime_recommendation(
                spec,
                slug,
                state["contract"]["sha256"],
                spec.get("runtime_recommendation"),
            )
            write_text(
                temporary / RECOMMENDATION_FILE,
                json.dumps(recommendation, ensure_ascii=False, indent=2) + "\n",
            )
        validate_package(temporary)
        rename_no_replace(temporary, target)
        temporary = None
        return target
    except Exception:
        if temporary is not None and temporary.exists():
            shutil.rmtree(str(temporary))
        if created_loops_root:
            remove_empty_parents(loops_root, workspace)
        raise


def instantiate_package(
    template_path: Path, workspace: Path, slug: str, raw_instance: Any
) -> Path:
    template_path = template_path.resolve()
    validate_package(template_path)
    template_state = load_state(template_path / "state.json")
    schema_version = template_state.get("schema_version")
    if schema_version not in {V2_SCHEMA_VERSION, CURRENT_SCHEMA_VERSION}:
        raise ValidationError("instantiate requires a schema v2 or v3 workflow package")
    raw_definition = require_dict(template_state.get("contract"), "state.contract").get(
        "definition"
    )
    definition = (
        normalize_v3_definition(raw_definition)
        if schema_version == CURRENT_SCHEMA_VERSION
        else normalize_legacy_definition(raw_definition, V2_SCHEMA_VERSION)
    )
    instance = require_dict(raw_instance, "instance specification")
    reject_unknown(
        instance,
        {"input_bindings", "title", "runtime_recommendation"},
        "instance specification",
    )
    input_bindings = normalize_input_bindings(
        instance.get("input_bindings"), definition["input_schema"]
    )
    raw_spec = (
        {"schema_version": CURRENT_SCHEMA_VERSION, **definition}
        if schema_version == CURRENT_SCHEMA_VERSION
        else legacy_definition_to_spec(definition)
    )
    raw_spec["input_bindings"] = input_bindings
    raw_spec.pop("input_bindings_sha256", None)
    if schema_version == V2_SCHEMA_VERSION:
        raw_spec["schema_version"] = V2_SCHEMA_VERSION
    if "title" in instance:
        raw_spec["title"] = require_text(instance["title"], "instance.title")
    if schema_version == CURRENT_SCHEMA_VERSION:
        if "runtime_recommendation" in instance:
            raw_spec["runtime_recommendation"] = instance["runtime_recommendation"]
        else:
            # Repository-derived provenance and scopes belong to the new
            # binding. Never copy a source instance recommendation silently;
            # the Skill supplies a freshly inferred override when available.
            raw_spec["runtime_recommendation"] = None
    return create_package(workspace, slug, raw_spec)


def slugify_stable(prefix: str, index: int) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", prefix.lower()).strip("-")
    if not cleaned or not cleaned[0].isalpha():
        cleaned = "item-{}".format(cleaned) if cleaned else "item"
    cleaned = cleaned[:48].rstrip("-")
    return "{}-{:02d}".format(cleaned, index)


def migration_plan(source_path: Path) -> Dict[str, Any]:
    source_path = source_path.resolve()
    validate_package(source_path)
    state = load_state(source_path / "state.json")
    schema_version = state.get("schema_version")
    if schema_version not in {"1.0", V2_SCHEMA_VERSION}:
        raise ValidationError("migrate-plan requires a schema v1 or v2 source package")
    contract = require_dict(state.get("contract"), "state.contract")
    definition = normalize_legacy_definition(contract.get("definition"), schema_version)
    raw_conditions = definition["done_conditions"]
    conditions = [
        {
            "id": slugify_stable("condition", index),
            "description": description,
            "evidence_requirement_ids": [],
        }
        for index, description in enumerate(raw_conditions, 1)
    ]
    raw_tasks = (
        definition["initial_tasks"]
        if schema_version == V2_SCHEMA_VERSION
        else validate_state_tasks(state.get("tasks"))
    )
    graph_nodes = []
    graph_edges = []
    task_ids = {task["id"] for task in raw_tasks}
    node_id_map: Dict[str, str] = {}
    used_node_ids: Set[str] = set()
    for index, task in enumerate(raw_tasks, 1):
        candidate = (
            task["id"]
            if len(task["id"]) <= 64 and STABLE_ID_RE.fullmatch(task["id"])
            else slugify_stable("node", index)
        )
        if candidate in used_node_ids:
            candidate = slugify_stable("migrated-node", index)
        used_node_ids.add(candidate)
        node_id_map[task["id"]] = candidate
    for task_index, task in enumerate(raw_tasks, 1):
        dependencies = [dep for dep in task["dependencies"] if dep in task_ids]
        node_id = node_id_map[task["id"]]
        graph_nodes.append(
            {
                "id": node_id,
                "title": task["title"],
                "description": task["description"],
                "input_ports": [
                    {
                        "id": "input-{:02d}".format(dependency_index),
                        "type": "artifact",
                        "description": "Validated output from {}".format(dependency),
                        "required": True,
                    }
                    for dependency_index, dependency in enumerate(dependencies, 1)
                ],
                "output_ports": [
                    {
                        "id": "result",
                        "type": "artifact",
                        "description": "Validated result for this node",
                    }
                ],
                "acceptance_criteria": task["acceptance_criteria"],
                "resource_keys": [],
                "max_attempts": 2,
                "no_progress_limit": 2,
            }
        )
        for dependency_index, dependency in enumerate(dependencies, 1):
            graph_edges.append(
                {
                    "id": "edge-{:02d}-{:02d}".format(task_index, dependency_index),
                    "from": {"node_id": node_id_map[dependency], "port_id": "result"},
                    "to": {"node_id": node_id, "port_id": "input-{:02d}".format(dependency_index)},
                }
            )
    authority = definition["authority"]
    authority_rules = []
    for effect, key in (("allow", "auto_allowed"), ("approve", "approval_required"), ("deny", "forbidden")):
        for index, description in enumerate(authority[key], 1):
            authority_rules.append(
                {
                    "authority_id": slugify_stable(effect, index),
                    "effect": effect,
                    "description": description,
                }
            )
    return {
        "status": "ok",
        "source": str(source_path),
        "source_schema_version": schema_version,
        "source_contract_sha256": contract.get("sha256"),
        "suggestions": {
            "conditions": conditions,
            "initial_graph": {"nodes": graph_nodes, "edges": graph_edges},
            "authority_rules": authority_rules,
        },
        "unresolved": [
            "Infer stable evidence_requirements from repository facts and bind every condition; ask only if deterministic or human evidence remains unavailable.",
            "Infer typed graph ports and resource_keys; use bounded attempt and no-progress defaults unless repository evidence requires a narrower choice.",
            "Translate prose verification into repository-backed Runtime Recommendation verifier bindings.",
            "Translate prose stop rules into observable circuit_breakers with block or fail actions, using safe defaults where evidence is absent.",
            "Compute max_total_tokens and context budgets from the standard formula; apply default checkpoint and memory policies.",
        ],
        "migration_contract": {
            "stdin": {"specification": "a complete confirmed schema 3.0 specification"},
            "source_is_never_modified": True,
            "runtime_history_is_never_copied": True,
        },
    }


def migrate_package(
    source_path: Path, workspace: Path, slug: str, raw_migration: Any
) -> Path:
    source_path = source_path.resolve()
    validate_package(source_path)
    source_state = load_state(source_path / "state.json")
    if source_state.get("schema_version") not in {"1.0", V2_SCHEMA_VERSION}:
        raise ValidationError("migrate requires a schema v1 or v2 source package")
    migration = require_dict(raw_migration, "migration specification")
    reject_unknown(migration, {"specification"}, "migration specification")
    specification = require_dict(migration.get("specification"), "migration.specification")
    if specification.get("schema_version", CURRENT_SCHEMA_VERSION) != CURRENT_SCHEMA_VERSION:
        raise ValidationError("migration specification must target schema 3.0")
    return create_package(workspace, slug, specification)


def render_update_progress_entry(
    progress: str,
    version: int,
    old_contract_sha256: str,
    new_contract_sha256: str,
    approval: Dict[str, str],
    now: str,
) -> str:
    separator = "\n" if progress.endswith("\n") else "\n\n"
    return separator + "## Contract update {}\n\n- Contract version: `{}`\n- Old contract SHA-256: `{}`\n- New contract SHA-256: `{}`\n- Approved by: {}\n- Approved at: {}\n- Rationale: {}\n- Evidence: expected contract SHA-256 matched immediately before transactional replacement.\n".format(
        now,
        version,
        old_contract_sha256,
        new_contract_sha256,
        approval["approved_by"],
        approval["approved_at"],
        approval["rationale"],
    )


def append_update_handoff(
    handoff: str, version: int, goal: str, status: str, now: str
) -> str:
    separator = "\n" if handoff.endswith("\n") else "\n\n"
    return handoff + separator + "## Contract update {}\n\n- Contract version: `{}`\n- Status remains: `{}`\n- Current goal: {}\n- Prior handoff content above is preserved as runtime context.\n".format(
        now, version, status, goal
    )


def update_package(path: Path, raw_update: Any) -> Path:
    path = path.resolve()
    validate_package(path)
    state = load_state(path / "state.json")
    if state.get("schema_version") != CURRENT_SCHEMA_VERSION:
        raise ValidationError("update requires a schema v3 workflow package")
    if state.get("status") not in {"ready", "blocked", "failed"}:
        raise ValidationError("update is allowed only for ready, blocked, or failed workflows")
    if state.get("active_task_ids"):
        raise ValidationError("update requires no active tasks")
    if state.get("pending_approval") is not None:
        raise ValidationError("update requires no pending approval")

    update = require_dict(raw_update, "update specification")
    reject_unknown(
        update,
        {"expected_contract_sha256", "specification", "approval"},
        "update specification",
    )
    expected_hash = require_text(
        update.get("expected_contract_sha256"), "update.expected_contract_sha256"
    )
    current_contract = require_dict(state.get("contract"), "state.contract")
    if expected_hash != current_contract.get("sha256"):
        raise ValidationError("expected contract SHA-256 does not match current state")
    approval_raw = require_dict(update.get("approval"), "update.approval")
    reject_unknown(approval_raw, {"approved_by", "approved_at", "rationale"}, "update.approval")
    approval = {
        key: require_text(approval_raw.get(key), "update.approval.{}".format(key))
        for key in ("approved_by", "approved_at", "rationale")
    }
    specification = require_dict(update.get("specification"), "update.specification")
    new_spec = normalize_v3_spec(specification, state["loop_id"])
    old_definition = normalize_v3_definition(current_contract.get("definition"))
    if new_spec["template"]["id"] != old_definition["template"]["id"]:
        raise ValidationError("update cannot change template.id")
    if new_spec["template"]["version"] < old_definition["template"]["version"]:
        raise ValidationError("update cannot decrease template.version")
    if new_spec["input_bindings"] != old_definition["input_bindings"]:
        raise ValidationError("input binding changes require a fresh instance")
    blueprint_changed = (
        new_spec["input_schema"] != old_definition["input_schema"]
        or new_spec["initial_graph"] != old_definition["initial_graph"]
    )
    if blueprint_changed and new_spec["template"]["version"] <= old_definition["template"]["version"]:
        raise ValidationError("input schema or graph changes require template.version to increase")
    if (
        blueprint_changed
        and (
            state["iteration"]["current"] > 0
            or state["node_outputs"]
            or any(task["evidence"] for task in state["tasks"])
        )
    ):
        raise ValidationError("cannot replace a graph blueprint after runtime evidence exists")
    old_requirements = {
        item["id"]: item for item in old_definition["evidence_requirements"]
    }
    new_requirements = {
        item["id"]: item for item in new_spec["evidence_requirements"]
    }
    new_condition_bindings = {
        item["id"]: set(item["evidence_requirement_ids"])
        for item in new_spec["conditions"]
    }
    for coverage in state["condition_coverage"]:
        for result in coverage["requirement_results"]:
            if result["result"] == "pending" and not result["evidence"]:
                continue
            requirement_id = result["requirement_id"]
            if (
                coverage["condition_id"] not in new_condition_bindings
                or requirement_id not in new_condition_bindings[coverage["condition_id"]]
                or new_requirements.get(requirement_id) != old_requirements.get(requirement_id)
            ):
                raise ValidationError(
                    "update cannot remove or redefine a condition requirement with runtime evidence"
                )

    now = utc_now()
    new_version = current_contract["version"] + 1
    workflow = render_v3_workflow(new_spec, state["loop_id"], new_version)
    definition = immutable_v3_definition(new_spec)
    new_contract_sha256 = sha256_bytes(canonical_json(definition))
    progress_path = path / "progress.md"
    handoff_path = path / "handoff.md"
    old_progress = progress_path.read_text(encoding="utf-8")
    progress_entry = render_update_progress_entry(
        old_progress,
        new_version,
        expected_hash,
        new_contract_sha256,
        approval,
        now,
    )
    new_progress = old_progress + progress_entry
    old_handoff = handoff_path.read_text(encoding="utf-8")
    new_handoff = append_update_handoff(
        old_handoff, new_version, new_spec["goal"], state["status"], now
    )
    if blueprint_changed:
        dependencies: Dict[str, List[str]] = {
            node["id"]: [] for node in new_spec["initial_graph"]["nodes"]
        }
        for edge in new_spec["initial_graph"]["edges"]:
            dependency = edge["from"]["node_id"]
            target = edge["to"]["node_id"]
            if dependency not in dependencies[target]:
                dependencies[target].append(dependency)
        state["tasks"] = [
            {
                "id": node["id"],
                "title": node["title"],
                "description": node["description"],
                "status": "pending",
                "dependencies": dependencies[node["id"]],
                "acceptance_criteria": node["acceptance_criteria"],
                "evidence": [],
            }
            for node in new_spec["initial_graph"]["nodes"]
        ]
        state["node_outputs"] = []
    old_coverage = {
        item["condition_id"]: {
            result["requirement_id"]: result
            for result in item["requirement_results"]
        }
        for item in state["condition_coverage"]
    }
    state["condition_coverage"] = [
        {
            "condition_id": condition["id"],
            "requirement_results": [
                old_coverage.get(condition["id"], {}).get(
                    requirement_id,
                    {"requirement_id": requirement_id, "result": "pending", "evidence": []},
                )
                for requirement_id in condition["evidence_requirement_ids"]
            ],
        }
        for condition in new_spec["conditions"]
    ]
    state["breaker_counters"] = {
        breaker["id"]: state["breaker_counters"].get(breaker["id"], 0)
        for breaker in new_spec["circuit_breakers"]
    }
    state["contract"] = {
        "version": new_version,
        "sha256": new_contract_sha256,
        "workflow_sha256": sha256_bytes(workflow.encode("utf-8")),
        "definition": definition,
    }
    state["iteration"]["max"] = new_spec["limits"]["max_iterations"]
    state["progress_hash_chain"] = {
        "head_sha256": progress_chain_next(
            state["progress_hash_chain"]["head_sha256"], progress_entry
        ),
        "entries": state["progress_hash_chain"]["entries"] + 1,
    }
    state["handoff_sha256"] = sha256_bytes(new_handoff.encode("utf-8"))
    state["updated_at"] = now

    parent = path.parent
    temporary = Path(tempfile.mkdtemp(prefix=".{}-update-".format(path.name), dir=str(parent)))
    backup = Path(tempfile.mkdtemp(prefix=".{}-backup-".format(path.name), dir=str(parent)))
    backup.rmdir()
    installed = False
    try:
        shutil.copytree(str(path), str(temporary), dirs_exist_ok=True)
        write_text(temporary / "WORKFLOW.md", workflow)
        write_text(temporary / "progress.md", new_progress)
        write_text(temporary / "handoff.md", new_handoff)
        write_text(temporary / "state.json", json.dumps(state, ensure_ascii=False, indent=2) + "\n")
        recommendation = build_runtime_recommendation(
            new_spec,
            state["loop_id"],
            new_contract_sha256,
            new_spec.get("runtime_recommendation"),
        )
        write_text(
            temporary / RECOMMENDATION_FILE,
            json.dumps(recommendation, ensure_ascii=False, indent=2) + "\n",
        )
        validate_package(temporary)
        live_state = load_state(path / "state.json")
        if live_state.get("contract", {}).get("sha256") != expected_hash:
            raise ValidationError("contract changed during update; retry with a fresh hash")
        os.replace(str(path), str(backup))
        try:
            os.replace(str(temporary), str(path))
            installed = True
        except Exception:
            os.replace(str(backup), str(path))
            raise
        shutil.rmtree(str(backup))
        validate_package(path)
        return path
    finally:
        if temporary.exists():
            shutil.rmtree(str(temporary))
        if backup.exists() and installed:
            shutil.rmtree(str(backup))


def parse_stdin_json() -> Any:
    try:
        return json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        raise ValidationError("standard input is not valid JSON: {}".format(exc))


def recommendation_result(path: Path) -> Dict[str, Any]:
    recommendation_path = path / RECOMMENDATION_FILE
    if not recommendation_path.is_file():
        return {}
    value = json.loads(recommendation_path.read_text(encoding="utf-8"))
    return {
        "runtime_recommendation": str(recommendation_path),
        "recommendation_status": value.get("status"),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create, instantiate, validate, migrate, or update a durable agent-loop workflow package."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    create = subparsers.add_parser("create", help="create a new package from stdin JSON")
    create.add_argument("--workspace", required=True, type=Path)
    create.add_argument("--slug", required=True)
    instantiate = subparsers.add_parser(
        "instantiate", help="create a fresh schema v2/v3 instance from an existing package"
    )
    instantiate.add_argument("--template", required=True, type=Path)
    instantiate.add_argument("--workspace", required=True, type=Path)
    instantiate.add_argument("--slug", required=True)
    validate = subparsers.add_parser("validate", help="validate an existing package")
    validate.add_argument("--path", required=True, type=Path)
    migrate_plan_parser = subparsers.add_parser(
        "migrate-plan", help="inspect a v1/v2 package and print a non-mutating v3 migration plan"
    )
    migrate_plan_parser.add_argument("--path", required=True, type=Path)
    migrate = subparsers.add_parser(
        "migrate", help="create a fresh v3 package from a confirmed migration specification"
    )
    migrate.add_argument("--source", required=True, type=Path)
    migrate.add_argument("--workspace", required=True, type=Path)
    migrate.add_argument("--slug", required=True)
    update = subparsers.add_parser(
        "update", help="transactionally update an eligible v3 package using contract-hash CAS"
    )
    update.add_argument("--path", required=True, type=Path)
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "create":
            path = create_package(args.workspace, args.slug, parse_stdin_json())
            result = {
                "status": "ok",
                "path": str(path),
                "started": False,
                **recommendation_result(path),
            }
        elif args.command == "instantiate":
            path = instantiate_package(
                args.template, args.workspace, args.slug, parse_stdin_json()
            )
            result = {
                "status": "ok",
                "path": str(path),
                "started": False,
                "instantiated_from": str(args.template.resolve()),
                **recommendation_result(path),
            }
        elif args.command == "validate":
            path = args.path.resolve()
            validate_package(path)
            result = {"status": "ok", "path": str(path)}
        elif args.command == "migrate-plan":
            result = migration_plan(args.path)
        elif args.command == "migrate":
            path = migrate_package(
                args.source, args.workspace, args.slug, parse_stdin_json()
            )
            result = {
                "status": "ok",
                "path": str(path),
                "started": False,
                "migrated_from": str(args.source.resolve()),
                **recommendation_result(path),
            }
        else:
            path = update_package(args.path, parse_stdin_json())
            result = {
                "status": "ok",
                "path": str(path),
                "started": False,
                **recommendation_result(path),
            }
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (ValidationError, OSError) as exc:
        print("error: {}".format(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
