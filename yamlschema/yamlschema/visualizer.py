from jinja2 import Environment, PackageLoader
import os

class Visualizer(object):
	
	def __init__(self, data=None):
		env = Environment(loader=PackageLoader('yamlschema', 'templates'))
		env.filters['id'] = id
		self.template = env.get_template('layout.html')
		self.data = data

	def render(self, output_file=None):
		ret = self.template.render(attributes=self.data)
		if output_file is None:
			return ret
		
		with open(output_file, "w") as f:
			f.write(ret)