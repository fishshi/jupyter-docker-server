import time

from jupyter_client.manager import AsyncKernelManager

class KernelMgrWithInfo:
    """
    封装的内核管理器类 <p>
    存储内核管理器对象本身以及最近活跃时间 <p>
    """
    def __init__(self, kernelName):
        """
        创建内核管理器对象同时记录最近活跃时间
        """
        self.kernel: AsyncKernelManager = AsyncKernelManager(kernel_name = kernelName)
        self.lastActivityTime = time.time()

    def getKernel(self) -> AsyncKernelManager:
        """
        获取内核管理器对象同时更新最近活跃时间
        """
        self.lastActivityTime = time.time()
        return self.kernel
