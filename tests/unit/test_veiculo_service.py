from decimal import Decimal

import pytest
from sqlalchemy.orm import Session

from app.core.errors import VehiclePlateConflict
from app.schemas.veiculo import VeiculoCreate, VeiculoPatch, VeiculoUpdate
from app.services.veiculo_service import veiculo_service


def test_service_rejects_duplicate_plate(db_session: Session) -> None:
    payload = VeiculoCreate(
        marca="Toyota",
        modelo="Corolla",
        ano=2022,
        cor="Prata",
        placa="ABC1D23",
        preco_brl=Decimal("100000.00"),
    )
    veiculo_service.create(db_session, payload)

    with pytest.raises(VehiclePlateConflict):
        veiculo_service.create(db_session, payload)


def test_service_patch_empty_payload_fails(db_session: Session) -> None:
    payload = VeiculoCreate(
        marca="Toyota",
        modelo="Corolla",
        ano=2022,
        cor="Prata",
        placa="ABC1D23",
        preco_brl=Decimal("100000.00"),
    )
    veiculo = veiculo_service.create(db_session, payload)

    with pytest.raises(ValueError):
        veiculo_service.patch(db_session, veiculo.id, VeiculoPatch())


def test_service_put_updates_all_fields(db_session: Session) -> None:
    veiculo = veiculo_service.create(
        db_session,
        VeiculoCreate(
            marca="Toyota",
            modelo="Corolla",
            ano=2022,
            cor="Prata",
            placa="ABC1D23",
            preco_brl=Decimal("100000.00"),
        ),
    )

    updated = veiculo_service.update(
        db_session,
        veiculo.id,
        VeiculoUpdate(
            marca="Honda",
            modelo="Civic",
            ano=2020,
            cor="Preto",
            placa="HIJ7K89",
            preco_brl=Decimal("125000.00"),
        ),
    )

    assert updated.marca == "Honda"
    assert updated.preco_usd == Decimal("25000.00")
