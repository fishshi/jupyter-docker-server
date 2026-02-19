from pydantic import BaseModel

class ExecuteRequest(BaseModel):
    """
    执行代码请求体
    """
    kernelId: str
    kernelName: str = "python3"
    code: str
