import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__ + '/..')))

from yamlschema.parser import Parser

class ParserTest(unittest.TestCase):
	
	SCHEMA_FILE 	= "./examples/schema.yml" 
	EXAMPLE_FILE 	= "./examples/schema_example_policy.yaml"

	def test_parser(self):
		parser = Parser(self.SCHEMA_FILE)
		self.assertTrue(isinstance(parser, Parser))
		self.assertTrue(parser.data is None)
		self.assertTrue(parser.validator is None)

		data = parser.parse(self.EXAMPLE_FILE)
		self.assertEqual(data["name"], "PolicyName")
		self.assertEqual(len(data["conditions"]), 2)

if __name__ == "__main__":
	unittest.main()