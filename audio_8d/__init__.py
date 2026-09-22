bl_info = {
    "name": "Sistema de reproducción de Audio 8D (TFG)",
    "author": "Carlos Rueda Martínez",
    "version": (1, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > Mi TFG",
    "description": "Herramienta de separación y espacialización 8D para archivos de audio .mp3, .wav, .flac",
    "category": "3D View",
}

#Paquete principal de integración con Blender y los módulos 
import bpy
from . import dependencias


#Si las dependencias no están instaladas iniciamos los módulos necesarios hasta para operar correctamente
if dependencias.MODULES_AVAILABLE:
    from .core import properties
    from . import operators
    from . import ui
    modules = (
        dependencias,
        properties,
        operators,
        ui,
    )
else:
    modules = (
        dependencias,
    )

#Registro y desregistro de todas las clases del addon
def register():
    """Registra todos los módulos del addon"""
    for module in modules:
        if hasattr(module, "register"):
            module.register()


def unregister():
    """Desregistra todos los módulos del addon"""
    for module in modules:
        if hasattr(module, "unregister"):
            module.unregister()

if __name__ == "__main__":
    register()