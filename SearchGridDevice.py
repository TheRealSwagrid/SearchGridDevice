import json
import random
import signal
import sys
from threading import Thread
from time import sleep

from AbstractVirtualCapability import AbstractVirtualCapability, VirtualCapabilityServer, formatPrint

class SearchGridDevice(AbstractVirtualCapability):
    def __init__(self, server):
        super().__init__(server)
        self.uri = "SearchGridDevice"
        self.ISSECopterPosition = [0., 0., 0.]

    def SearchGridGetNextPosition(self, params: dict) -> dict:
        current_position = self.invoke_sync("GetISSECopterPosition", {})["Position3D"]
        test_field = self.invoke_sync("GetTestFieldBoundaries", {})
        pointa = test_field["TestFieldPointA"]
        pointb = test_field["TestFieldPointB"]

        formatPrint(self, f"Calculating position from current_position: {current_position}, pointa: {pointa} and pointb: {pointb}")

        x = random.uniform(pointa[0], pointb[0])
        y = random.uniform(pointa[1], pointb[1])

        return {"Position3D": [x, y, 1.]}

    def loop(self):
        pass

    def asyncFunc(self, params: dict):
        formatPrint(self, f"Async Function got sth: {json.dumps(params)}")



if __name__ == "__main__":
    # Needed for properly closing when process is being stopped with SIGTERM signal
    def handler(signum, frame):
        print("[Main] Received SIGTERM signal")
        listener.kill()
        quit(1)

    try:
        port = None
        if len(sys.argv[1:]) > 0:
            port = int(sys.argv[1])
        server = VirtualCapabilityServer(port)
        listener = SearchGridDevice(server)
        listener.start()
        signal.signal(signal.SIGTERM, handler)
        listener.join()
        # Needed for properly closing, when program is being stopped wit a Keyboard Interrupt
    except KeyboardInterrupt:
        print("[Main] Received KeyboardInterrupt")
        server.kill()
        listener.kill()
