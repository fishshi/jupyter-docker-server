import json
import logging
import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from AutoExiter import AutoExiter
from KernelMgr import KernelMgr

class ExecuteRequest(BaseModel):
    userId: int
    code: str

class BaseRequest(BaseModel):
    userId: int

class App:
    def __init__(self):
        self.app = FastAPI()
        self.autoExiter = AutoExiter()
        self.kernelMgr = KernelMgr()

        self.app.post("/execute")(self.execute)
        self.app.post("/start")(self.startKernel)
        self.app.get("/getStatus/{userId}")(self.getKernelStatus)
        self.app.post("/shutdown")(self.shutdownKernel)
        self.app.post("/restart")(self.restartKernel)
        self.app.get("/isReady")(self.isReady)

    async def execute(self, request: ExecuteRequest):
        self.autoExiter.updateActivityTime()
        async def msg_generator(kc):
            try:
                while True:
                    msg = await kc.get_iopub_msg()
                    if msg['header']['msg_type'] != 'status':
                        output = {
                            'msg_type': msg['header']['msg_type'],
                            'content': msg['content']
                        }
                        yield json.dumps(output) + "\n"
                    else:
                        if msg['content']['execution_state'] == 'idle':
                            break
            except Exception as e:
                logging.exception("Exception in execute")
                error_msg = {'msg_type': 'error', 'content': str(e)}
                yield json.dumps(error_msg) + "\n"
            finally:
                kc.stop_channels()
        userId = request.userId
        code = request.code
        km = await self.kernelMgr.getKernel(userId)
        kc = km.client()
        kc.start_channels()
        kc.execute(code)
        return StreamingResponse(
            msg_generator(kc),
            media_type='application/json'
        )

    async def startKernel(self, request: BaseRequest):
        self.autoExiter.updateActivityTime()
        try:
            await self.kernelMgr.startKernel(request.userId)
            return JSONResponse(status_code=200, content={"statusCode": 200})
        except Exception as e:
            logging.exception("Exception in startKernel")
            return JSONResponse(status_code=500, content={"statusCode": 500, "message": str(e)})

    async def getKernelStatus(self, userId: int):
        self.autoExiter.updateActivityTime()
        try:
            return JSONResponse(status_code=200, content={"statusCode": 200, "data": self.kernelMgr.getKernelStatus(userId)})
        except Exception as e:
            logging.exception("Exception in getKernelStatus")
            return JSONResponse(status_code=500, content={"statusCode": 500, "message": str(e)})

    async def shutdownKernel(self, request: BaseRequest):
        self.autoExiter.updateActivityTime()
        try:
            await self.kernelMgr.shutdownKernel(request.userId)
            return JSONResponse(status_code=200, content={"statusCode": 200})
        except Exception as e:
            logging.exception("Exception in shutdownKernel")
            return JSONResponse(status_code=500, content={"statusCode": 500, "message": str(e)})

    async def restartKernel(self, request: BaseRequest):
        self.autoExiter.updateActivityTime()
        try:
            userId = request.userId
            await self.kernelMgr.restartKernel(userId)
            return JSONResponse(status_code=200, content={"statusCode": 200})
        except Exception as e:
            logging.exception("Exception in restartKernel")
            return JSONResponse(status_code=500, content={"statusCode": 500, "message": str(e)})

    async def isReady(self):
        return "ready"

# 运行 FastAPI
if __name__ == '__main__':
    app_instance = App()
    uvicorn.run(app_instance.app, host="0.0.0.0", port=8888, timeout_keep_alive=60)
