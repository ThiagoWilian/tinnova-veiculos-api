from datetime import datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, Field, field_validator


class VeiculoBase(BaseModel):
    marca: str = Field(..., min_length=1, max_length=80)
    modelo: str = Field(..., min_length=1, max_length=120)
    ano: int = Field(..., ge=1900, le=datetime.now().year + 1) # +1 pq pode ter veículos com ano acima do ano atual
    cor: str = Field(..., min_length=1, max_length=50)
    placa: str = Field(..., min_length=7, max_length=10)

    # Tratamento de dados
    @field_validator("marca", "modelo", "cor", "placa")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()

    @field_validator("placa")
    @classmethod
    def normalize_plate(cls, value: str) -> str:
        return value.strip().upper()

class VeiculoCreate(VeiculoBase):
    preco_brl: Decimal = Field(..., ge=0)

class VeiculoUpdate(VeiculoBase):
    preco_brl: Decimal = Field(..., ge=0)



class VeiculoPatch(BaseModel):
    marca: str | None = Field(None, min_length=1, max_length=80)
    modelo: str | None = Field(None, min_length=1, max_length=120)
    ano: int | None = Field(None, ge=1900, le=datetime.now().year + 1) # +1 pq pode ter veículos com ano acima do ano atual
    cor: str | None = Field(None, min_length=1, max_length=50)
    placa: str | None = Field(None, min_length=7, max_length=10)
    preco_brl: Decimal | None = Field(None, ge=0)

    @field_validator("marca", "modelo", "cor", "placa")
    @classmethod
    def strip_optional_text(cls, value: str | None) -> str | None:
        return value.strip() if value is not None else value

    @field_validator("placa")
    @classmethod
    def normalize_optional_plate(cls, value: str | None) -> str | None:
        return value.strip().upper() if value is not None else value


class VeiculoOut(BaseModel):
    id: str
    marca: str
    modelo: str
    ano: int
    cor: str
    placa: str
    preco_usd: Decimal
    ativo: bool

    model_config = {"from_attributes": True}


class VeiculoPage(BaseModel):
    items: list[VeiculoOut]
    page: int
    size: int
    total: int


class RelatorioPorMarca(BaseModel):
    marca: str
    quantidade: int


SortField = Literal["marca", "modelo", "ano", "cor", "preco_usd", "created_at"]
SortDirection = Literal["asc", "desc"]
