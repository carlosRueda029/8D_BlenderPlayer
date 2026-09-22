import json
import numpy as np
import soundfile as sf
from scipy.signal import fftconvolve
import os

#Lista vacía con todas las HRIR que se van a utilizar en el procesamiento
hrir_globales = {}

def aplicarProcesamiento8D(ruta_json):
    """Aplica toda la cadena de procesamiento con los datos proporcionados y las HRIR

    Args:
        ruta_json (string): contiene la ruta al archivo JSON
    """

    #---LEER JSON---
    try:
        with open(ruta_json, "r") as archivo:
            datos_dsp = json.load(archivo)

    except Exception as error_lectura:
        raise ValueError(f"El plugin DSP no pudo leer el JSON: {error_lectura}")

    #1. Variables globales
    contexto_global = datos_dsp.get("contexto_global", {})
    pistas = datos_dsp.get("pistas", {})
    frecuencia_muestreo = contexto_global.get("frecuencia_muestreo", 44100)
    fps_escena = contexto_global.get("fps_escena", 30)
    
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_diffuse = os.path.join(directorio_actual, "diffuse")

    #---EXTRAER Y ASIGNAR LAS HRIR NECESARIAS---
    try:
        cargarHRIR(ruta_diffuse, pistas)

    except Exception as error_cargaHRIR:
        raise ValueError(f"El plugin DSP no pudo cargar correctamente las HRIR: {error_cargaHRIR}")
    
    #---APLICAR CONVOLUCIÓN---
    try:
        ruta_pista_binaural = convolucionDSP(pistas, frecuencia_muestreo, fps_escena)

    except Exception as error_dsp:
        raise ValueError(f"La convolución tuvo un problema en: {error_dsp}")
    
    return ruta_pista_binaural


def convolucionDSP(pistas, frecuencia_muestreo, fps_escena):
    """_summary_

    Args:
        pistas (_type_): _description_
        frecuencia_muestreo (_type_): _description_
        fps_escena (_type_): _description_

    Returns:
        _type_: _description_
    """

    pistas_procesadas = []
    longitud_maxima = 0

    #1. Convolución para cada una de las pistas
    for nombre_pista, datos_pista in pistas.items():
        coordenadas = len(datos_pista.get("coordenadas", []))

        #ESTÁTICA
        if(coordenadas == 0):
            pista_audio = convolucionDSP_estatica(nombre_pista, datos_pista, frecuencia_muestreo)
        #DINÁMICA
        else:
            pista_audio = convolucionDSP_dinamica(nombre_pista, datos_pista, frecuencia_muestreo, fps_escena)

        #2. Determinamos la longitud máxima del audio para determinar la duración del master
        pistas_procesadas.append(pista_audio)
        if(len(pista_audio) > longitud_maxima):
            longitud_maxima = len(pista_audio)

    #3. Creación de la pista con el master final
    master_mix = np.zeros((longitud_maxima, 2))
    for pista in pistas_procesadas:
        master_mix[:len(pista)] += pista

    #4. Normalización de la ganancia
    pico_maximo = np.max(np.abs(master_mix))
    master_mix = master_mix / pico_maximo

    #5. Se obtiene el nombre de la canción para el archivo temporal final
    primera_pista = list(pistas.values())[0]
    ruta_stem_ref = primera_pista.get("ruta_stem", "")
    nombre_cancion = os.path.basename(os.path.dirname(ruta_stem_ref))
    nombre_archivo_8d = f"{nombre_cancion}_8D.wav"

    #6. Exportación temporal a la carpeta del plugin para manejar el Video Sequencer
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_pista_binaural = os.path.join(directorio_actual, nombre_archivo_8d)
    sf.write(ruta_pista_binaural, master_mix, frecuencia_muestreo, subtype='PCM_16')

    #7. Extra para las pruebas
    for nombre_pista, pista_procesada in zip(pistas.keys(), pistas_procesadas):
        nombre_archivo_subpista = f"{nombre_cancion}_{nombre_pista}_8D.wav"
        ruta_subpista = os.path.join(directorio_actual, nombre_archivo_subpista)
        sf.write(ruta_subpista, pista_procesada, frecuencia_muestreo, subtype='PCM_16')

    return ruta_pista_binaural


