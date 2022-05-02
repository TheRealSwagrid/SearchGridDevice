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
        self.last_position = [0,0]

    def SearchGridGetNextPosition(self, params: dict) -> dict:
        self.ISSECopterPosition = self.invoke_sync("GetISSECopterPosition", {})["Position3D"]
        test_field = self.invoke_sync("GetTestFieldBoundaries", {})
        pointa = test_field["TestFieldPointA"]
        pointb = test_field["TestFieldPointB"]

        #formatPrint(self, f"Calculating position from current_position: {self.ISSECopterPosition}, pointa: {pointa} and pointb: {pointb}")

        next_pos = self.last_position
        next_pos[1] += 1
        if next_pos[1] >= 10:
            next_pos[0] += 1
            next_pos[1] = 0
        if next_pos[0] >= 10:
            next_pos = [0,0]
        self.last_position = next_pos
        
        return {"Position3D": self.GetMapWithResolution(test_field, 10, next_pos[0], next_pos[1])}

    def GetMapWithResolution(self, TestFieldBoundaries, res, x, y):
        minX = min(TestFieldBoundaries[0][0], TestFieldBoundaries[1][0])
        minY = min(TestFieldBoundaries[0][1], TestFieldBoundaries[1][1])
        maxX = max(TestFieldBoundaries[0][0], TestFieldBoundaries[1][0])
        maxY = max(TestFieldBoundaries[0][1], TestFieldBoundaries[1][1])

        map = [[None for y in range(res)] for x in range(res)]
        for i in range(res):
            for j in range(res):
                map[i][j] = [minX + i/(maxX - minX), minY + j/(maxY - minY), 1.]
        return map[x][y]
    
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
