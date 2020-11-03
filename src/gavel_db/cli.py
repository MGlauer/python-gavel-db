"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -mgavel_db` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``gavel_db.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``gavel_db.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""
import os

from gavel.cli import cli
import gavel.config.settings as settings
from gavel.dialects.tptp.parser import TPTPParser
from gavel_db.dialects.db.structures import (
    store_all,
)
from gavel_db.dialects.db.compiler import DBCompiler

import click
from alembic import command
from alembic.config import Config

ROOT_DIR = os.path.dirname(__file__)
alembic_cfg = Config(os.path.join(ROOT_DIR, "alembic.ini"))
alembic_cfg.set_main_option("script_location", os.path.join(ROOT_DIR, "alembic"))

@click.group()
def db():
    pass

@click.command()
@click.argument("path", default=None)
@click.option("-r", default=False)
def store(path, r):
    parser = TPTPParser()
    compiler = DBCompiler()
    store_all(path, parser, compiler)

@click.command()
@click.option("-p", default=settings.TPTP_ROOT)
def store_problems(p):
    settings.TPTP_ROOT = p
    build_tptp.store_problems()


@click.command()
@click.option("-p", default=settings.TPTP_ROOT)
def store_solutions(p):
    """Drop tables created gy init-db"""
    build_tptp.all_solution(p)


@click.command()
def drop_db():
    """Drop tables created gy init-db"""
    command.downgrade(alembic_cfg, "base")


@click.command()
@click.option("-p", default=settings.TPTP_ROOT)
def clear_db(p):
    """Drop tables created gy init-db and recreate them"""
    command.downgrade(alembic_cfg, "base")
    command.upgrade(alembic_cfg, "head")

@click.command()
def migrate_db():
    """Create tables for storage of formulas"""
    command.upgrade(alembic_cfg, "head")

db.add_command(migrate_db)
db.add_command(drop_db)
db.add_command(clear_db)
db.add_command(store_problems)
db.add_command(store)
db.add_command(store_solutions)

cli.add_source(db)
