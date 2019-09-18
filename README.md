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
chmod +x fab.py
alias fab="/path/to/fab.py"
```


Usage:

```
fab --help
```

Examples:

```
fab create                            # create a new issue, opens editor
fab show -c "<2d"                     # show board with issues created earlier than 2 days ago
fab edit -c ">2h30m" -c "<1h"         # edit issues created between 1h and 2h30m ago
fab delete -p 4                       # delete issues whose parent has id 4
fab subtask 2 4                       # make issue 4 a subtask of issue 2
fab tag -a 5 "food,china"             # add tags food and china to all tasks descending from issue 5
fab show-issues -t "food,japan"       # display detailed information about all tasks tagged with food or japan (or both)
```