def convolucionDSP_estatica(nombre_pista, datos_pista, frecuencia_muestreo):
    """Proceso DSP que recoge una pista y aplica una convolución estática

    Args:
        nombre_pista (_type_): _description_
        pistas (_type_): _description_
        frecuencia_muestreo (_type_): _description_

    Returns:
        _type_: _description_
    """

    #1. Variables globales
    global hrir_globales
    ruta_stem = datos_pista["ruta_stem"]
    coordenadas = datos_pista.get("coordenadas", [])
    audio_stem, fs_stem = sf.read(ruta_stem)

    #2. Conversión a mono para aplicar el impulso (Espacialización por lateralización)
    audio_stem = np.mean(audio_stem, axis=1)

    #3. Obtención de las coordenadas
    r = coordenadas[0]["r"]
    az = coordenadas[0]["azimut"]
    el = coordenadas[0]["elevacion"]

    #4. Aplicación de la inversa del cuadrado conforme la amplitud y obtención de HRIR
    ganancia = 1.0 / r
    hrir = hrir_globales[(az, el)]
    hrir_L = hrir[:, 0]
    hrir_R = hrir[:, 1]

    #5. Aplicación de FFT
    audio_conv_L = fftconvolve(audio_stem, hrir_L, mode='full')
    audio_conv_R = fftconvolve(audio_stem, hrir_R, mode='full')

    #6. Únimos ambas señales en una matriz estéreo y aplicamos la ganancia
    audio_salida = np.column_stack((audio_conv_L, audio_conv_R))
    audio_salida *= ganancia

    return audio_salida

def convolucionDSP_dinamica(nombre_pista, datos_pista, frecuencia_muestreo, fps_escena):
    """
    Proceso DSP donde se aplica una convolución a las subpistas cuando su trayectoria es dinámica
    utilizando el método Overlap-Add
    """

    global hrir_globales
    
    #1. Variables globales
    ruta_stem = datos_pista["ruta_stem"]
    coordenadas = datos_pista.get("coordenadas", [])
    audio_stem, fs_stem = sf.read(ruta_stem)
    
    #2. Conversión a mono para aplicar el impulso (Espacialización por lateralización) 
    audio_stem = np.mean(audio_stem, axis=1)
    
    #3. Obtención del tamaño del bloque a procesar
    resolucion = datos_pista.get("resolucion_espacial", 30)
    salto_frames = 61 - resolucion
    muestras_por_bloque = int((frecuencia_muestreo / fps_escena) * salto_frames)
    total_muestras = len(audio_stem)
    n_bloques = int(np.ceil(total_muestras / muestras_por_bloque)) #Equivalente 1:1 al número de vértices con resolución 60!
    num_coordenadas = len(coordenadas)

    #4. Longitud de un filtro HRIR para saber cuanto tiene que medir el master final y aplicación de la inversa del cuadrado conforme la amplitud
    r = coordenadas[0]["r"]
    az_0 = coordenadas[0]["azimut"]
    el_0 = coordenadas[0]["elevacion"]
    ganancia = 1.0 / r
    longitud_hrir = len(hrir_globales[(az_0, el_0)][:, 0])

    #5. Matriz con la salida de audio conjunta de todas las pistas
    audio_salida = np.zeros((total_muestras + longitud_hrir - 1, 2))

    #Convolución por bloques (Overlapp-Add)
    for i in range(n_bloques):
        
        #6. Obtenemos el bloque de audio correspondiente al índice actual
        inicio = i * muestras_por_bloque
        fin = min(inicio + muestras_por_bloque, total_muestras)
        bloque_audio = audio_stem[inicio:fin]

        #7. Obtenemos el radio y el par de coordenadas (azimut, delta) a aplicar correspondiente al índice actual
        i_coord = i % num_coordenadas
        az = coordenadas[i_coord]["azimut"]
        el = coordenadas[i_coord]["elevacion"]

        #8. Obtención de HRIR
        hrir = hrir_globales[(az, el)]
        hrir_L = hrir[:, 0]
        hrir_R = hrir[:, 1]
        
        #9. Aplicación de HRIR e unión de canales L y R
        bloque_conv_L = fftconvolve(bloque_audio, hrir_L, mode='full')
        bloque_conv_R = fftconvolve(bloque_audio, hrir_R, mode='full')
        
        audio_estereo_bloque = np.column_stack((bloque_conv_L, bloque_conv_R))

        #10. Únimos ambas señales en una matriz estéreo y sumamos el bloque al audio de salida final
        fin_buffer = inicio + len(bloque_conv_L)
        audio_salida[inicio:fin_buffer] += audio_estereo_bloque

    #11. Aplicamos la ganancia y determinamos la longitud de la pista maestra final
    audio_salida *= ganancia
    
    return audio_salida


