import json
import logging
from config.LoggingConfig import LoggingConfig
from type.BaseRequest import BaseRequest
from type.ExecuteRequest import ExecuteRequest
from fastapi import FastAPI
from fastapi.responses import JSONResponse, StreamingResponse
from contextlib import asynccontextmanager
from util.KernelMgrPool import KernelMgrPool

class App:
    def __init__(self):
        LoggingConfig.setup()
        self.kernelMgrPool = KernelMgrPool()
        self.app = FastAPI(lifespan=self.lifespan)

        self.app.post("/execute")(self.execute)
        self.app.post("/start")(self.startKernel)
        self.app.get("/getStatus/{kernelId}")(self.getKernelStatus)
        self.app.post("/shutdown")(self.shutdownKernel)
        self.app.post("/restart")(self.restartKernel)
        self.app.post("/interrupt")(self.interruptKernel)
        self.app.get("/isReady")(self.isReady)

    @asynccontextmanager
    async def lifespan(self, _: FastAPI):
        self.kernelMgrPool.startCheckLoop()
        yield

    async def execute(self, request: ExecuteRequest):
        async def msg_generator(kc):
            try:
                while True:
                    msg = await kc.get_iopub_msg()
                    logging.info(msg)
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
        km = await self.kernelMgrPool.getKernel(kernelId, request.kernelName)
        logging.info("Executing code: " + code)
        kc = km.client()
        kc.start_channels()
        kc.execute(code)
        return StreamingResponse(
            msg_generator(kc),
            media_type='application/json'
        )

    async def startKernel(self, request: BaseRequest):
        try:
            await self.kernelMgrPool.startKernel(request.kernelId, request.kernelName)
            return JSONResponse(status_code=200, content={"statusCode": 200})
        except Exception as e:
            logging.exception("Exception in startKernel " + request.kernelId)
            return JSONResponse(status_code=500, content={"statusCode": 500, "message": str(e)})

    async def getKernelStatus(self, kernelId: str):
        try:
            return JSONResponse(status_code=200, content={"statusCode": 200, "data": self.kernelMgrPool.getKernelStatus(kernelId)})
        except Exception as e:
            logging.exception("Exception in getKernelStatus " + kernelId)
            return JSONResponse(status_code=500, content={"statusCode": 500, "message": str(e)})

    async def shutdownKernel(self, request: BaseRequest):
        try:
            await self.kernelMgrPool.shutdownKernel(request.kernelId)
            return JSONResponse(status_code=200, content={"statusCode": 200})
        except Exception as e:
            logging.exception("Exception in shutdownKernel " + request.kernelId)
            return JSONResponse(status_code=500, content={"statusCode": 500, "message": str(e)})

    async def restartKernel(self, request: BaseRequest):
        try:
            kernelId: str = request.kernelId
            await self.kernelMgrPool.restartKernel(kernelId, request.kernelName)
            return JSONResponse(status_code=200, content={"statusCode": 200})
        except Exception as e:
            logging.exception("Exception in restartKernel " + request.kernelId)
            return JSONResponse(status_code=500, content={"statusCode": 500, "message": str(e)})

    async def interruptKernel(self, request: BaseRequest):
        try:
            kernelId: str = request.kernelId
            await self.kernelMgrPool.interruptKernel(kernelId)
            return JSONResponse(status_code=200, content={"statusCode": 200})
        except Exception as e:
            logging.exception("Exception in interruptKernel " + request.kernelId)
            return JSONResponse(status_code=500, content={"statusCode": 500, "message": str(e)})

    async def isReady(self):
        return "ready"
