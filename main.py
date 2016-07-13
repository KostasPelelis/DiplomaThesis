from logger import init_logging
log = init_logging('noc-netmode')

from tests.test_pub import TestPublisher
import unittest

if __name__ == "__main__":
	unittest.main()
