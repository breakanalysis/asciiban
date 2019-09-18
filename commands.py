import os
import glob
import json
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
from render import render_kanban
from tempfile import NamedTemporaryFile
import subprocess
import re
from constants import TITLE, CREATED, DESCRIPTION, DATE_FORMAT, ID, STATUS, BACKLOG, INDENT, TAGS

issue_dir = os.path.join(os.getcwd(), 'issues')

def issues():
    return [parse_issue_file(filename) for filename in issue_files()]

def parse_issue_file(filename):
    with open(filename, 'r') as f:
        issue = json.load(f, object_hook=datetime_parser)
        if TAGS in issue:
            issue[TAGS] = set(issue[TAGS])
        else:
            issue[TAGS] = set()
    return issue

def datetime_parser(dct):
    for k, v in dct.items():
        try:
            dct[k] = dt.strptime(v, DATE_FORMAT)
        except:
            pass
    return dct

def issue_files():
    if not os.path.exists(issue_dir):
        return []
    return [filename for filename in glob.iglob(os.path.join(issue_dir, '**'), recursive=True) if os.path.isfile(filename)]

def get_id_path(id):
    for filename in glob.iglob(os.path.join(issue_dir, '**'), recursive=True):
        if os.path.isfile(filename) and str(id) == os.path.basename(filename):
            return filename
    raise Exception(f"Issue not found {id}")

def get_issue_path(issue):
    return get_id_path(issue[ID])

def write_issue(issue, issue_path):
    with open(issue_path, 'w') as f:
        json_str = json.dumps(issue, default=json_convert, indent=INDENT)
        f.write(json_str)

def format_date(date):
    return date.strftime(DATE_FORMAT)

def parse_date(date_str):
    return dt.strptime(date_str, DATE_FORMAT)

def _is_negated(expr):
    return expr.startswith('~:')

def matching_issues(args):
    return (issue for issue in issues() if match_issue(issue, args))

def match_issue(issue, args):
    return all([
        not args.id or match_id(issue, args.id),
        not args.status or match_status(issue, args.status),
        not args.tags or all(match_tags(issue, expr) for expr in args.tags),
        not args.created or all(match_created(issue, expr) for expr in args.created),
        not args.ancestor or match_ancestor(issue, args.ancestor),
        not args.title or all(match_title(issue, expr) for expr in args.title),
        not args.description or all(match_description(issue, expr) for expr in args.description),
        not args.match or all(match_text(issue, expr) for expr in args.match),
        not args.parent or match_parent(issue, args.parent)
    ])

def match_id(issue, id):
    return issue['id'] == id

def match_status(issue, statuses):
    is_negated = _is_negated(statuses)
    if is_negated:
        statuses = statuses[2:]
    return is_negated ^ any((issue[STATUS].startswith(status) for status in statuses.split(',')))

def match_tags(issue, tags):
    is_negated = _is_negated(tags)
    if is_negated:
        tags = tags[2:]
    matches = any((tag in issue[TAGS] for tag in tags.split(',')))
    return is_negated ^ matches

def time_symbol_to_level(s):
    if s == 'Y':
        return 0 # day level
    elif s == 'M':
        return 0 # day level
    elif s == 'w':
        return 0 # day level
    elif s == 'd':
        return 0 # day level
    elif s == 'h':
        return 1 # hour level
    elif s == 'm':
        return 2 # minute level
    else:
        return 3 # second level

def round_time(t, level):
    for curr_lvl in range(level + 1, 5):
        if curr_lvl == 1:
            t = t.replace(hour=0)
        if curr_lvl == 2:
            t = t.replace(minute=0)
        if curr_lvl == 3:
            t = t.replace(second=0)
        if curr_lvl == 4:
            t = t.replace(microsecond=0)
    return t

def match_created(issue, expr):
    op = expr[0]
    expr = expr[1:]
    m = re.match('(?:([0-9]+)([YMwdhms]))+', expr)
    level = 0 # day level by default
    delta = relativedelta()
    if m:
        for i in range(1, int(m.lastindex/2) + 1):
            digits = int(m.group(2 * i - 1))
            unit = m.group(2 * i)
            level = max(level, time_symbol_to_level(unit))
            if unit == 'Y':
                delta += relativedelta(years=digits)
            elif unit == 'M':
                delta += relativedelta(months=digits)
            elif unit == 'w':
                delta += relativedelta(weeks=digits)
            elif unit == 'd':
                delta += relativedelta(days=digits)
            elif unit == 'h':
                delta += relativedelta(hours=digits)
            elif unit == 'm':
                delta += relativedelta(minutes=digits)
            elif unit == 's':
                delta += relativedelta(seconds=digits)
            else:
                raise Exception(f"Unrecognized time unit {unit}.")
        cutoff = round_time(dt.now(), level) - delta
    else:
        try:
            cutoff = dt.strptime(expr, date_fmt='%Y-%m-%d')
        except:
            raise Exception(f"Relative time point specification {expr} does not match ([0-9]+[YMwdhms])+ nor YEAR-MONTH-DAY.")
    issue_time = round_time(issue[CREATED], level)
    if op == '=':
        return issue_time == cutoff
    elif op == '<':
        return issue_time < cutoff
    elif op == '>':
        return issue_time > cutoff
    else:
        raise Exception(f"Unrecognized operator {op}")


