# Interactive HTML Checklist Guide

Use the generator script for consistent output. If editing the HTML manually, preserve this workflow.

## Structure

- Header: title, short safety statement, disk availability panel.
- Sticky toolbar: risk filters, select recommended, clear selection, copy commands.
- Summary cards: total items, selected items, estimated reclaimable space.
- Main table: checkbox, path, type and impact, size, risk, recommendation.
- Side panel: execution confirmation checkbox, command preview, protected-items notes.
- Fixed top-right feedback toast for copy/validation states.

## Interaction Rules

- Copy is blocked until at least one item is selected.
- Copy is blocked until the confirmation checkbox is checked.
- On successful copy, show a top-right toast, change the button text to "已复制", and flash the command box border.
- On copy failure, select the command text and show a clear top-right warning.
- Commands must be joined with real newline characters.
- Commands must end with a read-only cleanup report block that:
  - Creates `~/disk-cleanup-report-$(date +%Y%m%d-%H%M%S).txt`.
  - Records generation time, estimated reclaimable space, selected cleanup paths, and post-cleanup `df -h` output.
  - Runs after deletion/cache-cleaning commands, so the disk summary reflects the resulting state.
  - Does not perform additional deletion.

## Visual Rules

- Keep the UI utilitarian and dense; avoid marketing-style sections.
- Do not make the table header sticky; sticky headers can overlap rows in local file viewers.
- Keep cards at 8px radius or less.
- Use restrained colors: ink text, off-white background, green/amber/red risk accents.
- Make mobile layout readable by turning rows into block sections with `data-label` prefixes.
