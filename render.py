from collections import defaultdict, Counter
from constants import ID, STATUS, BACKLOG, UPCOMING, WIP, BLOCKED, DONE, TITLE

def render_kanban(issues, statuses=None, box_width=15, box_rows=3):
    if statuses==None:
        statuses = [BACKLOG, UPCOMING, WIP, BLOCKED, DONE]
    rows = defaultdict(list)
    status_counter = Counter()
    for issue in issues:
        if STATUS in issue.keys() and issue[STATUS] in statuses:
            rows[issue[STATUS]].append(render_issue(issue, box_width, box_rows))
            status_counter[issue[STATUS]] += 1
    hline = (1 + len(statuses)*(1 + box_width)) * '-'
    lines = [hline]
    status_line = '|' + '|'.join([render_text(status, box_width) for status in statuses]) + '|'
    lines.append(status_line)
    lines.append(hline)
    for height in range(max(status_counter.values())):
        for sub_row in range(box_rows):
            line = '|' + '|'.join([fill_missing(rows[status], height, box_width, sub_row) for status in statuses]) + '|'
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
    title = issue[TITLE]
    for row_i in range(1, box_rows):
        rows.append(render_text(title[(row_i-1)*box_width:row_i*box_width], box_width))
    return rows