def cargarHRIR(ruta_diffuse, pistas):
    """_summary_

    Args:
        ruta_diffuse (_type_): _description_
        pistas (_type_): _description_
    """

    #Colecciones de datos para cargar las HRIR correspondientes a cada punto
    global hrir_globales
    coordenadas_unicas = set()
    aux_hrir = {}

    #1. Obtenemos los sets de coordenadas únicas para todas las pistas
    for nombre_pista, datos_pista in pistas.items():
        coordenadas = datos_pista.get("coordenadas", [])

        for punto in coordenadas:
            coordenadas_unicas.add((punto["azimut"], punto["elevacion"]))

    print(f"[MOTOR DSP]: se han detectado {len(coordenadas_unicas)} puntos espaciales únicos. Obteniendo HRIR")

    #2. Obtenemos las HRIR únicas más cercanas a todas las coordenadas de las pistas
    for az, el in coordenadas_unicas:
        
        #3. Búsqueda de HRIR para dicho punto
        ruta_hrir, invertir = buscarHRIR(ruta_diffuse, az, el)
        
        #4. Si no ha sido asignada se guarda por primera vez en el conjunto auxiliar
        if ruta_hrir not in aux_hrir:
            audio_hrir, fs_hrir = sf.read(ruta_hrir)
            aux_hrir[ruta_hrir] = audio_hrir

        #5. Obtenemos la HRIR (Par único ruta-audio)
        audio_hrir = aux_hrir[ruta_hrir]

        #6. Modificación de la HRIR base para dicha coordenada espejo en L y R (ej. 45 grados = 315 grados) 
        if(invertir):
            audio_hrir = audio_hrir[:, [1, 0]]
        
        #Guardamos el HRIR al par azimut, elevación
        hrir_globales[(az, el)] = audio_hrir

    #Limpiamos diccionario auxiliar
    del aux_hrir


def buscarHRIR(ruta_diffuse, az, el):
    """Conforme a una base de datos HRIR, azimut y elevación busca la ruta del archivo HRIR que mejor se adapta
    a dicho punto. 

    Args:
        ruta_diffuse (_type_): _description_
        az (_type_): _description_
        el (_type_): _description_

    Returns:
        _type_: _description_
    """

    #1. Límites de elevación KEMAR (-40 como elevación inferior máxima y elevación en saltos de 10 en 10)
    el_kemar = max(-40, el)
    el_kemar = round(el_kemar / 10) * 10
    ruta_el = f"elev{int(el_kemar)}"
    ruta_carpeta = os.path.join(ruta_diffuse, ruta_el)

    #2. Límites azimutales KEMAR (según aproximación al valor más cercano)
    az_kemar = az
    invertir = False

    if 180 < az < 360:
        az_kemar = 360 - az
        invertir = True
    
    #3. Obtenemos todas las HRIR para dicha elevación
    archivos = os.listdir(ruta_carpeta)
    az_disponibles = []
    
    for archivo in archivos:    
        if archivo.endswith(".wav"):
            az_archivo = archivo.split('e')[1].split('a')[0]
            az_disponibles.append(int(az_archivo))

    #4. Obtenemos el archivo con menor valor azimutal
    az_kemar_final = min(az_disponibles, key = lambda x: abs(x - az_kemar))
    nombre_archivo = f"H{int(el_kemar)}e{int(az_kemar_final):03d}a.wav"
    ruta_hrir = os.path.join(ruta_carpeta, nombre_archivo)

    return ruta_hrir, invertir