def match_ancestor(issue, ancestor_id):
    return get_issue_path(issue).startswith(get_id_path(ancestor_id) + '.d')

def _lcs(X, Y, m, n): 
    if m == 0 or n == 0: 
       return 0; 
    elif X[m-1] == Y[n-1]: 
       return 1 + _lcs(X, Y, m-1, n-1); 
    else: 
       return max(_lcs(X, Y, m, n-1), _lcs(X, Y, m-1, n)); 

def lcs(X, Y):
    return _lcs(X, Y, len(X), len(Y))

def match_generic(issue_func):
    def decorated(issue, expr):
        if not expr:
            return True
        expr = expr.replace(' ', '')
        return lcs(expr, issue_func(issue).replace(' ', ''))/len(expr) > 0.8
    return decorated

def match_title(issue, expr):
    return match_generic(lambda i: i[TITLE])(issue, expr)

def match_description(issue, expr):
    return match_generic(lambda i: i[DESCRIPTION])(issue, expr)

def match_text(issue, expr):
    return match_generic(lambda i: i[TITLE] + i[DESCRIPTION])(issue, expr)

def match_parent(issue, parent_id):
    return _subtask_path(parent_id, issue[ID]) == get_issue_path(issue)

def id_from_filename(filename):
    base = os.path.basename(filename)
    return int(os.path.splitext(base)[0])

def json_convert(o):
    if isinstance(o, dt):
        return format_date(o)
    if isinstance(o, set):
        return list(o)

def show_cmd(args):
    for line in render_kanban(matching_issues(args)):
        print(line)

def show_issues_cmd(args):
    print(100 * '*')
    for issue in matching_issues(args):
        print(json.dumps(issue, default=json_convert, indent=INDENT))
        print(100 * '*')

def create_cmd():
    tmp = NamedTemporaryFile('w')
    template = {TITLE: '', STATUS: BACKLOG, DESCRIPTION: '', TAGS: [], 'parent_id': 0}
    tmp.file.write(json.dumps(template, indent=INDENT))
    tmp.file.flush()
    user_issue = _input_user_issue(tmp.name)
    if user_issue == None:
        print("Did not create issue.")
        return
    tmp.close()
    ids = [id_from_filename(filename) for filename in issue_files()]
    last_id = 0 if len(ids) == 0 else max(ids)
    id = last_id + 1
    user_issue.update({CREATED: format_date(dt.utcnow()), ID: id})
    parent_id = user_issue['parent_id']
    del user_issue['parent_id']
    if not os.path.exists(issue_dir):
        os.mkdir(issue_dir)
    subtask_path = _subtask_path(parent_id, id)
    write_issue(user_issue, subtask_path)
    print(f"Created issue {id} at {subtask_path}")

def _input_user_issue(path):
    subprocess.run(['vim', path])
    with open(path, 'r') as fin:
        edited_contents = fin.read()
    if not edited_contents.isspace():
        try:
            user_json = json.loads(edited_contents)
        except Exception as e:
            print("Not valid json, please try again.")
            input("Press ENTER to continue.")
            _input_user_issue(path)
        if 'title' not in user_json or not isinstance(user_json['title'], str) or user_json['title'] == '':
            print("Must use non-empty string value for attribute title.")
            input("Press ENTER to continue.")
            _input_user_issue(path)
        return user_json
    else:
        return None

def delete_cmd(args):
    for issue in matching_issues(args):
        path = get_issue_path(issue)
        os.remove(path)

def edit_cmd(args):
    issues = list(matching_issues(args))
    n = 1
    for issue in issues:
        path = get_issue_path(issue)
        if len(issues) > 1:
            print(f"Edit {path} ({n} of {len(issues)}).")
            input("Press ENTER to continue.")
        n += 1
        _input_user_issue(path)

def tag_issue(issue, tag):
    if TAGS not in issue:
        issue[TAGS] = set()
    issue[TAGS].add(tag)

def tag_cmd(args):
    tags = args.mod
    for issue in matching_issues(args):
        for tag in tags.split(','):
            tag_issue(issue, tag)
        write_issue(issue, get_issue_path(issue))

def subtask_cmd(parent_id, subtask_id):
    subtask_current_path = get_id_path(subtask_id)
    os.rename(subtask_current_path, _subtask_path(parent_id, subtask_id))

def _subtask_path(parent_id, subtask_id):
    if parent_id == 0:
        subtask_directory = issue_dir
    else:
        parent_path = get_id_path(parent_id)
        subtask_directory = parent_path + '.d'
    if not os.path.exists(subtask_directory):
        os.mkdir(subtask_directory)
    return os.path.join(subtask_directory, str(subtask_id))
