from collections import namedtuple
import time

clss = namedtuple('Transaction', ['src', 'dst', 'value', 'timestamp'])

class Transaction(clss):
    def __new__(cls, *args, **kwargs):
        if len(args) <= 3:
            kwargs['timestamp'] = time.time()
        return clss.__new__(cls, *args, **kwargs)

    def __str__(self):
        return 'From: %s\tTo: %s\tValue: %s' % (self.src, self.dst, self.value)

    def __hash__(self):
        return hash(tuple(value for value in self))
