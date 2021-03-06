import threading
import random
import time
import logging
import sys

from os.path import dirname


sys.path.append(dirname(dirname(dirname(__file__))))

import hazelcast

def do_benchmark():
    REQ_COUNT = 50000
    ENTRY_COUNT = 10 * 1000
    VALUE_SIZE = 10000
    GET_PERCENTAGE = 40
    PUT_PERCENTAGE = 40

    logging.basicConfig(format='%(asctime)s%(msecs)03d [%(name)s] %(levelname)s: %(message)s', datefmt="%H:%M%:%S,")
    logging.getLogger().setLevel(logging.INFO)
    logger = logging.getLogger("main")

    config = hazelcast.ClientConfig()
    config.group_config.name = "dev"
    config.group_config.password = "dev-pass"
    config.network_config.addresses.append("127.0.0.1:5701")
    client = hazelcast.HazelcastClient(config)

    class Test(object):

        def __init__(self):
            self.ops = 0
            self.event = threading.Event()

        def incr(self, _):
            self.ops += 1
            if self.ops == REQ_COUNT:
                self.event.set()

        def run(self):
            my_map = client.get_map("default")
            for _ in xrange(0, REQ_COUNT):
                key = int(random.random() * ENTRY_COUNT)
                operation = int(random.random() * 100)
                if operation < GET_PERCENTAGE:
                    my_map.get_async(key).add_done_callback(self.incr)
                elif operation < GET_PERCENTAGE + PUT_PERCENTAGE:
                    my_map.put_async(key, "x" * VALUE_SIZE).add_done_callback(self.incr)
                else:
                    my_map.remove_async(key).add_done_callback(self.incr)
    t = Test()
    start = time.time()
    t.run()
    t.event.wait()
    time_taken = time.time() - start
    print("Took %s seconds for %d requests" % (time_taken, REQ_COUNT))
    print("ops per second: %s" % (t.ops/time_taken))

if __name__ == '__main__':
    do_benchmark()