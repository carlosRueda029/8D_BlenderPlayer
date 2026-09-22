import bpy
from .. import dependencias as preferences 
class AUDIO8D_PT_panel_separacion_ia(bpy.types.Panel):
    """Vista (Panel UI) que aloja las herramientas de separación de audio en la interfaz gráfica de Blender.
    Permite al usuario interactuar con el Controlador de separación desde la barra lateral (N-Panel).

    Args:
        bpy (module): Módulo de la API de Blender. Se utiliza para heredar la clase base `bpy.types.Panel`, 
        otorgando a esta clase los métodos necesarios (`draw`) para renderizar botones y 
        textos en el visor 3D.
    """

    bl_idname = "AUDIO8D_PT_panel_separacion_ia"
    bl_label = "1. Separación IA"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Audio 8D"

    def draw(self, context):
        layout = self.layout
        
        #Si las preferencias están bien cargadas se muestra
        if preferences.MODULES_AVAILABLE:
            
            #Indicador de la acción que realiza el panel
            layout.label(text="Selecciona la pista que quieras separar en subpistas", 
                         icon='FILE_FOLDER')
            
            #Operador separar audio
            layout.separator()
            layout.operator("audio8d.separar_audio", 
                            icon='SOUND',
                            text="Seleccionar canción")