__all__ = (
    'BaseException',
    'NotImplementedError',
    'HTTPException'
)


class BaseException(Exception):
    pass
        
        
class NotImplementedError(BaseException):
    def __init__(self, message: str, *args: object) -> None:
        self.message = message
        self.args = args
     
        
class HTTPException(BaseException):
    pass
