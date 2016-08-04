from pykwalify.core import Core
import os

class Parser:

	def __init__(self, schema_file=None):

		self.validator 		= None
		self.data 			= None
		self.schema_file    = None

		print(os.listdir())
		if schema_file is not None and os.path.exists(schema_file):
			self.schema_file = schema_file
		else:
			raise Exception("Couldn't not find schema file")



	def parse(self, source_file=None):
		
		if source_file is not None:
			try:
				self.validator = Core(
					source_file=source_file,
					schema_files=[self.schema_file]
				)
			except Exception as e:
				raise

		if self.validator is None:
			raise

		try:
			self.data = self.validator.validate()
			return self.data
		except Exception as e:
			raise


