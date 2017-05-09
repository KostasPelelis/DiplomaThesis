class a_stupid_class(object):

	def __init__(self):
		self.bound_class = None

	def wrapper(self, cls):
		self.bound_class = cls

a = a_stupid_class()

@a.wrapper
class WrappedClass(object):

	def a():
		return 5

assert(a.bound_class.a() == 5)