from fastapi import Request, HTTPException
from jose import JWTError, jwt
from app.config import SECRET_KEY, ALGORITHM

async def tenant_middleware(request: Request, call_next):
    # Rutas que no necesitan tenant
    rutas_publicas = ["/auth/login", "/auth/registro", "/registro", "/docs", "/openapi.json", "/", "/estadisticas"]
    
    if any(request.url.path.startswith(ruta) for ruta in rutas_publicas):
        return await call_next(request)

    # Extraer token
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        return await call_next(request)

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        request.state.tenant_id = payload.get("tenant_id")
        request.state.id_rol = payload.get("rol")
    except JWTError:
        request.state.tenant_id = None
        request.state.id_rol = None

    return await call_next(request)