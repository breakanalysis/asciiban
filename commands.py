import os
import glob
import json
from collections import Counter
from datetime import datetime as dt
from datetime import timedelta as td
from dateutil.relativedelta import relativedelta
from render import render_kanban
from tempfile import NamedTemporaryFile
import subprocess
import re
import regex
import readchar
from constants import *
from settings import (get_settings, get_dotfile, get_board_settings, get_board_settings_file,
                      default_settings, default_board_settings)
from sorting import get_sort_value

issue_dir = f"{get_settings()[DATADIR]}/issues"

def issues():
    return [parse_issue_file(filename) for filename in issue_files()]

def parse_issue_file(filename):
    with open(filename, 'r') as f:
        issue = json.load(f, object_hook=datetime_parser)
        if TAGS in issue:
            issue[TAGS] = set(issue[TAGS])
        else:
            issue[TAGS] = set()
    if DESCRIPTION not in issue:
        issue[DESCRIPTION] = ""
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

def save_issue(issue):
    write_issue(issue, get_issue_path(issue))

def load_issue(id):
    return parse_issue_file(get_id_path(id))

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
        not args.ids or match_id(issue, args.ids),
        not args.status or match_status(issue, args.status),
        not args.tags or all(match_tags(issue, expr) for expr in args.tags),
        not args.created or all(match_created(issue, expr) for expr in args.created),
        not args.ancestor or match_ancestor(issue, args.ancestor),
        not args.title or all(match_title(issue, expr) for expr in args.title),
        not args.description or all(match_description(issue, expr) for expr in args.description),
        not args.match or all(match_text(issue, expr) for expr in args.match),
        not args.parent or match_parent(issue, args.parent)
    ])

def match_id(issue, ids):
    return any(issue['id'] == int(id) for id in ids.split(','))

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

def _find_cutoff(expr, past=True):
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
        if past:
            cutoff = round_time(dt.now(), level) - delta
        else:
            cutoff = round_time(dt.now(), level) + delta
    else:
        try:
            cutoff = dt.strptime(expr, date_fmt='%Y-%m-%d')
        except:
            raise Exception(f"Relative time point specification {expr} does not match ([0-9]+[YMwdhms])+ nor YEAR-MONTH-DAY.")
    return cutoff, level

def match_created(issue, expr):
    op = expr[0]
    expr = expr[1:]
    cutoff, level = _find_cutoff(expr)
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

def fuzzy_match(expr, text):
    expr = expr.lower()
    pattern1 = ' '.join(f"({e})" + "{e<=1}" for e in expr.split(' '))
    pattern2 = f"({expr})" + "{e<=" + f"{round(len(expr)*0.15)}" + "}"
    return bool(regex.search(pattern1, text.lower()) or regex.search(pattern2, text.lower()))

def match_generic(issue_func):
    def decorated(issue, expr):
        if not expr:
            return True
        return fuzzy_match(expr, issue_func(issue))
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
    indent = None
    if args.pretty:
        print(100 * '*')
        indent = INDENT
    for issue in matching_issues(args):
        if not args.no_path:
            print(get_issue_path(issue))
        if not args.no_details:
            print(json.dumps(issue, default=json_convert, indent=indent))
        if args.pretty:
            print(100 * '*')

def create_cmd(issue_type='issue'):
    tmp = NamedTemporaryFile('w')
    template = {TITLE: '', STATUS: BACKLOG, DESCRIPTION: '', TAGS: [], 'parent_id': 0}
    if issue_type==HABIT:
        template[DUE_DATE] = '30d'
        template[HABIT] = True
    tmp.file.write(json.dumps(template, indent=INDENT))
    tmp.file.flush()
    user_issue = _input_user_issue(tmp.name)
    if user_issue == None:
        print(f"Did not create {issue_type}.")
        return
    tmp.close()
    ids = [id_from_filename(filename) for filename in issue_files()]
    last_id = 0 if len(ids) == 0 else max(ids)
    id = last_id + 1
    user_issue.update({CREATED: format_date(dt.now()), ID: id})
    parent_id = user_issue['parent_id']
    del user_issue['parent_id']
    if DUE_DATE in user_issue:
        user_issue[DUE_DATE], _ = _find_cutoff(user_issue[DUE_DATE], past=False)
    if not os.path.exists(issue_dir):
        os.mkdir(issue_dir)
    subtask_path = _subtask_path(parent_id, id)
    write_issue(user_issue, subtask_path)
    print(f"Created issue {id} at {subtask_path}")

def _input_user_issue(path):
    subprocess.run([get_settings()[EDITOR], path])
    with open(path, 'r') as fin:
        edited_contents = fin.read()
    if not edited_contents.isspace():
        try:
            user_json = json.loads(edited_contents)
        except Exception as e:
            print("Not valid json, please try again.")
            input("Press ENTER to continue.")
            return _input_user_issue(path)
        if TITLE not in user_json or not isinstance(user_json[TITLE], str) or user_json[TITLE] == '':
            print("Must use non-empty string value for attribute title.")
            input("Press ENTER to continue.")
            return _input_user_issue(path)
        if STATUS not in user_json or user_json[STATUS] not in get_board_settings()[STATUS_COLUMNS]:
            print(f"Must have status with a value in {get_board_settings()[STATUS_COLUMNS]}.")
            input("Press ENTER to continue.")
            return _input_user_issue(path)
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
        save_issue(issue)

def subtask_cmd(args):
    for issue in matching_issues(args):
        subtask_id = issue[ID]
        subtask_current_path = get_id_path(subtask_id)
        os.rename(subtask_current_path, _subtask_path(args.parent_id, subtask_id))

