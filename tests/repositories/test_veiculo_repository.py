from decimal import Decimal

import pytest
from sqlalchemy.orm import Session

from app.core.errors import VehiclePlateConflict
from app.models.veiculo import Veiculo
from app.repositories.veiculo_repository import veiculo_repository


def test_repository_filters_and_unique_plate(db_session: Session) -> None:
    veiculo_repository.create(
        db_session,
        Veiculo(
            marca="Toyota",
            modelo="Corolla",
            ano=2022,
            cor="Prata",
            placa="ABC1D23",
            preco_usd=Decimal("20000.00"),
        ),
    )

    items, total = veiculo_repository.list_veiculos(
        db_session,
        marca="Toyota",
        ano=2022,
        cor="Prata",
        min_preco=Decimal("10000"),
        max_preco=Decimal("25000"),
    )

    assert total == 1
    assert items[0].placa == "ABC1D23"

    with pytest.raises(VehiclePlateConflict):
        veiculo_repository.create(
            db_session,
            Veiculo(
                marca="Toyota",
                modelo="Etios",
                ano=2021,
                cor="Branco",
                placa="ABC1D23",
                preco_usd=Decimal("12000.00"),
            ),
        )


def test_repository_soft_delete_hides_vehicle(db_session: Session) -> None:
    veiculo = veiculo_repository.create(
        db_session,
        Veiculo(
            marca="Honda",
            modelo="Civic",
            ano=2020,
            cor="Prata",
            placa="HIJ7K89",
            preco_usd=Decimal("24000.00"),
        ),
    )
    veiculo.ativo = False
    veiculo_repository.save(db_session, veiculo)

    items, total = veiculo_repository.list_veiculos(db_session)

    assert total == 0
    assert items == []
