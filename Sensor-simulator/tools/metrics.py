import time

class Metrics:
    def __init__(self):
        self.reads = 0
        self.writes = 0
        self.start = time.time()

    def report(self):
        elapsed = time.time() - self.start
        return {
            "reads_per_sec": self.reads / elapsed,
            "writes_per_sec": self.writes / elapsed
        }
