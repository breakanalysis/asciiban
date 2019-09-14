import os
import glob
import json
from datetime import datetime as dt
from datetime import timedelta as td
from render import render_kanban
from constants import TITLE, CREATED, DATE_FORMAT, ID, STATUS, BACKLOG

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

def get_issue_path(issue):
    id = str(issue[ID])
    for filename in glob.iglob(os.path.join(issue_dir, '**'), recursive=True):
        if os.path.isfile(filename) and id == os.path.basename(filename):
            return filename
    raise Exception(f"Issue not found {id}")

def write_issue(issue, issue_path):
    with open(issue_path, 'w') as f:
        json_str = json.dumps(issue, default=json_convert, indent=2)
        f.write(json_str)

def unescape(lambda_body):
    return lambda_body

def format_date(date):
    return date.strftime(DATE_FORMAT)

def parse_date(date_str):
    return dt.strptime(date_str, DATE_FORMAT)

def matching_issues(query_body):
    matcher = compile_lambda(query_body)
    return filter(matcher, issues())

def compile_lambda(query_body):
    return eval('lambda x: ' + unescape(query_body))

def apply_udf(function_body, x):
    return exec(unescape(function_body))
            
def id_from_filename(filename):
    base = os.path.basename(filename)
    return int(os.path.splitext(base)[0])

def json_convert(o):
    if isinstance(o, dt):
        return format_date(o)

def show_cmd(query_body):
    for line in render_kanban(matching_issues(query_body)):
        print(line)

def show_issues_cmd(query_body):
    print(100 * '*')
    for issue in matching_issues(query_body):
        print(issue)
        print(100 * '*')

def create_cmd(title, lambda_body=None):
    ids = [id_from_filename(filename) for filename in issue_files()]
    last_id = 0 if len(ids) == 0 else max(ids)
    id = last_id + 1
    issue = {TITLE: title, CREATED: format_date(dt.utcnow()), ID: id, STATUS: BACKLOG}
    if lambda_body is not None:
        apply_udf(lambda_body, issue)
    if not os.path.exists(issue_dir):
        os.mkdir(issue_dir)
    issue_path = os.path.join(issue_dir, str(id))
    write_issue(issue, issue_path)

def delete_cmd(query_body):
    for issue in matching_issues(query_body):
        path = get_issue_path(issue)
        os.remove(path)

def update_cmd(query_body, lambda_body):
    for issue in matching_issues(query_body):
        apply_udf(lambda_body, issue)
        write_issue(issue, get_issue_path(issue))

def tag_issue(issue, tag):
    if 'tags' not in issue:
        issue['tags'] = set()
    issue['tags'].add(tag)

def tag_cmd(query_body, tag):
    for issue in matching_issues(query_body):
        tag_issue(issue, tag)
