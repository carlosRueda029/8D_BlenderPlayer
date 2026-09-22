import bpy
import os
import shutil

def exportar_pista(ruta_destino, context):
    """
    Localiza el archivo .wav en la carpeta interna 'procesador8d'
    y exporta una copia idéntica a la ruta elegida por el usuario.
    """

    #1. Localización de la carpeta con el plugin
    directorio_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    carpeta_procesador = os.path.join(directorio_base, "plugins", "procesador8d")
    
    ruta_origen = None
    
    #2. Buscar el archivo .wav dentro de esa carpeta
    if os.path.exists(carpeta_procesador):
        for archivo in os.listdir(carpeta_procesador):
            if archivo.endswith(".wav"):
                ruta_origen = os.path.join(carpeta_procesador, archivo)
                break # Cogemos el primero que encuentre (la mezcla 8D)
    
    #3. No se encuentra el archivo procesado
    if not ruta_origen or not os.path.exists(ruta_origen):
        raise FileNotFoundError("No se encontró ningún archivo de audio en la caché interna.")

    #3. Exportación de una copia al directorio seleccionado por el usuario
    try:
        shutil.copy2(ruta_origen, ruta_destino)
        return True, "Audio guardado exitosamente."
        
    except Exception as error_exportacion:
        raise RuntimeError(f"Fallo al copiar el archivo: {str(error_exportacion)}")