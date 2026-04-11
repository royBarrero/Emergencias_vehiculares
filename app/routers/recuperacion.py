from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.recuperacion import SolicitudRecuperacion, VerificarToken, CambiarContrasena
from app.services.recuperacion_service import (
    solicitar_recuperacion, verificar_token, cambiar_contrasena
)

router = APIRouter(
    prefix="/recuperacion",
    tags=["Recuperación de contraseña"]
)

@router.post("/solicitar")
def solicitar(datos: SolicitudRecuperacion, db: Session = Depends(get_db)):
    token = solicitar_recuperacion(db, datos.correo)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No existe una cuenta con ese correo"
        )
    # En producción esto no se retorna, se envía por correo
    return {
        "mensaje": "Token generado correctamente",
        "token": token
    }

@router.post("/verificar")
def verificar(datos: VerificarToken, db: Session = Depends(get_db)):
    valido = verificar_token(db, datos.token)
    if not valido:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido o expirado"
        )
    return {"mensaje": "Token válido"}

@router.post("/cambiar-contrasena")
def cambiar(datos: CambiarContrasena, db: Session = Depends(get_db)):
    resultado = cambiar_contrasena(db, datos.token, datos.nueva_contrasena)
    if not resultado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido o expirado"
        )
    return {"mensaje": "Contraseña actualizada correctamente"}