import asyncio
import threading
import time
from jupyter_client.manager import AsyncKernelManager

class KernelWithInfo:
    def __init__(self, kernelName):
        self.kernel: AsyncKernelManager = AsyncKernelManager(kernel_name = kernelName)
        self.lastActivityTime = time.time()
    def getKernel(self) -> AsyncKernelManager:
        self.lastActivityTime = time.time()
        return self.kernel

class KernelMgr:
    def __init__(self):
        self.kernels: dict[str, KernelWithInfo] = {}
        self.lock = asyncio.Lock()
        threading.Thread(target=self.checkLoop, daemon=True).start()

    async def _startKernel(self, kernelId, kernelName) -> AsyncKernelManager:
        """
        内部函数，创建并启动内核对象 <p>
        创建并启动内核对象，放入对象字典中并返回内核对象 <p>
        如果内核对象已经存在则直接返回 <p>
        使用协程锁保证不会重复创建内核 <p>
        """
        async with self.lock:
            kwi: KernelWithInfo | None = self.kernels.get(kernelId)
            if kwi:
                return kwi.getKernel()
            kwi = KernelWithInfo(kernelName)
            await kwi.getKernel().start_kernel()
            self.kernels[kernelId] = kwi
            return kwi.getKernel()

    async def restartKernel(self, kernelId, kernelName) -> AsyncKernelManager:
        """
        重启并返回内核对象 <p>
        如果内核对象不存在则创建并返回 <p>
        """
        kwi: KernelWithInfo | None = self.kernels.get(kernelId)
        if kwi:
            await kwi.getKernel().restart_kernel()
            return kwi.getKernel()
        else:
            km: AsyncKernelManager = await self._startKernel(kernelId, kernelName)
            return km

    def getKernelStatus(self, kernelId) -> str:
        """
        获取内核状态 <p>
        如果内核对象存在则返回 "运行中" <p>
        如果内核对象不存在则返回 "已关闭" <p>
        """
        if kernelId in self.kernels:
            return "运行中"
        else:
            return "已关闭"

    async def startKernel(self, kernelId, kernelName) -> None:
        """
        启动并返回提示信息 <p>
        如果内核对象不存在则创建 <p>
        如果内核对象存在则什么也不做 <p>
        """
        if kernelId not in self.kernels:
            await self._startKernel(kernelId, kernelName)

    async def getKernel(self, kernelId, kernelName) -> AsyncKernelManager:
        """
        获取并返回内核对象 <p>
        如果内核对象不存在则创建并返回 <p>
        """
        kwi: KernelWithInfo | None = self.kernels.get(kernelId)
        if not kwi:
            return await self._startKernel(kernelId, kernelName)
        else:
            return kwi.getKernel()

    async def interruptKernel(self, kernelId) -> None:
        """
        中断内核的执行 <p>
        如果内核对象不存在什么也不做 <p>
        """
        kwi: KernelWithInfo | None = self.kernels.get(kernelId)
        if kwi:
            await kwi.getKernel().interrupt_kernel()

    async def shutdownKernel(self, kernelId) -> None:
        """
        关闭并删除内核对象 <p>
        如果内核对象不存在什么也不做 <p>
        """
        kwi: KernelWithInfo | None = self.kernels.get(kernelId)
        if kwi:
            del self.kernels[kernelId]
            await kwi.getKernel().shutdown_kernel()

    def checkLoop(self) -> None:
        """
        初始化自动关闭空闲内核功能 <p>
        """
        async def asyncCheckLoop():
            """
            空闲内核检测循环线程 <p>
            每隔一小时检查一次所有内核是否空闲 <p>
            空闲超过一小时的内核会被关闭 <p>
            """
            while True:
                unActiveKernelIds = []
                for kernelId, kwi in self.kernels.items():
                    if time.time() - kwi.lastActivityTime > 60 * 60:
                        unActiveKernelIds.append(kernelId)
                for kernelId in unActiveKernelIds:
                    await self.shutdownKernel(kernelId)
                await asyncio.sleep(60 * 60)
        asyncio.run(asyncCheckLoop())
