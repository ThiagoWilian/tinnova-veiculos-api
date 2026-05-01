from decimal import Decimal

from app.core.config import get_settings
from app.core.database import SessionLocal, engine
from app.models import Base
from app.models.user import UserRole
from app.models.veiculo import Veiculo
from app.repositories.user_repository import user_repository
from app.repositories.veiculo_repository import veiculo_repository



SEEDED_VEHICLES = [
    {
        "marca": "Toyota",
        "modelo": "Corolla",
        "ano": 2022,
        "cor": "Prata",
        "placa": "TOY1A22",
        "preco_usd": Decimal("21000.00"),
    },
    {
        "marca": "Toyota",
        "modelo": "Hilux",
        "ano": 2023,
        "cor": "Branco",
        "placa": "TOY2B23",
        "preco_usd": Decimal("48000.00"),
    },
    {
        "marca": "Toyota",
        "modelo": "Yaris",
        "ano": 2021,
        "cor": "Vermelho",
        "placa": "TOY3C21",
        "preco_usd": Decimal("16000.00"),
    },
    {
        "marca": "Volkswagen",
        "modelo": "Gol",
        "ano": 2020,
        "cor": "Preto",
        "placa": "VWG1D20",
        "preco_usd": Decimal("11000.00"),
    },
    {
        "marca": "Volkswagen",
        "modelo": "Polo",
        "ano": 2022,
        "cor": "Cinza",
        "placa": "VWG2E22",
        "preco_usd": Decimal("17000.00"),
    },
    {
        "marca": "Volkswagen",
        "modelo": "T-Cross",
        "ano": 2023,
        "cor": "Azul",
        "placa": "VWG3F23",
        "preco_usd": Decimal("26000.00"),
    },
    {
        "marca": "Chevrolet",
        "modelo": "Onix",
        "ano": 2021,
        "cor": "Branco",
        "placa": "CHE1G21",
        "preco_usd": Decimal("14000.00"),
    },
    {
        "marca": "Chevrolet",
        "modelo": "Tracker",
        "ano": 2023,
        "cor": "Prata",
        "placa": "CHE2H23",
        "preco_usd": Decimal("24000.00"),
    },
    {
        "marca": "Ford",
        "modelo": "Ka",
        "ano": 2019,
        "cor": "Preto",
        "placa": "FOR1I19",
        "preco_usd": Decimal("9500.00"),
    },
    {
        "marca": "Ford",
        "modelo": "Ranger",
        "ano": 2022,
        "cor": "Vermelho",
        "placa": "FOR2J22",
        "preco_usd": Decimal("42000.00"),
    },
]


def init_db() -> None:
    Base.metadata.create_all(bind=engine)

    settings = get_settings()
    with SessionLocal() as db:
        admin = user_repository.get_by_email(db, settings.admin_email)
        if admin is None:
            user_repository.create(
                db=db,
                email=settings.admin_email,
                password=settings.admin_password,
                role=UserRole.ADMIN,
            )

        user = user_repository.get_by_email(db, settings.user_email)
        if user is None:
            user_repository.create(
                db=db,
                email=settings.user_email,
                password=settings.user_password,
                role=UserRole.USER,
            )

        for vehicle_data in SEEDED_VEHICLES:
            existing_vehicle = veiculo_repository.get_by_placa(db, vehicle_data["placa"])
            if existing_vehicle is None:
                veiculo_repository.create(db, Veiculo(**vehicle_data))


if __name__ == "__main__":
    init_db()
    print("Banco inicializado com sucesso.")
