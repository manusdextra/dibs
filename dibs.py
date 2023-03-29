import os
import click
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

from flask_migrate import Migrate
from app import create_app, db
from app.models import Category, User, Role

app = create_app(os.getenv("FLASK_CONFIG") or "default")
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(
        db=db,
        User=User,
        Role=Role,
        Category=Category,
    )


@app.cli.command()
@click.option("--coverage/--no-coverage", default=False, help="Enable code coverage")
def test(coverage):
    """Run the unit tests."""
    import unittest

    tests = unittest.TestLoader().discover("tests")
    unittest.TextTestRunner(verbosity=2).run(tests)


@app.cli.command()
def setup() -> None:
    Role.insert_roles()
    Category.insert_categories()
    admin = User(
        email=os.getenv("DIBS_ADMIN"),
        username="admin",
        password=os.getenv("DIBS_PASS"),
        confirmed=True,
    )
    db.session.add(admin)
    user = User(
        email=os.getenv("DIBS_USER"),
        username="user",
        password=os.getenv("DIBS_PASS"),
        confirmed=True,
    )
    db.session.add(user)
    db.session.commit()
