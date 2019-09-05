import os
import glob
from datetime import datetime as dt
from datetime import timedelta as td

def issues():
    issue_dir = os.path.join(os.getcwd(), 'issues')
    if not os.path.exists(issue_dir):
        return []
    return [filename for filename in glob.iglob(os.path.join(issue_dir, '**'), recursive=True) if os.path.isfile(filename)]

def unescape(lambda_body):
    return lambda_body

def matching_issues(lambda_body):
    matcher = eval('lambda x: ' + unescape(lambda_body))
    return filter(matcher, issues())
            
def show_cmd(lambda_body):
    print(list(matching_issues(lambda_body)))
