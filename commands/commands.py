import os
import glob
import json
from datetime import datetime as dt
from datetime import timedelta as td
from render.render import render_kanban

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
    matcher = eval('lambda x: ' + unescape(lambda_body))
    return filter(matcher, issues())
            
def show_cmd(lambda_body):
    # print(list(matching_issues(lambda_body)))
    for line in render_kanban(issues()):
        print(line)
