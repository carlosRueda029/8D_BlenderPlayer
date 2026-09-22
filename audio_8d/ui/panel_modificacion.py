import bpy

class AUDIO8D_PT_panel_control(bpy.types.Panel):
    """Panel que controla qué pista se está modificando y abarca sus propiedades de trayectoria"""
    bl_label = "2. Modificación de trayectorias"
    bl_idname = "AUDIO8D_PT_panel_control"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Audio 8D'

    def draw(self, context):
        layout = self.layout
        propiedades = context.scene.audio8d

        #1. Mensaje de advertencia si la pista base no ha sido procesada
        if not propiedades.pista_procesada_ia:
            layout.label(text="Selecciona una pista para habilitar los controles de modificación.", icon='INFO')

        #2. Columna para todos los paneles que se añadirán
        col_principal = layout.column()
        col_principal.enabled = propiedades.pista_procesada_ia

        #2. Selector de las cuatro subpistas
        row_tabs = col_principal.row()
        row_tabs.prop(propiedades, "pista_activa", expand=True)

        #3. Determinar cuál de ellas está activa para mostrar el panel de configuración individual
        activa = propiedades.pista_activa
        
        if activa == 'VOCALS':
            subpista = propiedades.vocals
            icono = 'USER'
            nombre = "Vocals"
        elif activa == 'DRUMS':
            subpista = propiedades.drums
            icono = 'STRANDS'
            nombre = "Drums"
        elif activa == 'BASS':
            subpista = propiedades.bass
            icono = 'MATCUBE'
            nombre = "Bass"
        else:
            subpista = propiedades.other
            icono = 'SOUND'
            nombre = "Other"

        #4. Muestra las propiedades de la trayectoria de la subpista activa
        box = col_principal.box()
        
        #5. Cabecera con el nombre de la subpista
        row_cabecera = box.row()
        row_cabecera.label(text=nombre, icon=icono)
        row_color = row_cabecera.row()
        row_color.enabled = False 
        row_color.prop(subpista, "color_ui", text="")

        #6. Muestra de las propiedades dinámicas según la trayectoria
        box.prop(subpista, "tipo_trayectoria", text="Trayectoria")

        if subpista.tipo_trayectoria == 'ESTATICA':
            col = box.column(align=True)
            col.prop(subpista, "distancia")
            col.prop(subpista, "azimut")
            col.prop(subpista, "elevacion")
        else:
            col = box.column(align=True)
            col.prop(subpista, "distancia")
            col.prop(subpista, "azimut")
            col.prop(subpista, "elevacion")
            col.prop(subpista, "resolucion_espacial")
            col.prop(subpista, "inclinacion_orbita")

        col_principal.separator()
        row_boton = col_principal.row()

        #Operador -> Procesar audio
        row_boton.operator("audio8d.procesar_dsp", 
                        text="Procesar Audio 8D", 
                        icon='PLAY_SOUND')
