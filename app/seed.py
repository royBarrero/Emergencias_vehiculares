from app.database import SessionLocal
from app.models.rol import Rol
from app.models.usuario import Usuario
from app.models.conductor import Conductor
from app.models.taller import Taller
from app.models.servicio_taller import ServicioTaller
from app.models.tecnico import Tecnico
from app.models.vehiculo import Vehiculo
from app.models.tenant import Tenant
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def run_seed():
    db = SessionLocal()
    try:

        # ROLES
        roles = [
            Rol(id_rol=1, nombre="conductor", descripcion="Usuario conductor"),
            Rol(id_rol=2, nombre="taller", descripcion="Taller mecánico"),
            Rol(id_rol=3, nombre="tecnico", descripcion="Técnico de taller"),
            Rol(id_rol=4, nombre="admin", descripcion="Administrador"),
            Rol(id_rol=5, nombre="tenant_admin", descripcion="Administrador de red de talleres"),
        ]
        db.add_all(roles)
        db.commit()

        # USUARIOS CONDUCTORES
        u_conductor1 = Usuario(
            nombre="Carlos Mamani",
            correo="carlos@conductor.com",
            contrasena=hash_password("123456"),
            telefono="70011001",
            estado=True,
            id_rol=1
        )
        u_conductor2 = Usuario(
            nombre="Ana Perez",
            correo="ana@conductor.com",
            contrasena=hash_password("123456"),
            telefono="70022002",
            estado=True,
            id_rol=1
        )

        # USUARIOS TALLERES
        u_taller1 = Usuario(
            nombre="Taller El Motor",
            correo="motor@taller.com",
            contrasena=hash_password("123456"),
            telefono="70033003",
            estado=True,
            id_rol=2
        )
        u_taller2 = Usuario(
            nombre="Taller Santa Cruz",
            correo="santacruz@taller.com",
            contrasena=hash_password("123456"),
            telefono="70044004",
            estado=True,
            id_rol=2
        )
        u_taller3 = Usuario(
            nombre="Taller Los Equipos",
            correo="equipos@taller.com",
            contrasena=hash_password("123456"),
            telefono="70055005",
            estado=True,
            id_rol=2
        )

        # USUARIO ADMIN
        u_admin = Usuario(
            nombre="Admin Sistema",
            correo="admin@emergencias.com",
            contrasena=hash_password("123456"),
            telefono="70099009",
            estado=True,
            id_rol=4
        )
        

        db.add_all([u_conductor1, u_conductor2, u_taller1, u_taller2, u_taller3, u_admin])
        db.commit()
        u_tenant_admin1 = Usuario(
            nombre="Admin Auxilio Norte",
            correo="admin@auxilionorte.com",
            contrasena=hash_password("123456"),
            telefono="70011111",
            estado=True,
            id_rol=5
        )
        u_tenant_admin2 = Usuario(
            nombre="Admin Mecánicos Express",
            correo="admin@mecanicosexpress.com",
            contrasena=hash_password("123456"),
            telefono="70022222",
            estado=True,
            id_rol=5
        )
        db.add_all([u_tenant_admin1, u_tenant_admin2])
        db.commit()
        # CONDUCTORES
        conductor1 = Conductor(
            id_usuario=u_conductor1.id_usuario,
            licencia="LC-001122",
            direccion="Av. Banzer km 5, Santa Cruz"
        )
        conductor2 = Conductor(
            id_usuario=u_conductor2.id_usuario,
            licencia="LC-003344",
            direccion="Av. Cristo Redentor, Santa Cruz"
        )
        db.add_all([conductor1, conductor2])
        db.commit()
       
        # TENANTS
        tenant1 = Tenant(
            nombre="Auxilio Norte",
            descripcion="Red de talleres zona norte de Santa Cruz",
            estado=True
        )
        tenant2 = Tenant(
            nombre="Mecánicos Express",
            descripcion="Red de talleres express Santa Cruz",
            estado=True
        )
        db.add_all([tenant1, tenant2])
        db.commit()
        tenant1.id_usuario_admin = u_tenant_admin1.id_usuario
        tenant2.id_usuario_admin = u_tenant_admin2.id_usuario
        db.commit()
        # VEHICULOS
        vehiculos = [
            Vehiculo(
                id_conductor=conductor1.id_conductor,
                marca="Toyota",
                modelo="Corolla",
                anio=2020,
                placa="ABC-1234",
                color="Blanco",
                tipo_vehiculo="sedan"
            ),
            Vehiculo(
                id_conductor=conductor2.id_conductor,
                marca="Nissan",
                modelo="Sentra",
                anio=2019,
                placa="XYZ-5678",
                color="Negro",
                tipo_vehiculo="sedan"
            ),
        ]
        db.add_all(vehiculos)
        db.commit()

        # TALLERES (alrededor de -17.9052529, -63.2101961)
        taller1 = Taller(
            id_usuario=u_taller1.id_usuario,
            id_tenant=tenant1.id_tenant,
            nombre_taller="Taller El Motor",
            direccion="Av. Banzer km 3, Santa Cruz",
            telefono="70033003",
            latitud=-17.9010,
            longitud=-63.2150,
            estado="activo",
            calificacion_promedio=4.5
        )
        taller2 = Taller(
            id_usuario=u_taller2.id_usuario,
            id_tenant=tenant1.id_tenant,
            nombre_taller="Taller Santa Cruz",
            direccion="Radial 27, Santa Cruz",
            telefono="70044004",
            latitud=-17.9080,
            longitud=-63.2050,
            estado="activo",
            calificacion_promedio=4.2
        )
        taller3 = Taller(
            id_usuario=u_taller3.id_usuario,
            id_tenant=tenant2.id_tenant,
            nombre_taller="Taller Los Equipos",
            direccion="Av. San Martín, Santa Cruz",
            telefono="70055005",
            latitud=-17.9120,
            longitud=-63.2200,
            estado="activo",
            calificacion_promedio=4.8
        )
        db.add_all([taller1, taller2, taller3])
        db.commit()

        # SERVICIOS POR TALLER
        servicios = [
            ServicioTaller(id_taller=taller1.id_taller, nombre_servicio="Mecánica general", descripcion="Reparación general", disponible=True),
            ServicioTaller(id_taller=taller1.id_taller, nombre_servicio="Electricidad", descripcion="Sistema eléctrico", disponible=True),
            ServicioTaller(id_taller=taller1.id_taller, nombre_servicio="Grúa", descripcion="Servicio de grúa", disponible=True),
            ServicioTaller(id_taller=taller2.id_taller, nombre_servicio="Mecánica general", descripcion="Reparación general", disponible=True),
            ServicioTaller(id_taller=taller2.id_taller, nombre_servicio="Llantería", descripcion="Cambio de llantas", disponible=True),
            ServicioTaller(id_taller=taller2.id_taller, nombre_servicio="Grúa", descripcion="Servicio de grúa", disponible=True),
            ServicioTaller(id_taller=taller3.id_taller, nombre_servicio="Electricidad", descripcion="Sistema eléctrico", disponible=True),
            ServicioTaller(id_taller=taller3.id_taller, nombre_servicio="Llantería", descripcion="Cambio de llantas", disponible=True),
            ServicioTaller(id_taller=taller3.id_taller, nombre_servicio="Mecánica general", descripcion="Reparación general", disponible=True),
        ]
        db.add_all(servicios)
        db.commit()

        # TECNICOS
        u_tec1 = Usuario(nombre="Juan Quispe", correo="juan@tecnico.com", contrasena=hash_password("123456"), telefono="70066006", estado=True, id_rol=3)
        u_tec2 = Usuario(nombre="Pedro Rojas", correo="pedro@tecnico.com", contrasena=hash_password("123456"), telefono="70077007", estado=True, id_rol=3)
        u_tec3 = Usuario(nombre="Luis Vaca", correo="luis@tecnico.com", contrasena=hash_password("123456"), telefono="70088008", estado=True, id_rol=3)
        db.add_all([u_tec1, u_tec2, u_tec3])
        db.commit()

        tecnicos = [
            Tecnico(id_taller=taller1.id_taller, id_usuario=u_tec1.id_usuario, especialidad="Mecánica general", estado_disponibilidad="disponible", latitud_actual=-17.9010, longitud_actual=-63.2150),
            Tecnico(id_taller=taller2.id_taller, id_usuario=u_tec2.id_usuario, especialidad="Electricidad", estado_disponibilidad="disponible", latitud_actual=-17.9080, longitud_actual=-63.2050),
            Tecnico(id_taller=taller3.id_taller, id_usuario=u_tec3.id_usuario, especialidad="Llantería", estado_disponibilidad="disponible", latitud_actual=-17.9120, longitud_actual=-63.2200),
        ]
        db.add_all(tecnicos)
        db.commit()

        print("Seed ejecutado correctamente")

    except Exception as e:
        db.rollback()
        print(f"Error en seed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_seed()