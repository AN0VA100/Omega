from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import View

from .models import Rol


"""
Clases de permisos RBAC para proteger los endpoints de la API RESTful.
"""



def _tiene_rol(request: Request, roles_permitidos: list[str]) -> bool:
    """Función auxiliar que verifica autenticación, actividad y pertenencia al rol."""
    user = request.user
    if not (user and user.is_authenticated and user.estado_activo):
        return False
    if user.is_superuser:
        return True
    return bool(user.rol and user.rol.nombre_rol in roles_permitidos)


class IsAdministradorGeneral(BasePermission):
    """Permite acceso exclusivo al rol Administrador General."""
    message = "No tiene permisos para realizar esta acción. Se requiere perfil Administrador General."

    def has_permission(self, request: Request, view: View) -> bool:
        return _tiene_rol(request, [Rol.ADMIN_GENERAL])


class IsBodega(BasePermission):
    """Permite el acceso a los roles Bodega/Logística y Administrador General."""
    message = "No tiene permisos para realizar esta acción. Se requiere perfil Bodega/Logística."

    def has_permission(self, request: Request, view: View) -> bool:
        return _tiene_rol(request, [Rol.BODEGA, Rol.ADMIN_GENERAL])


class IsTecnico(BasePermission):
    """Permite el acceso exclusivo al rol Técnico (Portal Móvil PWA)."""
    message = "No tiene permisos para realizar esta acción. Se requiere perfil Técnico."

    def has_permission(self, request: Request, view: View) -> bool:
        return _tiene_rol(request, [Rol.TECNICO])

class IsAdminOAdministracion(BasePermission):
    """Permite gestionar usuarios a Administrador General y Administración."""
    message = "No tiene permisos para gestionar usuarios. Se requiere perfil Administrador General o Administración."

    def has_permission(self, request: Request, view: View) -> bool:
        return _tiene_rol(request, [Rol.ADMIN_GENERAL, Rol.ADMINISTRACION])