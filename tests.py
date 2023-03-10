import sys
import unittest
from loguru import logger

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