import bpy
from . import panel_exportacion, panel_modificacion, panel_separacion_ia

#Inclusión de todas las clases UI
classes = (
    panel_separacion_ia.AUDIO8D_PT_panel_separacion_ia,
    panel_modificacion.AUDIO8D_PT_panel_control,
    panel_exportacion.AUDIO8D_PT_panel_exportacion,
)

#Registro/desregistro
def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)