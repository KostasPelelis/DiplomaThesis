from yamlschema.visualizer import Visualizer
from yamlschema.parser import Parser

p = Parser(schema_file='examples/schema1.yml')
data = p.parse()
v = Visualizer(data=[data], output_file='output.html')
v.render() 