def _subtask_path(parent_id, subtask_id):
    if parent_id == 0:
        subtask_directory = issue_dir
    else:
        parent_path = get_id_path(parent_id)
        subtask_directory = parent_path + '.d'
    if not os.path.exists(subtask_directory):
        os.mkdir(subtask_directory)
    return os.path.join(subtask_directory, str(subtask_id))

def rename_cmd(args):
    issue = load_issue(args.id)
    issue[TITLE] = args.title
    save_issue(issue)

def transition_cmd(args):
    if args.new_status not in get_board_settings()[STATUS_COLUMNS]:
        print(f"Must use status with a value in {get_board_settings()[STATUS_COLUMNS]}.")
        return
    for issue in matching_issues(args):
        issue[STATUS] = args.new_status
        save_issue(issue)

def _user_edit_file(path):
    subprocess.run([get_settings()[EDITOR], path])
    with open(path, 'r') as fin:
        edited_contents = fin.read()
    return edited_contents

def log_cmd(args):
    date = format_date(dt.now())
    id = args.id
    issue = load_issue(id)
    if HABIT in issue and not args.no_report:
        success = ''
        while not success in ['y', 'n']:
            print("Did you succeed? (y/n)?")
            success = readchar.readchar()
        if not TRACK_RECORD in issue:
            issue[TRACK_RECORD] = []
        issue[TRACK_RECORD].append({SUCCESS: success, DATE: date})
    if LOG in issue:
        log = issue[LOG]
    else:
        log = ''
    log += date + ':\n'
    tmp = NamedTemporaryFile('w')
    tmp.file.write(log)
    tmp.file.flush()
    log = _user_edit_file(tmp.name)
    tmp.close()
    issue[LOG] = log
    save_issue(issue)

def edit_and_validate_settings(dotfile):
    subprocess.run([get_settings()[EDITOR], dotfile])
    try:
        get_settings()
        return True
    except Exception as e:
        print(e)
        return False

def settings_cmd():
    dotfile = get_dotfile()
    if not os.path.exists(dotfile):
        defaults = default_settings()
        contents = [f"#{k}={defaults[k]}" for k in defaults]
        with open(dotfile, 'w') as f:
             for line in contents:
                 f.write(line + '\n')
    while not edit_and_validate_settings(dotfile):
        input("Press enter to try again.")

def edit_and_validate_board_settings(board_settings_file):
    subprocess.run([get_settings()[EDITOR], board_settings_file])
    try:
        get_board_settings()
    except Exception as e:
        print(e)
        return False
    return check_defaults() and test_sorting()

def test_sorting():
    issue = {ID: 0}
    try:
        v = get_sort_value(issue)
    except Exception as e:
        print(e)
        import pdb; pdb.set_trace()
        return False
    return True

def check_defaults():
    board_settings = get_board_settings()
    FIELD = r'[a-zA-Z_][a-zA-Z0-9_]*'
    used_fields = set(re.findall(FIELD, board_settings[BACKLOG_SORTING]))
    fields_with_defaults = set(board_settings[CUSTOM_FIELDS])
    missing_defaults = used_fields - fields_with_defaults - {CREATED}
    if len(missing_defaults) > 0:
        print(f"Fields {list(missing_defaults)} in {BACKLOG_SORTING} do not have defaults in {CUSTOM_FIELDS}.")
        return False
    return True

def board_settings_cmd():
    board_settings_file = get_board_settings_file()
    if not os.path.exists(board_settings_file):
        defaults = default_board_settings()
        with open(board_settings_file, 'w') as f:
            for key in defaults:
                if key == STATUS_COLUMNS:
                    f.write("#{key}={rhs}\n".format(key=key, rhs=",".join([str(v) for v in defaults[key]])))
                elif key == CUSTOM_FIELDS:
                    f.write("#{key}={rhs}\n".format(key=key, rhs=",".join([f"{k}:{v}" for k, v in defaults[key].items()])))
                else:
                    f.write("#{key}={rhs}\n".format(key=key, rhs=defaults[key]))
    while not edit_and_validate_board_settings(board_settings_file):
        input("Press enter to try again.")

def push_cmd():
    cmds = [['git', 'add', '.'], ['git', 'commit', '-m"Asciiban autocommit"'], ['git', 'push']]
    for cmd in cmds:
        full_cmd = ' '.join(cmd)
        try:
            ret = subprocess.run(cmd, cwd=get_settings()[DATADIR])
        except:
            raise Exception("Something went wrong with {}".format(full_cmd))
        if ret.returncode != 0:
            return

def pull_cmd():
    cmd = ['git', 'pull']
    full_cmd = ' '.join(cmd)
    try:
        ret = subprocess.run(cmd, cwd=get_settings()[DATADIR])
    except:
        raise Exception("Something went wrong with {}".format(full_cmd))

def status_cmd():
    cmd = ['git', 'status']
    full_cmd = ' '.join(cmd)
    ret = subprocess.run(cmd, cwd=get_settings()[DATADIR])

def diff_cmd():
    cmds = [['git', 'add', '.'], ['git', 'diff', '--cached']]
    for cmd in cmds:
        full_cmd = ' '.join(cmd)
        ret = subprocess.run(cmd, cwd=get_settings()[DATADIR])

def ls_tags_cmd(args):
    tags = Counter()
    for issue in matching_issues(args):
        tags.update(issue[TAGS])
    print(dict(tags))
