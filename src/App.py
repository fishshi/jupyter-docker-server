import json
import logging
import uvicorn
from uvicorn.config import LOGGING_CONFIG
from fastapi import FastAPI
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from KernelMgr import KernelMgr

class ExecuteRequest(BaseModel):
    kernelId: str
    code: str

class BaseRequest(BaseModel):
    kernelId: str

class App:
    def __init__(self):
        self.app = FastAPI()
        self.kernelMgr = KernelMgr()

        self.app.post("/execute")(self.execute)
        self.app.post("/start")(self.startKernel)
        self.app.get("/getStatus/{kernelId}")(self.getKernelStatus)
        self.app.post("/shutdown")(self.shutdownKernel)
        self.app.post("/restart")(self.restartKernel)
        self.app.post("/interrupt")(self.interruptKernel)
        self.app.get("/isReady")(self.isReady)

    async def execute(self, request: ExecuteRequest):
        async def msg_generator(kc):
            try:
                while True:
                    msg = await kc.get_iopub_msg()
                    if msg['header']['msg_type'] == 'status':
                        if msg['content']['execution_state'] == 'idle':
                            break
                        else:
                            continue
                    elif msg['header']['msg_type'] == 'execute_input':
                        output = {
                            'msg_type': msg['header']['msg_type'],
                            'content': {"execution_count": msg['content']['execution_count']}
                        }
                    else:
                        output = {
                            'msg_type': msg['header']['msg_type'],
                            'content': msg['content']
                        }
                    yield json.dumps(output) + "\n"

            except Exception as e:
                logging.exception("Exception in execute")
                error_msg = {'msg_type': 'error', 'content': str(e)}
                yield json.dumps(error_msg) + "\n"
            finally:
                kc.stop_channels()

        kernelId: str = request.kernelId
        code: str = request.code
        km = await self.kernelMgr.getKernel(kernelId)
        kc = km.client()
        kc.start_channels()
        kc.execute(code)
        return StreamingResponse(
            msg_generator(kc),
            media_type='application/json'
        )

    async def startKernel(self, request: BaseRequest):
        try:
            await self.kernelMgr.startKernel(request.kernelId)
            return JSONResponse(status_code=200, content={"statusCode": 200})
        except Exception as e:
            logging.exception("Exception in startKernel " + request.kernelId)
            return JSONResponse(status_code=500, content={"statusCode": 500, "message": str(e)})

    async def getKernelStatus(self, kernelId: str):
        try:
            return JSONResponse(status_code=200, content={"statusCode": 200, "data": self.kernelMgr.getKernelStatus(kernelId)})
        except Exception as e:
            logging.exception("Exception in getKernelStatus " + kernelId)
            return JSONResponse(status_code=500, content={"statusCode": 500, "message": str(e)})

    async def shutdownKernel(self, request: BaseRequest):
        try:
            await self.kernelMgr.shutdownKernel(request.kernelId)
            return JSONResponse(status_code=200, content={"statusCode": 200})
        except Exception as e:
            logging.exception("Exception in shutdownKernel " + request.kernelId)
            return JSONResponse(status_code=500, content={"statusCode": 500, "message": str(e)})

    async def restartKernel(self, request: BaseRequest):
        try:
            kernelId: str = request.kernelId
            await self.kernelMgr.restartKernel(kernelId)
            return JSONResponse(status_code=200, content={"statusCode": 200})
        except Exception as e:
            logging.exception("Exception in restartKernel " + request.kernelId)
            return JSONResponse(status_code=500, content={"statusCode": 500, "message": str(e)})

    async def interruptKernel(self, request: BaseRequest):
        try:
            kernelId: str = request.kernelId
            await self.kernelMgr.interruptKernel(kernelId)
            return JSONResponse(status_code=200, content={"statusCode": 200})
        except Exception as e:
            logging.exception("Exception in interruptKernel " + request.kernelId)
            return JSONResponse(status_code=500, content={"statusCode": 500, "message": str(e)})

    async def isReady(self):
        return "ready"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(asctime)s - %(levelprefix)s %(message)s"
LOGGING_CONFIG["formatters"]["access"]["fmt"] = "%(asctime)s - %(levelprefix)s %(client_addr)s - \"%(request_line)s\" %(status_code)s"

# 运行 FastAPI
if __name__ == '__main__':
    app_instance = App()
    uvicorn.run(app_instance.app, host="0.0.0.0", port=8888, timeout_keep_alive=60)
