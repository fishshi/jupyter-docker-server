import os
import threading
import time

class AutoExiter:
    def __init__(self):
        self.idleTimeOut: int = 3600
        self.lastActivityTime: float = time.time()
        threading.Thread(target=self.checkIdleLoop, daemon=True).start()

    def updateActivityTime(self):
        self.lastActivityTime = time.time()

    def checkIdleLoop(self):
        while True:
            if time.time() - self.lastActivityTime > self.idleTimeOut:
                os._exit(0)
            else:
                time.sleep(300)