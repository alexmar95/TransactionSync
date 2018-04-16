from collections import namedtuple
import time


class Transaction(namedtuple('Transaction', ['src', 'dst', 'value', 'timestamp'])):
    def __new__(cls, *args, **kwargs):
        kwargs['timestamp'] = time.time()
        return super().__new__(cls, *args, **kwargs)

    def __str__(self):
        return 'From: %s\tTo: %s\tValue: %s' % (self.src, self.dst, self.value)

    def __hash__(self):
        return hash(tuple(value for value in self))
