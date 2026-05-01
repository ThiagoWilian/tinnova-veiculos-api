from decimal import Decimal, ROUND_HALF_EVEN
from sqlalchemy.orm import Session
from app.core.errors import NotFoundError, VehiclePlateConflict
from app.models.veiculo import Veiculo
from app.repositories.veiculo_repository import veiculo_repository
from app.schemas.veiculo import SortDirection, SortField, VeiculoCreate, VeiculoPatch, VeiculoUpdate
from app.services.cotacao_service import cotacao_service


class VeiculoService:
    def _preco_brl_to_usd(self, preco_brl: Decimal) -> Decimal:
        """
        Converte o preço em real para dólar.
        Args:
            preco_brl: O preço em real.
        Returns:
            O preço em dólar.
        """
        rate = cotacao_service.usd_brl()
        # quantize - arredonda o resultado para 2 casas decimais
        # ROUND_HALF_EVEN - arredonda para o mais próximo. Se o número for 0.5, arredonda para o parmais próximo
        return (preco_brl / rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)

    def _ensure_unique_plate(self, db: Session, placa: str, ignore_id: str | None = None) -> None:
        """
        Verifica se a placa é única.
        Args:
            db: A sessão do banco de dados.
            placa: A placa do veículo.
            ignore_id: O ID do veículo a ser ignorado. 
        """
        existing = veiculo_repository.get_by_placa(db, placa)
        if existing is not None and existing.id != ignore_id:
            raise VehiclePlateConflict()

    def create(self, db: Session, payload: VeiculoCreate) -> Veiculo:
        """
        Cria um novo veículo.
        Args:
            db: A sessão do banco de dados.
            payload: O payload do veículo.
        Returns:
            O veículo criado.
        """
        self._ensure_unique_plate(db, payload.placa)
        veiculo = Veiculo(
            marca=payload.marca,
            modelo=payload.modelo,
            ano=payload.ano,
            cor=payload.cor,
            placa=payload.placa,
            preco_usd=self._preco_brl_to_usd(payload.preco_brl),
        )
        return veiculo_repository.create(db, veiculo)

    def list_veiculos(
        self,
        db: Session,
        marca: str | None,
        ano: int | None,
        cor: str | None,
        min_preco: Decimal | None,
        max_preco: Decimal | None,
        page: int,
        size: int,
        sort_by: SortField,
        sort_dir: SortDirection,
    ) -> tuple[list[Veiculo], int]:
        return veiculo_repository.list_veiculos(
            db, marca, ano, cor, min_preco, max_preco, page, size, sort_by, sort_dir
        )

    def get(self, db: Session, veiculo_id: str) -> Veiculo:
        """
        Obtém um veículo ativo pelo ID.
        Args:
            db: A sessão do banco de dados.
            veiculo_id: O ID do veículo.
        Returns:
            O veículo ativo.
        """
        veiculo = veiculo_repository.get_active(db, veiculo_id)
        if veiculo is None:
            raise NotFoundError("Veículo não encontrado")
        return veiculo

    def update(self, db: Session, veiculo_id: str, payload: VeiculoUpdate) -> Veiculo:
        """
        Atualiza um veículo.
        Args:
            db: A sessão do banco de dados.
            veiculo_id: O ID do veículo.
            payload: O payload do veículo.
        Returns:
            O veículo atualizado.
        """
        veiculo = self.get(db, veiculo_id)
        self._ensure_unique_plate(db, payload.placa, ignore_id=veiculo.id)
        veiculo.marca = payload.marca
        veiculo.modelo = payload.modelo
        veiculo.ano = payload.ano
        veiculo.cor = payload.cor
        veiculo.placa = payload.placa
        veiculo.preco_usd = self._preco_brl_to_usd(payload.preco_brl)
        return veiculo_repository.save(db, veiculo)

    def patch(self, db: Session, veiculo_id: str, payload: VeiculoPatch) -> Veiculo:
        """
        Atualiza um veículo parcialmente.
        Args:
            db: A sessão do banco de dados.
            veiculo_id: O ID do veículo.
            payload: O payload do veículo.
        Returns:
            O veículo atualizado.
        """
        update_data = payload.model_dump(exclude_unset=True)
        if not update_data:
            raise ValueError("Informe ao menos um campo para atualizacao")

        veiculo = self.get(db, veiculo_id)
        if "placa" in update_data:
            self._ensure_unique_plate(db, update_data["placa"], ignore_id=veiculo.id)

        preco_brl = update_data.pop("preco_brl", None)
        for field, value in update_data.items():
            setattr(veiculo, field, value)
        if preco_brl is not None:
            veiculo.preco_usd = self._preco_brl_to_usd(preco_brl)
        return veiculo_repository.save(db, veiculo)

    def delete(self, db: Session, veiculo_id: str) -> None:
        """
        Deleta um veículo.
        Args:
            db: A sessão do banco de dados.
            veiculo_id: O ID do veículo.
        """
        veiculo = self.get(db, veiculo_id)
        veiculo.ativo = False
        veiculo_repository.save(db, veiculo)

    def report_by_marca(self, db: Session) -> list[tuple[str, int]]:
        """
        Gera um relatório de veículos por marca.
        Args:
            db: A sessão do banco de dados.
        Returns:
            Uma lista de tuplas contendo a marca e o número de veículos.
        """
        return veiculo_repository.report_by_marca(db)


veiculo_service = VeiculoService()