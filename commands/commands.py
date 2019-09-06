import os
import glob
import json
from datetime import datetime as dt
from datetime import timedelta as td
from render.render import render_kanban
from constants import TITLE, CREATED, DATE_FORMAT, ID, STATUS, BACKLOG

def issue_files():
    issue_dir = os.path.join(os.getcwd(), 'issues')
    if not os.path.exists(issue_dir):
        return []
    return [filename for filename in glob.iglob(os.path.join(issue_dir, '**'), recursive=True) if os.path.isfile(filename)]

def parse_issue_file(filename):
    with open(filename, 'r') as f:
        issue = json.load(f)
    return issue

def issues():
    return [parse_issue_file(filename) for filename in issue_files()]

def unescape(lambda_body):
    return lambda_body

def matching_issues(lambda_body):
    matcher = compile_lambda(lambda_body)
    return filter(matcher, issues())

def compile_lambda(lambda_body):
    return eval('lambda x: ' + unescape(lambda_body))

def apply_udf(function_body, x):
    return exec(unescape(function_body))
            
def show_cmd(lambda_body):
    # print(list(matching_issues(lambda_body)))
    for line in render_kanban(issues()):
        print(line)

def format_date(date):
    return date.strftime(DATE_FORMAT)

def parse_date(date_str):
    return dt.strptime(date_str, DATE_FORMAT)

def id_from_filename(filename):
    base = os.path.basename(filename)
    return int(os.path.splitext(base)[0])

def json_convert(o):
    if isinstance(o, dt):
        return format_date(o)

def create_cmd(title, lambda_body=None):
    ids = [id_from_filename(filename) for filename in issue_files()]
    last_id = 0 if len(ids) == 0 else max(ids)
    id = last_id + 1
    issue = {TITLE: title, CREATED: format_date(dt.utcnow()), ID: id, STATUS: BACKLOG}
    if lambda_body is not None:
        apply_udf(lambda_body, issue)
    issue_dir = os.path.join(os.getcwd(), 'issues')
    if not os.path.exists(issue_dir):
        os.mkdir(issue_dir)
    issue_path = os.path.join(issue_dir, str(id))
    with open(issue_path, 'w') as f:
        json_str = json.dumps(issue, default=json_convert, indent=2)
        f.write(json_str)
