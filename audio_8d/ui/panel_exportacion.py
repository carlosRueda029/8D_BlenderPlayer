import bpy
import os

class AUDIO8D_PT_panel_exportacion(bpy.types.Panel):
    """Vista (Panel UI) para la exportación de la pista 8D."""

    bl_idname = "AUDIO8D_PT_panel_exportacion"
    bl_label = "3. Exportar pista binaural"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Audio 8D"

    def draw(self, context):
            layout = self.layout
            propiedades = context.scene.audio8d
            
            #Mensaje que aparece si no hemos generado una pista binaural
            if not propiedades.pista_procesada:
                layout.label(text="Procesa una pista binaural para poder guardar la pista 8D.", icon='INFO')

            #Indicador de la acción que realiza el panel
            layout.label(text="Selecciona la carpeta donde quieras guardar la pista", 
                         icon='FILE_FOLDER')
            
            #Creamos la columna y le asignamos la condición de bloqueo
            col_principal = layout.column()
            col_principal.enabled = propiedades.pista_procesada
            
            col_principal.separator()

            #Operador exportar pista
            col_principal.operator("audio8d.exportar_pista", 
                                icon='SOUND',
                                text="Exportar Pista Binaural")