import bpy
import os
import wave
from bpy_extras.io_utils import ImportHelper, ExportHelper
from ..core import kernel
from ..utils import cancion_base, entorno_base, exportar_pista, exportar_propiedades, exportar_timeline, generacion_trayectorias 


class AUDIO8D_OT_separar_audio(bpy.types.Operator, ImportHelper):
    """Controlador que gestiona la carga de una pista de audio estéreo y su separación 
    en subpistas mediante Inteligencia Artificial. Abre el explorador de archivos nativo, 
    invoca al núcleo de separación, actualiza el Modelo de Datos y calibra la escena 3D.

    Args:
        bpy (module): módulo principal de la API de Blender. Se utiliza para heredar la clase 
        base `bpy.types.Operator`, lo que convierte a esta clase en un Controlador ejecutable.
        
        ImportHelper (class): clase de utilidad de Blender que inyecta automáticamente la lógica
        para abrir una ventana del explorador de archivos.

    Raises:
        ValueError: Se lanza si el módulo de Inteligencia Artificial falla durante el proceso o 
        no devuelve el diccionario con las pistas generadas.
        
        Exception: Captura errores generales derivados del fallo de lectura del archivo .wav o 
        durante la generación del entorno 3D.

    Returns:
        set: Conjunto de cadenas requerido por la API de Blender que indica el estado final 
        de la ejecución. Devuelve FINISHED si el proceso y la sincronización 3D concluyen 
        con éxito, o CANCELLED si el usuario aborta o se captura un error crítico.
    """

    bl_idname = "audio8d.separar_audio"
    bl_label = "Seleccionar pista"
    bl_description = "Operador que abre el explorador, carga y separa la canción seleccionada"

    #Propiedad para filtrar archivos .wav en ImportHelper
    file_filter: bpy.props.StringProperty(
        default="*wav",
        options={'HIDDEN'},
        maxlen=255,
    )

    def execute(self, context):
        #---SELECCIÓN DE LA PISTA---
        #Cargar los datos con el explorador de archivos de Blender
        ruta = self.filepath
        context.scene.audio8d.ruta_original = ruta

        #Comprobación de la ruta y el tipo de archivo correcto
        if not ruta or not ruta.lower().endswith(".wav"):
            self.report({'ERROR'}, "Por favor, selecciona una pista de audio .WAV")
            return {'CANCELLED'}
        

        #---OBTENCIÓN DE LA FRECUENCIA DE MUESTREO---
        try:
            self.report({'INFO'}, f"Obteniendo la frecuencia de muestreo de {os.path.basename(ruta)}.")
            with wave.open(ruta, 'rb') as archivo_wav:
                frecuencia = archivo_wav.getframerate() 
                
                # Lo guardamos en el modelo de datos global
                context.scene.audio8d.frecuencia_muestreo = frecuencia
                
                self.report({'INFO'}, f"Frecuencia de muestreo detectada: {frecuencia} Hz")
                
                #Validación de la frecuencia de muestreo
                if frecuencia < 44100:
                    self.report({'WARNING'}, "La pista tiene una frecuencia inferior a 44.1kHz. La calidad espacial podría verse afectada.")

        except Exception as error_frecuencia:
            self.report({'ERROR'}, f"No se pudo leer la cabecera del WAV: {error_frecuencia}")
            return {'CANCELLED'}
        

        #---PROCESO DE SEPARACIÓN---
        self.report({'INFO'}, "Separando pista... Blender no responderá, para más información sobre el proceso abre la consola del sistema")
        print(f"[OPERADOR IA]: Solicitando separación de: {os.path.basename(ruta)}. El tiempo dependerá de las características del módulo de procesamiento y el ordenador")
        self.report({'INFO'}, f"Procesando: {ruta}")

        try:
            stems = kernel.KernelAudio8D.cargarPistaEstereo(ruta)
            
            if not stems:
                raise ValueError("El núcleo no devolvió las pistas generadas.")
            
        except Exception as error_ia:
            self.report({'ERROR'}, f"Fallo en el módulo de separación de AI, revisa el módulo: {str(error_ia)}")
            return {'CANCELLED'}


        #---ACTUALIZACIÓN DEL MODELO, ENTORNO Y GENERACIÓN DE UI---
        try:
            self.report({'INFO'}, f"Separación de {os.path.basename(ruta)} completada. Generando entorno 3D.")
            propiedades = context.scene.audio8d

            #1. Guardado de las propiedades generales (Ruta, nombre, carpeta)
            propiedades.ruta_original = ruta
            propiedades.nombre_original = os.path.basename(ruta)

            carpeta_destino = os.path.dirname(stems["vocals"])
            propiedades.carpeta_destino = carpeta_destino

            #2. Ruta y audio de las pistas separadas (vocals, drums, bass y other)
            propiedades.vocals.ruta_stem = stems['vocals']
            propiedades.vocals.audio = bpy.data.sounds.load(stems['vocals'])

            propiedades.drums.ruta_stem = stems['drums']
            propiedades.drums.audio = bpy.data.sounds.load(stems['drums'])

            propiedades.bass.ruta_stem = stems['bass']
            propiedades.bass.audio = bpy.data.sounds.load(stems['bass'])

            propiedades.other.ruta_stem = stems['other']
            propiedades.other.audio = bpy.data.sounds.load(stems['other'])

            self.report({'INFO'}, f"Pistas separadas y guardadas en la ruta: {carpeta_destino}")

            cancion_base.obtener_datos_base(context, propiedades)
            entorno_base.generar_entorno(propiedades)
            
            #---DIBUJAR TRAYECTORIAS POR DEFECTO---
            #1. Obtener la duración total de la canción para la escala de tiempo
            total_frames = context.scene.frame_end
            escala = propiedades.escala
            
            #2. Mapeo de pistas utilizando el modelo de datos actualizado
            pistas = {
                "Vocals": propiedades.vocals,
                "Bass": propiedades.bass,
                "Drums": propiedades.drums,
                "Other": propiedades.other
            }
            
            #3. Generación de las subpistas 
            for nombre, props in pistas.items():
                esfera = bpy.data.objects.get(f"Pista_{nombre}")
                if esfera:
                    generacion_trayectorias.modificar_trayectorias(esfera, props, total_frames, escala)   
            
            #4. Actualizar la vista de Blender
            bpy.context.view_layer.update()

            #5. Activamos el panel de modificación de propiedades
            propiedades.pista_procesada_ia = True
            return{'FINISHED'}

        except Exception as error_generacion:
            self.report({'WARNING'}, f"Audio separado, la generación 3D no ha cargado correctamente: {str(error_generacion)}")
            return{'CANCELLED'}

