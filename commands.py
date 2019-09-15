import os
import glob
import json
from datetime import datetime as dt
from datetime import timedelta as td
from render import render_kanban
from tempfile import NamedTemporaryFile
import subprocess
from constants import TITLE, CREATED, DATE_FORMAT, ID, STATUS, BACKLOG, INDENT

issue_dir = os.path.join(os.getcwd(), 'issues')

def issues():
    return [parse_issue_file(filename) for filename in issue_files()]

def parse_issue_file(filename):
    with open(filename, 'r') as f:
        issue = json.load(f)
    return issue

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

def matching_issues(args):
    return (issue for issue in issues() if match_issue(issue, args))

def match_issue(issue, args):
    return all([
        match_id(issue, args.id),
        match_status(issue, args.status),
        match_tags(issue, args.tags),
        match_created(issue, args.created),
        match_ancestor(issue, args.ancestor),
        match_title(issue, args.title),
        match_description(issue, args.description),
        match_text(issue, args.text),
        match_parent(issue, args.parent)
    ])

def match_id(issue, args.id):
    return issue['id'] == args.id

def match_status(issue, args.status):
    pass
def match_tags(issue, args.tags):
    pass
def match_created(issue, args.created):
    pass
def match_ancestor(issue, args.ancestor):
    pass
def match_title(issue, args.title):
    pass
def match_description(issue, args.description):
    pass
def match_text(issue, args.text):
    pass
def match_parent(issue, args.parent):
    pass

def id_from_filename(filename):
    base = os.path.basename(filename)
    return int(os.path.splitext(base)[0])

def json_convert(o):
    if isinstance(o, dt):
        return format_date(o)

def show_cmd(args):
    for line in render_kanban(matching_issues(args)):
        print(line)

def show_issues_cmd(args):
    print(100 * '*')
    for issue in matching_issues(args):
        print(issue)
        print(100 * '*')

def create_cmd():
    tmp = NamedTemporaryFile('w')
    template = {'title': '', 'status': BACKLOG, 'description': '', 'tags': [], 'parent_id': 0}
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
    pass

def tag_issue(issue, tag):
    if 'tags' not in issue:
        issue['tags'] = set()
    issue['tags'].add(tag)

def tag_cmd(args, tag):
    for issue in matching_issues(args):
        tag_issue(issue, tag)

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
