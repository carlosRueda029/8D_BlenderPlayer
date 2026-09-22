import bpy
import wave

def obtener_datos_base(context, propiedades):
    """Obtiene y asigna las características de la canción base

    Args:
        context (bpy.types.Context): estructura de Blender API que representa el estado actual del entorno
        propiedades (Audio8DProperties): modelo de datos que almacena los parámetros del proyecto
    """

    propiedades.fps_escena = 30
    fps = propiedades.fps_escena
    ruta = propiedades.ruta_original

    try:
        #1. Asignamos los fps del modelo a la escena
        context.scene.render.fps = fps

        #2. Cargamos el audio a través de wave para obtener su duración
        with wave.open(ruta, 'rb') as archivo_wav:
            frames_audio = archivo_wav.getnframes()
            frecuencia_muestreo = archivo_wav.getframerate()

            duracion = frames_audio / float(frecuencia_muestreo)

        #3. Obtención del número de frames de la canción
        frames_totales = int(duracion * fps)
        
        #3. Guardado del modelo de datos
        propiedades.duracion_segundos = duracion
        propiedades.fps_escena = fps
        propiedades.total_frames = frames_totales
        
        #4. Adaptación de la línea de tiempo
        context.scene.frame_start = 1
        context.scene.frame_end = frames_totales

    except Exception as error_duracion:
        print(f"Error al calcular información del audio original: {str(error_duracion)}")

    