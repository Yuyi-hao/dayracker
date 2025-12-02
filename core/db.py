import os
import click
from datetime import datetime

import sqlite3
from flask import current_app, g

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    
    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()
    model_schema_folder = os.path.join(current_app.root_path, "..", "database_models")
    files = sorted(os.listdir(model_schema_folder))
    for filename in files:
        current_schema_path = os.path.join(model_schema_folder, filename) 
        with current_app.open_resource(current_schema_path) as f:
            print("Executing:", filename)
            db.executescript(f.read().decode('utf-8'))

@click.command('init-db')
def init_db_command():
    "Clear already existing db and create new one"
    init_db()
    click.echo("Database initialized")

sqlite3.register_converter(
    "timestamp", lambda val: datetime.fromisoformat(val.decode())
)

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)