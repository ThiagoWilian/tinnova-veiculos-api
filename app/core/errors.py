from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class AppError(Exception):
    status_code = status.HTTP_400_BAD_REQUEST
    code = "APP_ERROR"
    message = "Erro na requisicao"

    def __init__(self, message: str | None = None) -> None:
        if message is not None:
            self.message = message


class NotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "NOT_FOUND"
    message = "Recurso nao encontrado"


class VehiclePlateConflict(AppError):
    status_code = status.HTTP_409_CONFLICT
    code = "VEHICLE_PLATE_CONFLICT"
    message = "Placa ja cadastrada"


class CurrencyRateUnavailable(AppError):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    code = "CURRENCY_RATE_UNAVAILABLE"
    message = "Cotacao do dolar indisponivel"


def error_payload(code: str, message: str) -> dict[str, dict[str, str]]:
    return {"detail": {"code": code, "message": message}}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
        """
        Trata erros de aplicacao.
        """
        return JSONResponse(
            status_code=exc.status_code,
            content=error_payload(exc.code, exc.message),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        """
        Trata erros de validacao do Pydantic.
        """
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content=error_payload("VALIDATION_ERROR", str(exc.errors())),
        )
