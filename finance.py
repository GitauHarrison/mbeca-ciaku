from app import db, create_app
from app.models import User


app = create_app()


@app.shell_context_processor
def make_shell_context():
    return dict(
        db=db,
        User=User)
