import datetime
import os
from urllib.parse import quote_plus
import json
from pathlib import Path
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from models import Post


def load_db_auth():
    pwd = os.path.dirname(__file__)
    return json.loads(Path(os.path.join(pwd, 'db.json.local')).read_text(encoding='utf-8'))


db_auth = load_db_auth()

engine = create_engine("mysql+pymysql://%s:%s@%s:%s/%s" % (
    db_auth['username'], quote_plus(db_auth['password']), db_auth['host'], db_auth['port'], db_auth['database']),
                       echo=True)
with Session(engine) as session:
    stmt = select(Post).where(Post.create_time > datetime.datetime(2023, 1, 1))
    scalars = session.scalars(stmt)
    for post in scalars:
        print(post)
