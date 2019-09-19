from collections import defaultdict, Counter
from constants import (ID, STATUS, BACKLOG, UPCOMING,
                       WIP, BLOCKED, DONE, TITLE, HABIT,
                       SUCCESS, TRACK_RECORD, DUE_DATE)
from textwrap import wrap
from datetime import datetime as dt

def render_kanban(issues, statuses=None, box_width=15, box_rows=3):
    if statuses==None:
        statuses = [BACKLOG, UPCOMING, WIP, BLOCKED, DONE]
    rows = defaultdict(list)
    status_counter = Counter()
    for issue in issues:
        if STATUS in issue.keys() and issue[STATUS] in statuses:
            rows[issue[STATUS]].append(render_issue(issue, box_width, box_rows))
            status_counter[issue[STATUS]] += 1
    hline = (1 + len(statuses)*(3 + box_width)) * '-'
    lines = [hline]
    status_line = '| ' + ' | '.join([render_text(status, box_width) for status in statuses]) + ' |'
    lines.append(status_line)
    lines.append(hline)
    if len(status_counter) == 0:
        return lines
    for height in range(max(status_counter.values())):
        for sub_row in range(box_rows):
            line = '| ' + ' | '.join([fill_missing(rows[status], height, box_width, sub_row) for status in statuses]) + ' |'
            lines.append(line)
        lines.append(hline)
    return lines

def fill_missing(col, ind, box_width, sub_row):
    if ind >= len(col):
        return box_width * ' '
    return col[ind][sub_row]

def render_text(text, box_width):
    truncated = text[:min(box_width, len(text))]
    left_pad = (box_width - len(truncated))//2 * ' '
    right_pad = (box_width - len(left_pad) - len(truncated)) * ' '
    return left_pad + truncated + right_pad

def render_issue(issue, box_width, box_rows):
    rows = [render_text(str(issue[ID]), box_width)]
    if HABIT in issue:
        successes = 0
        failures = 0
        if TRACK_RECORD not in issue:
            issue[TRACK_RECORD] = []
        for data in issue[TRACK_RECORD]:
            if data[SUCCESS] == 'y':
                successes += 1
            else:
                failures += 1
        days_remaining = (issue[DUE_DATE] - dt.now()).days + 1
        rows.append(render_text(f"S:{successes} F:{failures} R:{days_remaining}", box_width))
    title = issue[TITLE]
    content = wrap(title, box_width)[:box_rows - len(rows)]
    rows.extend([render_text(t, box_width) for t in content])
    rows.extend([box_width * ' ' for _ in range(box_rows - len(rows))])
    return rows
