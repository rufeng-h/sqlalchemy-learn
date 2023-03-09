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
    auth = json.loads(Path(os.path.join(pwd, 'db.json.local')).read_text(encoding='utf-8'))
    return auth['username'], auth['password']


username, password = load_db_auth()

engine = create_engine("mysql+pymysql://%s:%s@81.71.161.25:3306/halodb" % (username, quote_plus(password)), echo=True)
with Session(engine) as session:
    stmt = select(Post).where(Post.create_time > datetime.datetime(2023, 1, 1))
    scalars = session.scalars(stmt)
    for post in scalars:
        print(post)
