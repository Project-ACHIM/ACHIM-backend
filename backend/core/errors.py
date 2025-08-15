from fastapi import HTTPException, status

class AppException(HTTPException):
    def __init__(self, status_code: int, message: str):
        super().__init__(status_code=status_code, detail=message)

class NotFoundException(AppException):
    def __init__(self, message: str = "リソースが見つかりません"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, message=message)

class UnauthorizedException(AppException):
    def __init__(self, message: str = "認証に失敗しました"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, message=message)

class BadRequestException(AppException):
    def __init__(self, message: str = "不正なリクエストです"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, message=message)