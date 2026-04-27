from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.routers.auth import get_current_user
from app.models.pago import Pago
from app.schemas.pago import PagoCreate, PagoOut

router = APIRouter(prefix="/pagos", tags=["Pagos"])


@router.post("/", response_model=PagoOut, status_code=201)
def registrar_pago(datos: PagoCreate, db: Session = Depends(get_db),
                   current_user=Depends(get_current_user)):
    # Verificar si ya existe pago para esta emergencia
    existe = db.query(Pago).filter(Pago.id_emergencia == datos.id_emergencia).first()
    if existe:
        raise HTTPException(status_code=400, detail="Ya existe un pago para esta emergencia")

    comision = round(datos.monto_total * 0.10, 2)
    monto_neto = round(datos.monto_total - comision, 2)

    pago = Pago(
        id_emergencia=datos.id_emergencia,
        monto_total=datos.monto_total,
        comision=comision,
        monto_neto=monto_neto,
        metodo_pago=datos.metodo_pago,
    )
    db.add(pago)
    db.commit()
    db.refresh(pago)
    return pago


@router.get("/emergencia/{id_emergencia}", response_model=PagoOut)
def obtener_pago_emergencia(id_emergencia: int, db: Session = Depends(get_db),
                             current_user=Depends(get_current_user)):
    pago = db.query(Pago).filter(Pago.id_emergencia == id_emergencia).first()
    if not pago:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    return pago