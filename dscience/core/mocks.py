
class Mammal:
	def __init__(self, species):
		self.species = species
	def __eq_(self, o): return hash(o.species) == hash(self.species)
	def __hash__(self): return hash(self.species)
	def __repr__(self): return '<' + self.species + '>|'
	def __str__(self): return '<' + self.species + '>|'

class MockWritable:
	def __init__(self):
		self.data = None
	def write(self, data):
		self.data = 'write:' + data
	def flush(self):
		self.data += 'flush'
	def close(self):
		self.data += 'close'


class MockCallable:
	def __init__(self):
		self.data = None
	def __call__(self, data):
		self.data = 'call:' + data

class WritableWritableCallable(MockCallable, MockWritable): pass
