#!/usr/bin/env python3
from datetime import timedelta
from datetime import datetime
from commands import (
        show_cmd, create_cmd, edit_cmd, delete_cmd,
        show_issues_cmd, tag_cmd, subtask_cmd,
        rename_cmd, transition_cmd, log_cmd, settings_cmd
        )
import click
from argparse import ArgumentParser
from constants import HABIT

def add_filtering(parsers):
    for parser in parsers:
        parser.add_argument('-i', '--id', type=int, help="Match issue with given id.")
        parser.add_argument('-s', '--status', help="Match issues whose status matches any of given comma separated statuses. May be repeated.")
        parser.add_argument('-T', '--tags', action='append', help="Match issues that have at least one tag among the comma separated tags in TAGS. May be repeated.")
        # parser.add_argument('-D', '--due-date', action='append', help="")
        parser.add_argument('-c', '--created', action='append', help="Match by creation date pattern CREATED which starts with [<>=] followed by ([0-9]+[YMwdhms])+ or YEAR-MONTH-DAY. For equality filtering, current time and creation time are rounded downward to the same precision as used in CREATED (i.e. day, hour or minute precision). May be repeated.")
        parser.add_argument('-a', '--ancestor', type=int, help="Match issues that are decendants of issue with id ANCESTOR.")
        parser.add_argument('-t', '--title', action='append', help="Fuzzily match issues by comparing their title with TITLE. May be repeated.")
        parser.add_argument('-d', '--description', action='append', help="Fuzzily match issues by comparing their description with DESCRIPTION. May be repeated.")
        parser.add_argument('-m', '--match', action='append', help="Fuzzily match issues by comparing their title and description with MATCH. May be repeated.")
        parser.add_argument('-p', '--parent', type=int, help="Match issues that are children of issue with id PARENT.")
        # parser.add_argument('-P', '--priority', action='append', help="")

def add_show_issues_parser(sub_parsers):
    show_issues_parser = sub_parsers.add_parser("show-issues", help="Detailed view of issues matching given filters.")
    show_issues_parser.add_argument("--no-path", action='store_true', help="If given, do not print path of matching issues.")
    show_issues_parser.add_argument("--no-details", action='store_true', help="If given, do not print issue details.")
    show_issues_parser.add_argument("--pretty", action='store_true', help="If given, pretty print issue details.")
    return show_issues_parser
    
def add_tag_parser(sub_parsers):
    tag_parser = sub_parsers.add_parser("tag")
    tag_parser.add_argument("mod", help="Comma delimited tags to add (or delete if tag is prepended by ~). E.g. fab tag -i 10 ~food,cuisine")
    return tag_parser

def add_subtask_parser(sub_parsers):
    subtask_parser = sub_parsers.add_parser("subtask", help="Make all issues matching given filters subtasks of issue with id PARENT_ID.")
    subtask_parser.add_argument("parent_id")
    return subtask_parser

def add_rename_parser(sub_parsers):
    rename_parser = sub_parsers.add_parser("rename", help="Changes issues title.")
    rename_parser.add_argument('title', help="The new title")
    rename_parser.add_argument('-i', '--id', type=int, help="Issue id to operate on")
    return rename_parser

def add_transition_parser(sub_parsers):
    transition_parser = sub_parsers.add_parser("transition", help="Transition all issues matching given filters to status NEW_STATUS.")
    transition_parser.add_argument('new_status', help="The new status")
    return transition_parser

def add_log_parser(sub_parsers):
    log_parser = sub_parsers.add_parser("log", help="Edit an issues log in editor. Additionally if issue is habit, report success or failure.")
    log_parser.add_argument('-i', '--id', type=int, help="Id of issue whose log to edit.")
    log_parser.add_argument('--no-report', action='store_true', help="Just edit log without reporting success or failure.")
    return log_parser

if __name__=='__main__':
    parser = ArgumentParser()
    sub_parsers = parser.add_subparsers(help='Available commands', dest='command')
    show_issues_parser = add_show_issues_parser(sub_parsers) 
    show_parser = sub_parsers.add_parser("show", help="Display a kanban board.")
    create_parser = sub_parsers.add_parser("create", help="Create an issue by editing a json template.")
    create_habit_parser = sub_parsers.add_parser("create-habit", help="Create a habit issue by editing a json template.")
    delete_parser = sub_parsers.add_parser("delete", help="Delete all issues matching given filters.")
    edit_parser = sub_parsers.add_parser("edit", help="Edit all issues matching given filters.")
    tag_parser = add_tag_parser(sub_parsers)
    subtask_parser = add_subtask_parser(sub_parsers)
    transition_parser = add_transition_parser(sub_parsers)
    add_rename_parser(sub_parsers)
    log_parser = add_log_parser(sub_parsers)
    settings_parser = sub_parsers.add_parser("settings", help="Edit asciiban settings file.")
    add_filtering([show_parser, show_issues_parser, delete_parser, edit_parser, tag_parser, subtask_parser,
                   transition_parser])
    args = parser.parse_args()
    command = args.command
    if command == 'show-issues':
        show_issues_cmd(args)
    elif command == 'show':
        show_cmd(args)
    elif command == 'create':
        create_cmd()
    elif command == 'delete':
        delete_cmd(args)
    elif command == 'edit':
        edit_cmd(args)
    elif command == 'tag':
        tag_cmd(args)
    elif command == 'subtask':
        subtask_cmd(args)
    elif command == 'rename':
        rename_cmd(args)
    elif command == 'transition':
        transition_cmd(args)
    elif command == 'create-habit':
        create_cmd(HABIT)
    elif command == 'log':
        log_cmd(args)
    elif command == 'settings':
        settings_cmd()
    else:
        pass
