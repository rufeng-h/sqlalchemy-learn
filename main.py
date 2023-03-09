import json
import os
from pathlib import Path
from urllib.parse import quote_plus

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from models import Post, Option


def load_db_auth():
    pwd = os.path.dirname(__file__)
    return json.loads(Path(os.path.join(pwd, 'db.json.local')).read_text(encoding='utf-8'))


db_auth = load_db_auth()

engine = create_engine("mysql+pymysql://%s:%s@%s:%s/%s" % (
    db_auth['username'], quote_plus(db_auth['password']), db_auth['host'], db_auth['port'], db_auth['database']),
                       echo=True)
with Session(engine) as session:
    stmt = select(Post.id).order_by(Post.create_time.desc())
    scalars = session.scalars(stmt)
    ids = scalars.fetchall()
    stmt = select(Option.option_value).where(Option.option_key == "post_permalink_type")
    post_link_type = session.scalar(stmt)
print(ids)
print(post_link_type)
