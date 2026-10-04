from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.custom_errors import ProveedorYaExisteError, ProveedorNombreInvalidoError, ProveedorNoEncontradoError
from app.models.proveedor_model import Proveedor
from app.schemas.proveedor_schema import ProveedorCreate
from app.repositories.proveedor_repository import ProveedorRepository
from app.utils.messages import Mensajes

class ProveedorService:
  def __init__(self, db: AsyncSession):
    self.db = db
    self.repo = ProveedorRepository(db)

  async def registrar_proveedor(self, proveedor: ProveedorCreate) -> None:    
    nombre = proveedor.nombre.strip().upper()
    
    if len(nombre) == 0:
      raise ProveedorNombreInvalidoError(Mensajes.PROVEEDOR_NOMBRE_VACIO)    
    
    existe = await self.repo.obtener_por_nombre(nombre)
      
    if existe:
      raise ProveedorYaExisteError(nombre)    
    
    nuevo_proveedor = await self.repo.registrar(nombre)   
    return nuevo_proveedor

  async def obtener_todos(self, skip: int = 0, limit: int = 100) -> list[Proveedor]:
    return await self.repo.obtener_todos(skip=skip, limit=limit)

  async def obtener_por_nombre(self, nombre: str) -> Proveedor | None:
    return await self.repo.obtener_por_nombre(nombre)  

  async def obtener_por_id(self, id: int) -> Proveedor | None:
    proveedor = await self.repo.obtener_por_id(id)   
    return proveedor 

  async def actualizar_proveedor(self, id: int, nuevo_nombre: str) -> Proveedor:
    nombre_limpio = nuevo_nombre.strip().upper()
    
    if not nombre_limpio:
      raise ProveedorNombreInvalidoError()

    # Verificamos si el proveedor existe
    proveedor_actual = await self.repo.obtener_por_id(id)
    if not proveedor_actual:
      raise ProveedorNoEncontradoError()      

    #  VALIDACIÓN DE UNICIDAD: Solo si el nombre ha cambiado
    if nombre_limpio != proveedor_actual.nombre:
      existe_otro_proveedor = await self.repo.obtener_por_nombre(nombre_limpio)
      if existe_otro_proveedor:
        raise ProveedorYaExisteError(nombre_limpio)

    # Si pasa las validaciones, llamamos al repo para que actualice y haga commit
    return await self.repo.actualizar(id, nombre_limpio)