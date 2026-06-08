from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.routers.auth import get_current_user
from app.models.pago import Pago, EstadoPagoEnum, MetodoPagoEnum
from app.models.emergencia import Emergencia, EstadoEmergenciaEnum
import stripe
import os

router = APIRouter(prefix="/stripe", tags=["Stripe"])

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@router.post("/crear-intent/{id_emergencia}")
def crear_payment_intent(
    id_emergencia: int,
    datos: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    emergencia = db.query(Emergencia).filter(
        Emergencia.id_emergencia == id_emergencia
    ).first()
    if not emergencia:
        raise HTTPException(status_code=404, detail="Emergencia no encontrada")

    monto = datos.get("monto_total")
    if not monto:
        raise HTTPException(status_code=400, detail="Monto requerido")

    # Stripe maneja centavos
    monto_centavos = int(float(monto) * 100)

    intent = stripe.PaymentIntent.create(
        amount=monto_centavos,
        currency="usd",
        metadata={
            "id_emergencia": id_emergencia,
            "id_conductor": str(emergencia.id_conductor)
        }
    )

    return {
        "client_secret": intent.client_secret,
        "payment_intent_id": intent.id,
        "monto": monto,
        "publishable_key": os.getenv("STRIPE_PUBLISHABLE_KEY")
    }

@router.post("/confirmar/{id_emergencia}")
def confirmar_pago(
    id_emergencia: int,
    datos: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    payment_intent_id = datos.get("payment_intent_id")
    monto_total = float(datos.get("monto_total", 0))
    metodo = datos.get("metodo_pago", "tarjeta")

    # Verificar con Stripe
    try:
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        if intent.status != "succeeded":
            raise HTTPException(status_code=400, detail="Pago no completado")
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Calcular comisión 10%
    comision = round(monto_total * 0.10, 2)
    monto_neto = round(monto_total - comision, 2)

    # Registrar pago en BD
    pago_existente = db.query(Pago).filter(
        Pago.id_emergencia == id_emergencia
    ).first()

    if pago_existente:
        pago_existente.estado = EstadoPagoEnum.completado
        pago_existente.monto_total = monto_total
        pago_existente.comision = comision
        pago_existente.monto_neto = monto_neto
    else:
        pago = Pago(
            id_emergencia=id_emergencia,
            monto_total=monto_total,
            comision=comision,
            monto_neto=monto_neto,
            metodo_pago=MetodoPagoEnum.qr if metodo == "qr" else MetodoPagoEnum.efectivo,
            estado=EstadoPagoEnum.completado
        )
        db.add(pago)

    db.commit()

    return {
        "mensaje": "Pago registrado exitosamente",
        "monto_total": monto_total,
        "comision": comision,
        "monto_neto": monto_neto,
        "comprobante": {
            "id_emergencia": id_emergencia,
            "payment_intent_id": payment_intent_id,
            "estado": "completado"
        }
    }

@router.post("/confirmar-efectivo/{id_emergencia}")
def confirmar_pago_efectivo(
    id_emergencia: int,
    datos: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    monto_total = float(datos.get("monto_total", 0))
    comision = round(monto_total * 0.10, 2)
    monto_neto = round(monto_total - comision, 2)

    pago_existente = db.query(Pago).filter(
        Pago.id_emergencia == id_emergencia
    ).first()

    if pago_existente:
        pago_existente.estado = EstadoPagoEnum.completado
        pago_existente.monto_total = monto_total
        pago_existente.comision = comision
        pago_existente.monto_neto = monto_neto
        pago_existente.metodo_pago = MetodoPagoEnum.efectivo
    else:
        pago = Pago(
            id_emergencia=id_emergencia,
            monto_total=monto_total,
            comision=comision,
            monto_neto=monto_neto,
            metodo_pago=MetodoPagoEnum.efectivo,
            estado=EstadoPagoEnum.completado
        )
        db.add(pago)

    db.commit()
    return {
        "mensaje": "Pago en efectivo registrado",
        "monto_total": monto_total,
        "comision": comision,
        "monto_neto": monto_neto,
    }