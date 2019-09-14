#!/usr/bin/env python3
from datetime import timedelta
from datetime import datetime
import click
from commands import (
        show_cmd, create_cmd, update_cmd, delete_cmd,
        show_issues_cmd, tag_cmd, subtask_cmd
        )

@click.group()
def fab():
    pass

@click.command()
@click.argument("query_body")
def show_issues(query_body):
    show_issues_cmd(query_body)

@click.command()
@click.argument("query_body")
def show(query_body):
    show_cmd(query_body)

@click.command()
@click.argument("title")
@click.argument("lambda_body", required=False)
def create(title, lambda_body=None):
    create_cmd(title, lambda_body)

@click.command()
@click.argument("query_body")
def delete(query_body):
    delete_cmd(query_body)

@click.command()
@click.argument("query_body")
@click.argument("lambda_body")
def update(query_body, lambda_body):
    update_cmd(query_body, lambda_body)

@click.command()
@click.argument("query_body")
def tag(query_body, tag):
    tag_cmd(query_body, tag)

@click.command()
@click.argument("parent_id", type=int)
@click.argument("subtask_id", type=int)
def subtask(parent_id, subtask_id):
    subtask_cmd(parent_id, subtask_id)

for command in [
        show, show_issues, create, delete,
        update, tag, subtask]:
    fab.add_command(command)

if __name__=='__main__':
    fab()
