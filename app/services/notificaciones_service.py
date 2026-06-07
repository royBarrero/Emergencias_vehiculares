import firebase_admin
from firebase_admin import credentials, messaging
import os

_firebase_inicializado = False

def inicializar_firebase():
    global _firebase_inicializado
    if not _firebase_inicializado:
        cred_path = os.path.join(os.path.dirname(__file__), 'firebase-credentials.json')
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        _firebase_inicializado = True

def enviar_notificacion(fcm_token: str, titulo: str, cuerpo: str, datos: dict = {}):
    try:
        inicializar_firebase()
        message = messaging.Message(
            notification=messaging.Notification(
                title=titulo,
                body=cuerpo,
            ),
            data={k: str(v) for k, v in datos.items()},
            token=fcm_token,
        )
        response = messaging.send(message)
        print(f"Notificación enviada: {response}")
        return True
    except Exception as e:
        print(f"Error enviando notificación: {e}")
        return False
    

import requests as req
import os

def enviar_notificacion_taller(onesignal_id: str, titulo: str, cuerpo: str, datos: dict = {}):
    try:
        app_id = os.getenv("ONESIGNAL_APP_ID")
        api_key = os.getenv("ONESIGNAL_API_KEY")
        
        payload = {
            "app_id": app_id,
            "include_subscription_ids": [onesignal_id],
            "headings": {"en": titulo},
            "contents": {"en": cuerpo},
            "data": datos
        }
        
        response = req.post(
            "https://api.onesignal.com/notifications",
            json=payload,
            headers={
                "Authorization": f"Key {api_key}",
                "Content-Type": "application/json"
            }
        )
        print(f"OneSignal respuesta: {response.status_code} - {response.text}")
        return True
    except Exception as e:
        print(f"Error enviando notificación OneSignal: {e}")
        return False    