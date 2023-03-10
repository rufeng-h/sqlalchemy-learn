import configparser
import os
from urllib.parse import quote_plus

import requests
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from models import Post


def load_db_auth():
    parser = configparser.ConfigParser()
    pwd = os.path.dirname(__file__)
    parser.read(os.path.join(pwd, 'db.conf'))
    return parser


def get_engine():
    db_auth = load_db_auth()['auth']

    en = create_engine("mysql+pymysql://%s:%s@%s:%s/%s" % (
        db_auth['username'], quote_plus(db_auth['password']), db_auth['host'], db_auth['port'], db_auth['database']),
                       echo=True)
    return en


if __name__ == '__main__':
    engine = get_engine()
    with Session(engine) as session:
        stmt = select(Post.id).order_by(Post.create_time.desc())
        scalars = session.scalars(stmt)
        ids = scalars.fetchall()

    blog_url_body = '\r\n'.join([f"http://windcf.com/archives/{blog_id}" for blog_id in ids])

    response = requests.post('http://data.zz.baidu.com/urls?site=windcf.com&token=X95hGKj0yvEILNyl', data=blog_url_body)
