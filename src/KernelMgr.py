import threading
from jupyter_client.manager import AsyncKernelManager

class KernelMgr:
    def __init__(self):
        self.kernels = {}
        self.lock = threading.Lock()

    async def _startKernel(self, kernelId):
        """
        内部函数，创建并启动内核对象 <p>
        创建并启动内核对象，放入对象字典中并返回内核对象 <p>
        如果内核对象已经存在则直接返回 <p>
        使用锁确保线程安全 <p>
        """
        with self.lock:
            km = self.kernels.get(kernelId)
            if km:
                return km
            km = AsyncKernelManager()
            await km.start_kernel()
            self.kernels[kernelId] = km
            return km

    async def restartKernel(self, kernelId):
        """
        重启并返回内核对象 <p>
        如果内核对象不存在则创建并返回 <p>
        """
        km = self.kernels.get(kernelId)
        if km:
            await km.restart_kernel()
        else:
            km = await self._startKernel(kernelId)
        return km

    def getKernelStatus(self, kernelId):
        """
        获取内核状态 <p>
        如果内核对象存在则返回 "运行中" <p>
        如果内核对象不存在则返回 "已关闭" <p>
        """
        if kernelId in self.kernels:
            return "运行中"
        else:
            return "已关闭"

    async def startKernel(self, kernelId):
        """
        启动并返回提示信息 <p>
        如果内核对象不存在则创建 <p>
        如果内核对象存在则什么也不做 <p>
        """
        if kernelId not in self.kernels:
            await self._startKernel(kernelId)

    async def getKernel(self, kernelId):
        """
        获取并返回内核对象 <p>
        如果内核对象不存在则创建并返回 <p>
        """
        km = self.kernels.get(kernelId)
        if not km:
            km = await self._startKernel(kernelId)
        return km

    async def shutdownKernel(self, kernelId):
        """
        关闭并删除内核对象 <p>
        如果内核对象不存在什么也不做 <p>
        """
        km = self.kernels.get(kernelId)
        if km:
            del self.kernels[kernelId]
            await km.shutdown_kernel()
