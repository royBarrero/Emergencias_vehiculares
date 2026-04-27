from google import genai
from google.genai import types
import requests
from app.config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)


def transcribir_y_mejorar_audio(url_audio: str) -> str:
    try:
        response = requests.get(url_audio)
        if response.status_code != 200:
            return None

        audio_bytes = response.content

        prompt = """Eres un asistente técnico automotriz. 
        El siguiente audio es de un conductor describiendo una falla en su vehículo.
        Por favor:
        1. Transcribe exactamente lo que dice
        2. Reformula la descripción en términos técnicos claros y profesionales
        3. Responde en este formato:
        
        TRANSCRIPCIÓN: [lo que dijo el conductor]
        DIAGNÓSTICO PRELIMINAR: [descripción técnica clara para el mecánico]
        """

        resultado = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                prompt,
                types.Part.from_bytes(data=audio_bytes, mime_type="audio/m4a")
            ]
        )
        return resultado.text

    except Exception as e:
        print(f"Error en IA audio: {e}")
        return None


def analizar_imagen_vehiculo(url_imagen: str) -> str:
    try:
        response = requests.get(url_imagen)
        if response.status_code != 200:
            return None

        imagen_bytes = response.content

        prompt = """Eres un mecánico experto. Analiza esta imagen de un vehículo con problemas.
        Describe brevemente:
        1. Qué problema visual puedes identificar
        2. Posible causa
        3. Urgencia (baja/media/alta)
        
        Responde de forma concisa y profesional en español.
        """

        resultado = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                prompt,
                types.Part.from_bytes(data=imagen_bytes, mime_type="image/jpeg")
            ]
        )
        return resultado.text

    except Exception as e:
        print(f"Error en IA imagen: {e}")
        return None