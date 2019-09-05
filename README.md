Textbased kanban issue tracker

Each issue has an id and a key-value data structure with arbitrary information.
The 'status' key has predefined usage as columns of a kanban board.
A kanban layout is given by an ordered list of column names.

Each command is a selection followed by a command.

Usage:

ak show QUERY
ak delete QUERY
ak update QUERY LAMBDA
ak create LAMBDA

Examples:

ak show 'date>\today'
ak delete 'status=done'
ak update 'x.due_date+=timedelta(day=1)' 'x.importance>=3'
ak create 'x.date=\today'
