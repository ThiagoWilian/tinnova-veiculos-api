import uuid
from decimal import Decimal
from sqlalchemy import Boolean, Index, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin

# TimestampMixin: cria automaticamente created_at e updated_at
class Veiculo(TimestampMixin, Base):
    __tablename__ = "veiculos"
    __table_args__ = (
        Index("ix_veiculos_marca_ano_cor", "marca", "ano", "cor"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    marca: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    modelo: Mapped[str] = mapped_column(String(120), nullable=False)
    ano: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    cor: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    placa: Mapped[str] = mapped_column(String(10), unique=True, index=True, nullable=False)
    preco_usd: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)