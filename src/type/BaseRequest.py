from pydantic import BaseModel

class BaseRequest(BaseModel):
    """
    基础请求体
    """
    kernelId: str
    kernelName: str = "python3"
