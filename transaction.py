import time


class Transaction(object):
    def __init__(self, src, dst, value):
        self.src = src
        self.dst = dst
        self.value = value
        self.timestamp = time.time()

    def __str__(self):
        return f'From: {self.src}\nTo: {self.dst}\nValue: {self.value}'

