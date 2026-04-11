from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.usuario import Usuario
from app.models.recuperacion import RecuperacionContrasena
from app.services.auth_service import encriptar_contrasena
import secrets

def solicitar_recuperacion(db: Session, correo: str):
    usuario = db.query(Usuario).filter(Usuario.correo == correo).first()
    if not usuario:
        return None

    # Generar token único
    token = secrets.token_urlsafe(32)
    expiracion = datetime.now() + timedelta(hours=1)

    recuperacion = RecuperacionContrasena(
        id_usuario=usuario.id_usuario,
        token=token,
        fecha_expiracion=expiracion,
        usado=False
    )
    db.add(recuperacion)
    db.commit()

    # En producción aquí se enviaría el correo
    # Por ahora retornamos el token directamente para pruebas
    return token

def verificar_token(db: Session, token: str):
    recuperacion = db.query(RecuperacionContrasena).filter(
        RecuperacionContrasena.token == token,
        RecuperacionContrasena.usado == False,
        RecuperacionContrasena.fecha_expiracion > datetime.now()
    ).first()

    if not recuperacion:
        return False
    return True

def cambiar_contrasena(db: Session, token: str, nueva_contrasena: str):
    recuperacion = db.query(RecuperacionContrasena).filter(
        RecuperacionContrasena.token == token,
        RecuperacionContrasena.usado == False,
        RecuperacionContrasena.fecha_expiracion > datetime.now()
    ).first()

    if not recuperacion:
        return False

    # Cambiar contraseña
    usuario = db.query(Usuario).filter(
        Usuario.id_usuario == recuperacion.id_usuario
    ).first()

    usuario.contrasena = encriptar_contrasena(nueva_contrasena)

    # Marcar token como usado
    recuperacion.usado = True

    db.commit()
    return True