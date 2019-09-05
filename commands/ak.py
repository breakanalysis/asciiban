from datetime import timedelta
from datetime import datetime
import click
from .commands import show_cmd

@click.group()
def ak():
    pass

@click.command()
@click.argument("lambda_body")
def show(lambda_body):
    show_cmd(lambda_body)

@click.command()
def create():
    pass

@click.command()
def delete():
    pass

@click.command()
def update():
    pass

ak.add_command(show)
ak.add_command(create)
ak.add_command(delete)
ak.add_command(update)

if __name__=='__main__':
    ak()
