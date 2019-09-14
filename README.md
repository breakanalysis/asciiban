# Textbased kanban issue tracker

Each issue has a key-value data structure with arbitrary information.
The mandatory keys are id (auto-generated increasing id), title and status.
Status is automatically initiated to 'backlog'.
The 'status' key has predefined usage as columns of a kanban board.
A kanban layout is given by an ordered list of column names, but by default the list
is ['backlog', 'selected', 'wip', 'blocked', 'done'].

TODO: add max rows for kanban board and crud operations for the kanban boards.
TODO: handle no issues dir
TODO: implement escape sequences for dates
TODO: nicer and more flexible views for the issues themselves
TODO: implement priority field and sorting function(s)

Each command is a selection followed by a command.

Commands are accomanied with python expressions QUERY and LAMBDA which are bodies of lambdas
whose variable is x. QUERY is used for issue selection by filtering and LAMBDA is used for setting key-value data on issues.

Install:

```
# get python 3
pip install -r requirements.txt
clone this repo
chmod +x ab.py
alias ab="/path/to/ab.py"
```


Usage:

```
fab show QUERY
fab show-issues QUERY
fab delete QUERY
fab update QUERY LAMBDA
fab create TITLE [LAMBDA]
```

Examples:

```
fab show 'date>\today'
fab show-issues 1
fab delete 'status=done'
fab update 'x.due_date+=timedelta(day=1)' 'x.importance>=3'
fab create 'my_title' 'x.date=\today'
```
