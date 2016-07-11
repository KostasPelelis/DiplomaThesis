from logger import init_logging
from tests.test_pub import TestPublisher
import unittest

if __name__ == "__main__":
	log = init_logging('noc-netmode')
	unittest.main()
