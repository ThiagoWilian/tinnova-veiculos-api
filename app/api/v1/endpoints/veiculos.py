from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_admin
from app.core.database import get_db
from app.models.user import User
from app.schemas.veiculo import (
    RelatorioPorMarca,
    SortDirection,
    SortField,
    VeiculoCreate,
    VeiculoOut,
    VeiculoPage,
    VeiculoPatch,
    VeiculoUpdate,
)
from app.services.veiculo_service import veiculo_service

router = APIRouter(prefix="/veiculos", tags=["veiculos"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=VeiculoPage)
def list_veiculos(
    marca: str | None = None,
    ano: int | None = None,
    cor: str | None = None,
    min_preco: Decimal | None = Query(None, alias="minPreco", ge=0),
    max_preco: Decimal | None = Query(None, alias="maxPreco", ge=0),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    sort_by: SortField = "created_at",
    sort_dir: SortDirection = "desc",
    db: Session = Depends(get_db),
    ) -> VeiculoPage:
        items, total = veiculo_service.list(
            db, marca, ano, cor, min_preco, max_preco, page, size, sort_by, sort_dir
        )
        return VeiculoPage(items=items, page=page, size=size, total=total)


@router.get("/relatorios/por-marca", response_model=list[RelatorioPorMarca])
def report_by_marca(
    db: Session = Depends(get_db),
    ) -> list[RelatorioPorMarca]:
        return [
            RelatorioPorMarca(marca=marca, quantidade=quantidade)
            for marca, quantidade in veiculo_service.report_by_marca(db)
        ]


@router.get("/{veiculo_id}", response_model=VeiculoOut)
def get_veiculo(
    veiculo_id: str,
    db: Session = Depends(get_db),
    ) -> VeiculoOut:
        return veiculo_service.get(db, veiculo_id)


@router.post("", dependencies=[Depends(require_admin)], response_model=VeiculoOut, status_code=status.HTTP_201_CREATED)
def create_veiculo(
    payload: VeiculoCreate,
    db: Session = Depends(get_db),
    ) -> VeiculoOut:
        return veiculo_service.create(db, payload)


@router.put("/{veiculo_id}", dependencies=[Depends(require_admin)], response_model=VeiculoOut)
def update_veiculo(
    veiculo_id: str,
    payload: VeiculoUpdate,
    db: Session = Depends(get_db),
    ) -> VeiculoOut:
        return veiculo_service.update(db, veiculo_id, payload)


@router.patch("/{veiculo_id}", dependencies=[Depends(require_admin)], response_model=VeiculoOut)
def patch_veiculo(
    veiculo_id: str,
    payload: VeiculoPatch,
    db: Session = Depends(get_db),
    ) -> VeiculoOut:
        try:
            return veiculo_service.patch(db, veiculo_id, payload)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"code": "VALIDATION_ERROR", "message": str(exc)},
            ) from exc


@router.delete(
    "/{veiculo_id}", 
    dependencies=[Depends(require_admin)], 
    status_code=status.HTTP_204_NO_CONTENT)
def delete_veiculo(veiculo_id: str, db: Session = Depends(get_db)) -> Response:
    veiculo_service.delete(db, veiculo_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)