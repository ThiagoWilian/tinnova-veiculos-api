from decimal import Decimal
from sqlalchemy import Select, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.core.errors import VehiclePlateConflict
from app.models.veiculo import Veiculo
from app.schemas.veiculo import SortDirection, SortField


class VeiculoRepository:
    """
    Repositório de veículos.
    """
    sortable_fields = {
        "marca": Veiculo.marca,
        "modelo": Veiculo.modelo,
        "ano": Veiculo.ano,
        "cor": Veiculo.cor,
        "preco_usd": Veiculo.preco_usd,
        "created_at": Veiculo.created_at,
    }

    def _apply_filters(
        self,
        consulta: Select[tuple[Veiculo]],
        marca: str | None = None,
        ano: int | None = None,
        cor: str | None = None,
        min_preco: Decimal | None = None,
        max_preco: Decimal | None = None,
        ) -> Select[tuple[Veiculo]]:
        """
        Aplica filtros à query.
        Args:
            query_filtered: A query a ser aplicado os filtros.
            marca: A marca do veículo.
            ano: O ano do veículo.
            cor: A cor do veículo.
            min_preco: O preço mínimo do veículo.
            max_preco: O preço máximo do veículo.
        Returns:
            A query aplicada os filtros.
        """
        consulta = consulta.where(Veiculo.ativo.is_(True))
        if marca:
            consulta = consulta.where(func.lower(Veiculo.marca) == marca.lower())
        if ano:
            consulta = consulta.where(Veiculo.ano == ano)
        if cor:
            consulta = consulta.where(func.lower(Veiculo.cor) == cor.lower())
        if min_preco is not None:
            consulta = consulta.where(Veiculo.preco_usd >= min_preco)
        if max_preco is not None:
            consulta = consulta.where(Veiculo.preco_usd <= max_preco)
        return consulta

    def list(
        self,
        db: Session,
        marca: str | None = None,
        ano: int | None = None,
        cor: str | None = None,
        min_preco: Decimal | None = None,
        max_preco: Decimal | None = None,
        page: int = 1,
        size: int = 20,
        sort_by: SortField = "created_at",
        sort_dir: SortDirection = "desc",
        ) -> tuple[list[Veiculo], int]:
        """
        Lista veículos com filtros e ordenação.
        Args:
            db: A sessão do banco de dados.
            marca: A marca do veículo.
            ano: O ano do veículo.
            cor: A cor do veículo.
            min_preco: O preço mínimo do veículo.
            max_preco: O preço máximo do veículo.
            page: A página atual.
            size: O número de itens por página.
            sort_by: Campo de ordenação (validado por SortField).
            sort_dir: Direção da ordenação (asc/desc).
        Returns:
            Uma tupla contendo a lista de veículos e o total de veículos.
        """
        consulta = self._apply_filters(select(Veiculo), marca, ano, cor, min_preco, max_preco)
        consulta_count = self._apply_filters(select(func.count(Veiculo.id)), marca, ano, cor, min_preco, max_preco)
        total = db.execute(consulta_count).scalar_one()

        sort_column = self.sortable_fields[sort_by]
        order_by = sort_column.desc() if sort_dir == "desc" else sort_column.asc()

        items = db.execute(
            consulta.order_by(order_by).offset((page - 1) * size).limit(size)
        ).scalars().all()
        return list(items), total

    def get_active(self, db: Session, veiculo_id: str) -> Veiculo | None:
        """
        Obtém um veículo ativo pelo ID.
        Args:
            db: A sessão do banco de dados.
            veiculo_id: O ID do veículo.
        Returns:
            O veículo ativo ou None se não encontrado.
        """
        return db.execute(
            select(Veiculo).where(Veiculo.id == veiculo_id, Veiculo.ativo.is_(True))
        ).scalar_one_or_none()

    def get_by_placa(self, db: Session, placa: str) -> Veiculo | None:
        """
        Obtém um veículo pela placa.
        Args:
            db: A sessão do banco de dados.
            placa: A placa do veículo.
        Returns:
            O veículo ou None se não encontrado.
        """
        return db.execute(select(Veiculo).where(Veiculo.placa == placa)).scalar_one_or_none()

    def create(self, db: Session, veiculo: Veiculo) -> Veiculo:
        """
        Cria um novo veículo.
        Args:
            db: A sessão do banco de dados.
            veiculo: O veículo a ser criado.
        Returns:
            O veículo criado.
        """
        try:
            db.add(veiculo)
            db.commit()
            db.refresh(veiculo)
            return veiculo
        except IntegrityError as exc:
            db.rollback()
            raise VehiclePlateConflict() from exc

    def save(self, db: Session, veiculo: Veiculo) -> Veiculo:
        """
        Salva um veículo.
        Args:
            db: A sessão do banco de dados.
            veiculo: O veículo a ser salvo.
        Returns:
            O veículo salvo.
        """
        try:
            db.commit()
            db.refresh(veiculo)
            return veiculo
        except IntegrityError as exc:
            db.rollback()
            raise VehiclePlateConflict() from exc

    def report_by_marca(self, db: Session) -> list[tuple[str, int]]:
        """
        Gera um relatório de veículos por marca.
        Args:
            db: A sessão do banco de dados.
        Returns:
            Uma lista de tuplas contendo a marca e o número de veículos.
        """
        rows = db.execute(
            select(Veiculo.marca, func.count(Veiculo.id))
            .where(Veiculo.ativo.is_(True))
            .group_by(Veiculo.marca)
            .order_by(Veiculo.marca.asc())
        ).all()
        return [(row[0], row[1]) for row in rows]


veiculo_repository = VeiculoRepository()