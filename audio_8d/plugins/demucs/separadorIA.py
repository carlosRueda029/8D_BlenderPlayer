import os
import sys
import subprocess
import time

def ejecutar_separacion(ruta):

    #1. Encontrar la carpeta origen y el nombre de la canción
    carpeta_origen = os.path.dirname(ruta)
    nombre_cancion = os.path.splitext(os.path.basename(ruta))[0]

    #2. Usar el Python interno de Blender
    ruta_python = sys.executable

    #3. Enrutamiento al módulo FFPMEG que necesita demucs
    ruta_script = os.path.dirname(__file__)
    ruta_ffmpeg_bin = os.path.join(ruta_script, "bin")
    ruta_ffmpeg_exe = os.path.join(ruta_ffmpeg_bin, "ffmpeg.exe")

    if not os.path.exists(ruta_ffmpeg_exe):
        raise FileNotFoundError("No se encuentra ffmpeg interno. Revisa la carpeta bin del Addon.")

    #4. Inyección de ffpmeg en el entorno de ejecución del archivo
    entorno_personalizado = os.environ.copy()
    
    #5. Preparación de la ejecución del comando
    path_key = "PATH"
    for key in entorno_personalizado.keys():
        if key.upper() == "PATH":
            path_key = key
            break
    
    entorno_personalizado[path_key] = ruta_ffmpeg_bin + os.pathsep + entorno_personalizado.get(path_key, "")

    #6. Recolección de los datos de la canción para comprobar si ya ha sido separada o no
    ruta_base_stems = os.path.join(carpeta_origen, "mdx_extra_q", nombre_cancion)
    stems = {
        "vocals": os.path.join(ruta_base_stems, "vocals.wav"),
        "drums": os.path.join(ruta_base_stems, "drums.wav"),
        "bass": os.path.join(ruta_base_stems, "bass.wav"),
        "other": os.path.join(ruta_base_stems, "other.wav")
    }

    #6. Comprobación por si la pista ya estuviera separada
    ya_procesada = all(os.path.exists(pista) for pista in stems.values())
    if ya_procesada:
        print(f"[SEPARADOR IA]: '{nombre_cancion}' ya está separada! Se recogen sus stems")
        return stems
    
    print(f"[SEPARADOR IA]: Ejecutando demucs en: {nombre_cancion}...")

    #7. Ejecución del proceso
    comando = [ruta_python, "-m", "demucs", "-n", "mdx_extra_q", "-d", "cpu", "-j", "4", "--out", carpeta_origen, ruta]
    tiempo_inicio = time.time()
    
    resultado = subprocess.run(
        comando, 
        check=False, 
        capture_output=True, 
        text=True, 
        env=entorno_personalizado
    )

    #8. Gestión de devolución de errores en la consola para la UI
    if resultado.returncode != 0:
        error_completo = resultado.stderr.strip() if resultado.stderr else "Error desconocido del comando del motor de separación."
        lineas = error_completo.split('\n')
        error_interfaz = lineas[-1] if lineas else error_completo
        raise RuntimeError(error_interfaz)
    
    tiempo_total = time.time() - tiempo_inicio
    print(f"[SEPARADOR IA] Finalizado en: {int(tiempo_total // 60)} min y {int(tiempo_total % 60)} seg.\n")

    #Verificación de las pistas después de su separación
    for pista, ruta_pista in stems.items():
        if not os.path.exists(ruta_pista):
            raise FileNotFoundError(f"El motor no pudo generar la subpista: {pista}.wav")
    
    return stems