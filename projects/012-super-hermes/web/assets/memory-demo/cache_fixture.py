"""Research-built, intentionally unbounded cache and an LRU alternative.

This is a mechanism demonstration, not upstream Super Hermes code or an AI test.
"""
from collections import OrderedDict

PAYLOAD_BYTES = 64 * 1024


def make_response():
    return bytearray(PAYLOAD_BYTES)


class UnboundedCache:
    def __init__(self):
        self.cache = {}

    def get(self, key):
        if key not in self.cache:
            self.cache[key] = make_response()
        return self.cache[key]

    def clear(self):
        self.cache.clear()


class BoundedCache:
    def __init__(self, capacity=32):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key):
        if key not in self.cache:
            self.cache[key] = make_response()
        self.cache.move_to_end(key)
        while len(self.cache) > self.capacity:
            self.cache.popitem(last=False)
        return self.cache[key]

    def clear(self):
        self.cache.clear()
