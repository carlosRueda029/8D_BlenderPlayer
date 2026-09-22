import bpy
from ..utils import generacion_trayectorias

#Trigger para actualizar las propiedades que se necesiten
def trigger_actualizacion_trayectoria(self, context): 
    generacion_trayectorias.actualizar_trayectoria_ui(self, context)

#Propiedades de las subpistas
class PropiedadesSubpistas(bpy.types.PropertyGroup):
    """Modelo de datos específico para cada una de las subpistas. 
    Almacena el estado de las variables acústicas y espaciales (azimut, elevación, distancia), 
    así como el tipo de trayectoria y la resolución espacial que necesitará leer el motor DSP.

    Args:
        bpy (module): Módulo principal de la API nativa de Blender. Se utiliza para heredar 
        la clase base `bpy.types.PropertyGroup`, permitiendo que estas variables 
        se integren y guarden de forma persistente en la memoria del proyecto (RNF-03).
    """
    
    #Metadatos de las subpistas
    ruta_stem: bpy.props.StringProperty(name="Ruta", subtype='FILE_PATH')
    audio: bpy.props.PointerProperty(name="Audio", type=bpy.types.Sound)
    color_ui: bpy.props.FloatVectorProperty(name="Color", subtype='COLOR', size=4, default=(1.0, 1.0, 1.0, 1.0))

    #Posición esférica de las subpistas
    distancia: bpy.props.FloatProperty(name="Distancia (r)", 
                                       default=1.0, 
                                       min=0.1, 
                                       update=trigger_actualizacion_trayectoria)
    
    azimut: bpy.props.FloatProperty(name="Azimut (Theta)", 
                                    default=0.0, 
                                    min=0.0, 
                                    max=359.0, 
                                    step=500, 
                                    update=trigger_actualizacion_trayectoria)
    
    elevacion: bpy.props.FloatProperty(name="Elevación (Delta)", 
                                       default=0.0, 
                                       min=-90.0, 
                                       max=90.0, 
                                       step=500, 
                                       update=trigger_actualizacion_trayectoria)
    
    #Propiedades modificables de las subpistas
    tipo_trayectoria: bpy.props.EnumProperty(
        name="Tipo de Trayectoria",
        description="Selecciona el patrón de movimiento 8D para esta pista",
        items=[
            ('ESTATICA', "Estática", "La pista no se mueve"),
            ('CIRCULAR', "Circular", "Orbita en círculo alrededor del oyente"),
            ('CUADRADA', "Cuadrada", "Orbita con forma de cuadrado alrededor del oyente"),
        ],
        default='CIRCULAR',
        update=trigger_actualizacion_trayectoria)
    
    resolucion_espacial: bpy.props.IntProperty(
        name="Resolución Espacial",
        description="Cada cuántos frames de Blender se genera y calcula un vértice",
        default=30,
        min=1,
        max=60,
        update=trigger_actualizacion_trayectoria
    )

    #Propiedades específicas de cada una de las órbitas
    inclinacion_orbita: bpy.props.FloatProperty(
        name="Inclinación de la Órbita",
        description="Grados de inclinación del plano de rotación",
        default=0.0,
        min=-90.0,
        max=90.0,
        step=500,
        update=trigger_actualizacion_trayectoria
    )


#Propiedades generales
class Audio8DProperties(bpy.types.PropertyGroup):
    """Modelo de datos general del proyecto (El 'Modelo' en la arquitectura MVC).
    Actúa como la 'fuente de la verdad' centralizada, gestionando las variables globales temporales 
    y de entorno (FPS, duración, escala) y agrupando los punteros a los submodelos de las cuatro 
    pistas separadas (vocals, bass, drums, other).

    Args:
        bpy (module): Módulo principal de la API nativa de Blender. Se utiliza para heredar 
        la clase base `bpy.types.PropertyGroup`, lo que convierte a esta clase en 
        un contenedor registrable y accesible globalmente desde el contexto (`bpy.context.scene`).
    """

    #Metadatos de la pista base
    nombre_original: bpy.props.StringProperty(name="Nombre pista orignal", subtype="FILE_NAME")
    ruta_original: bpy.props.StringProperty(name="Pista original", subtype='FILE_PATH')
    carpeta_destino: bpy.props.StringProperty(name="Carpeta destino", subtype='FILE_PATH')

    #Datos de la duración y frecuencia de la pista base
    duracion_segundos: bpy.props.FloatProperty(name="Duración (s)", default=0.0)
    total_frames: bpy.props.IntProperty(name="Número de frames", default=0)
    fps_escena: bpy.props.IntProperty(name="FPS de la escena", default=30)
    frecuencia_muestreo: bpy.props.FloatProperty(
        name="Frecuencia de Muestreo",
        description="Frecuencia de muestreo global para el procesamiento DSP",
        default=44100.0,
        min=0.0
    )

    #Modelo de datos de cada una de las subpistas
    vocals: bpy.props.PointerProperty(type=PropiedadesSubpistas)
    drums: bpy.props.PointerProperty(type=PropiedadesSubpistas)
    bass: bpy.props.PointerProperty(type=PropiedadesSubpistas)
    other: bpy.props.PointerProperty(type=PropiedadesSubpistas)

    #Determina que pista está activa en el panel de propiedades
    pista_activa: bpy.props.EnumProperty(
        name="Pista Activa",
        description="Selecciona qué pista editar en la Mesa de Mezclas",
        items=[
            ('VOCALS', "Vocals", "Ajustes de la voz", 'USER', 0),
            ('DRUMS', "Drums", "Ajustes de la batería", 'STRANDS', 1),
            ('BASS', "Bass", "Ajustes del bajo", 'MATCUBE', 2),
            ('OTHER', "Other", "Ajustes de otros instrumentos", 'SOUND', 3)
        ],
        default='VOCALS'
    )

    pista_procesada_ia: bpy.props.BoolProperty(
        name="Pista Procesada",
        description="Indica si la IA ha terminado de separar la canción correctamente",
        default=False
    )

    pista_procesada: bpy.props.BoolProperty(
        name="Pista Procesada",
        description="Indica si la IA ha terminado de separar la canción correctamente",
        default=False
    )

    #Variables de control de la generación del entorno
    escala: bpy.props.IntProperty(
        name="Escala de los elementos", 
        default=5,
        min=1,
        description="Factor de multiplicación visual en Blender")
    
    elevacion_base: bpy.props.FloatProperty(
        name="Elevación base",
        default=3,
        min=0.0,
        description="Altura de la cabeza del oyente respecto al suelo")
    
    


#Registro/desregistro
def register():
    """Registro de las propiedades del proyecto"""
    bpy.utils.register_class(PropiedadesSubpistas)
    bpy.utils.register_class(Audio8DProperties)

    #Anclado general
    bpy.types.Scene.audio8d = bpy.props.PointerProperty(type=Audio8DProperties)

def unregister():
    """Desregistro de las propiedades del proyecto"""

    #Eliminación de los datos de la escena
    del bpy.types.Scene.audio8d

    bpy.utils.unregister_class(Audio8DProperties)
    bpy.utils.unregister_class(PropiedadesSubpistas)