class AUDIO8D_OT_procesar_dsp(bpy.types.Operator):
    """_summary_

    Args:
        bpy (_type_): _description_
    """

    bl_idname = "audio8d.procesar_dsp"
    bl_label = "Procesar audio 8D"
    bl_description = "Operador que recoge las propiedades de las subpistas y aplica el motor DSP"

    def execute(self, context):
        propiedades = context.scene.audio8d

        #---RECOGEMOS LAS PROPIEDADES QUE NECESITA EL PROCESADOR EN UN JSON---
        try:
            ruta_json = exportar_propiedades.obtener_ruta_directorio()
            exportar_propiedades.exportar_propiedades(ruta_json, propiedades)

            self.report({'INFO'}, f"Coordenadas guardadas correctamente en: {ruta_json}")
            
        except Exception as error_propiedades:
            self.report({'ERROR'}, str(error_propiedades))
            return{'CANCELLED'}
        
        #---APLICACIÓN DEL PROCESAMIENTO 8D--- 
        try:
            ruta_pista_binaural = kernel.KernelAudio8D.iniciarProcesamiento8D(ruta_json)
            self.report({'INFO'}, f"Procesamiento 8D realizado correctamente: {ruta_json}")  
            
        except Exception as error_dsp:
            self.report({'ERROR'}, str(error_dsp))
            return{'CANCELLED'}
        
        #---EXPORTAR AL TIMELINE---
        try:
            exportar_timeline.integrar_pista_binaural(context.scene, ruta_pista_binaural)
            self.report({'INFO'}, f"Pista enlazada correctamente, abre el Video Sequencer para visualizar la pista!")
        
        except Exception as error_timeline:
            self.report({'ERROR'}, str(error_timeline))
            return{'CANCELLED'}
        
        #1. Activamos la posibilidad de poder exportar la pista
        propiedades.pista_procesada = True
        return{'FINISHED'}
    
class AUDIO8D_OT_exportar_pista(bpy.types.Operator, ExportHelper):
    """Operador que recoge la pista binaural resultante y la guarda en el directorio deseado"""

    bl_idname = "audio8d.exportar_pista"
    bl_label = "Exportar Pista Binaural"
    bl_description = "Abre el explorador para guardar la mezcla final y limpia la caché"

    #Filtro del archivo .wav
    filename_ext = ".wav"
    filter_glob: bpy.props.StringProperty(
        default="*.wav",
        options={'HIDDEN'},
        maxlen=255,
    )

    #Función que prepara el archivo antes de abrir la ventana
    def invoke(self, context, event):
        """Prepara el nombre del archivo sugerido antes de abrir la ventana"""
        nombre_base = context.scene.audio8d.nombre_original
        
        nombre_sin_ext = os.path.splitext(nombre_base)[0]
        self.filepath = f"{nombre_sin_ext}_8D.wav"
            
        #1. Llamada al explorador de archivos de Blender
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        ruta_destino = self.filepath

        try:
            # Llamamos a nuestra función de utilidad pasándole el contexto y la ruta
            exito, mensaje = exportar_pista.exportar_pista(ruta_destino, context)
            self.report({'INFO'}, f"Pista exportada correctamente en: {ruta_destino}")
            return {'FINISHED'}

        except Exception as error_exportacion:
            self.report({'ERROR'}, str(error_exportacion))
            return{'CANCELLED'}