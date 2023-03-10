import sys
import unittest

from loguru import logger
from sqlalchemy.orm import Session

from main import get_engine
from models import Post


def fil(record):
    print(record)
    return True


class Test(unittest.TestCase):
    def test_log(self):
        logger.remove(
        )
        logger.add(sys.stdout,
                   filter=fil)
        logger.debug("dafddsaf")
        logger.info("dafafasdfadsf")

    def test_read(self):
        engine = get_engine()
        with Session(engine) as session:
            post = session.get(Post, 5)
            print(post.format_content)
