import asyncio
import logging
import time
from jupyter_client.manager import AsyncKernelManager
from type.KernelMgrWithInfo import KernelMgrWithInfo

class KernelMgrPool:
    """
    内核管理器池 <p>
    """
    def __init__(self):
        self.kernels: dict[str, KernelMgrWithInfo] = {}
        self.checkTask: asyncio.Task | None = None
        self.kernelLocks: dict[str, asyncio.Lock] = {}
        self.lock = asyncio.Lock()

    async def _getKernelLock(self, kernelId) -> asyncio.Lock:
        """
        内部函数，获取内核锁 <p>
        如果锁不存在则创建并返回 <p>
        """
        async with self.lock:
            if kernelId not in self.kernelLocks:
                self.kernelLocks[kernelId] = asyncio.Lock()
            return self.kernelLocks[kernelId]

    async def _startKernel(self, kernelId, kernelName) -> AsyncKernelManager:
        """
        内部函数，创建并启动内核对象 <p>
        创建并启动内核对象，放入对象字典中并返回内核对象 <p>
        如果内核对象已经存在则直接返回 <p>
        使用锁保证不会重复创建内核避免内核泄漏 <p>
        """
        lock = await self._getKernelLock(kernelId)
        async with lock:
            kwi: KernelMgrWithInfo | None = self.kernels.get(kernelId)
            if kwi:
                return kwi.getKernel()
            kwi = KernelMgrWithInfo(kernelName)
            self.kernels[kernelId] = kwi
            await kwi.getKernel().start_kernel()
            return kwi.getKernel()

    async def restartKernel(self, kernelId, kernelName) -> AsyncKernelManager:
        """
        重启并返回内核对象 <p>
        如果内核对象不存在则创建并返回 <p>
        """
        kwi: KernelMgrWithInfo | None = self.kernels.get(kernelId)
        if kwi:
            await kwi.getKernel().restart_kernel()
            return kwi.getKernel()
        else:
            return await self._startKernel(kernelId, kernelName)

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
        创建并启动内核 <p>
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
        kwi: KernelMgrWithInfo | None = self.kernels.get(kernelId)
        if not kwi:
            return await self._startKernel(kernelId, kernelName)
        else:
            return kwi.getKernel()

    async def interruptKernel(self, kernelId) -> None:
        """
        中断内核的执行 <p>
        如果内核对象不存在什么也不做 <p>
        """
        kwi: KernelMgrWithInfo | None = self.kernels.get(kernelId)
        if kwi:
            await kwi.getKernel().interrupt_kernel()

    async def shutdownKernel(self, kernelId) -> None:
        """
        关闭并删除内核对象 <p>
        如果内核对象不存在什么也不做 <p>
        删除内存对象后，同时删除内存锁对象 <p>
        """
        lock = await self._getKernelLock(kernelId)
        async with lock:
            kwi: KernelMgrWithInfo | None = self.kernels.get(kernelId)
            if kwi:
                await kwi.getKernel().shutdown_kernel()
                del self.kernels[kernelId]
        async with self.lock:
            if kernelId in self.kernelLocks:
                del self.kernelLocks[kernelId]

    def startCheckLoop(self) -> None:
        """
        启动自动关闭空闲内核功能 <p>
        """
        async def asyncCheckLoop():
            """
            空闲内核检测循环线程 <p>
            每隔一小时检查一次所有内核是否空闲 <p>
            空闲超过一小时的内核会被关闭 <p>
            """
            while True:
                try:
                    unActiveKernelIds = []
                    async with self.lock:
                        for kernelId, kwi in self.kernels.items():
                            if time.time() - kwi.lastActivityTime > 60 * 60:
                                unActiveKernelIds.append(kernelId)
                    for kernelId in unActiveKernelIds:
                        await self.shutdownKernel(kernelId)
                except Exception:
                    logging.exception("KernelMgrPool check loop error")
                await asyncio.sleep(60 * 60)
        if not self.checkTask or self.checkTask.done():
            self.checkTask = asyncio.create_task(asyncCheckLoop())
