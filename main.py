from logger import init_logging
from tests.test_pub import TestPublisher
import unittest
log = init_logging('noc-netmode')
from pubsub import subscriber

if __name__ == "__main__":
   unittest.main()
