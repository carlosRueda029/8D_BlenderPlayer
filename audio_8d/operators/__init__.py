import bpy
from . import audio_ops

#Inclusión de todos los botones
operators = (
    audio_ops.AUDIO8D_OT_separar_audio, audio_ops.AUDIO8D_OT_procesar_dsp, audio_ops.AUDIO8D_OT_exportar_pista
)

#Registro/desregistro
def register():
    """Registro de todos los operadores del addon"""
    for cls in operators:
        bpy.utils.register_class(cls)

def unregister():
    """Registro de todos los operadores del addon"""
    for cls in reversed(operators):
        bpy.utils.unregister_class(cls)
