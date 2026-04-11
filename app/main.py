from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth
from app.models import usuario, rol  # <- agregar esta línea
from app.database import Base, engine
from app.routers import auth, conductores, vehiculos, recuperacion, talleres, tecnicos,roles
from app.models import usuario, rol, conductor, vehiculo, recuperacion as recuperacion_model,taller , servicio_taller, tecnico

Base.metadata.create_all(bind=engine)  

app = FastAPI(
    title="EmergenciasVial API",
    description="Backend para la plataforma de emergencias vehiculares",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(conductores.router)
app.include_router(vehiculos.router)
app.include_router(recuperacion.router)
app.include_router(talleres.router)
app.include_router(tecnicos.router)
app.include_router(roles.router)

@app.get("/")
def root():
    return {"mensaje": "Bienvenido a EmergenciasVial API"}