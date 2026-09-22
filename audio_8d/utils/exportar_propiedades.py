import bpy
import json
import os
from .entorno_base import cartesianas_a_esfericas

def exportar_propiedades(ruta_json, propiedades):
    """Genera un JSON con las propiedades que utilizará el procesador DSP que son las generales del sistema 
    y las coordenadas esféricas de cada pista

    Args:
        ruta_json (string): nombre de la ruta donde se volcará el JSON
        propiedades (context): _description_
    """

    json_dsp = {
        "contexto_global": {
            "frecuencia_muestreo": int(propiedades.frecuencia_muestreo),
            "fps_escena": propiedades.fps_escena
        },
        "pistas": {}
    }
    
    escala = propiedades.escala
    pistas = {
        "Vocals": propiedades.vocals,
        "Drums": propiedades.drums,
        "Bass": propiedades.bass,
        "Other": propiedades.other
    }

    #Coordenadas de las pistas
    for nombre_pista, props in pistas.items():
        puntos_pista = []
        esfera = bpy.data.objects.get(f"Pista_{nombre_pista}")

        #Estática
        if props.tipo_trayectoria == 'ESTATICA':
            x, y, z = esfera.location
            r, az, el = cartesianas_a_esfericas(x, y, z)
            r_real = r / escala

            puntos_pista.append({
                "r": round(r_real, 4),
                "azimut": round(az, 2),
                "elevacion": round(el, 2)
            })

        #Dinámica
        else:
            instancer = bpy.data.objects.get(f"Instancer_{nombre_pista}")
            
            for vertice in instancer.data.vertices:
                x, y, z = vertice.co
                r, az, el = cartesianas_a_esfericas(x, y, z)
                r_real = r / escala

                puntos_pista.append({
                    "r": round(r_real, 4),
                    "azimut": round(az, 2),
                    "elevacion": round(el, 2)
                })
    
        datos_pista = {
                "ruta_stem": props.ruta_stem,
                "coordenadas": puntos_pista
        }

        #Si la pista no es estática volcamos la resolución espacial
        if props.tipo_trayectoria != 'ESTATICA':
                datos_pista["resolucion_espacial"] = props.resolucion_espacial

        json_dsp["pistas"][nombre_pista] = datos_pista

    #Empaquetar JSON
    try:
        with open(ruta_json, "w") as archivo:
            json.dump(json_dsp, archivo, indent=4)
        print(f"Mapa de propiedades DSP guardado en {ruta_json}")

    except Exception as error_json:
        print(f"Error al guardar el JSON: {error_json}")


def obtener_ruta_directorio():
    """
    Calcula la ruta exacta donde está guardado el archivo .blend actual
    y devuelve la ruta final para guardar el JSON en el mismo directorio.
    """

    #1. Obtenemos la ruta completa del archivo de Blender
    ruta_blend = bpy.data.filepath
    
    #2. Si no se ha guardado el archivo se instancia un error
    if not ruta_blend:
        raise ValueError("Guarda tu archivo antes de ejecutar el procesador DSP")
    
    #2. Obtenemos la carpeta
    directorio_base = os.path.dirname(ruta_blend)
    
    #3. Construimos la ruta final con el nombre del archivo JSON
    ruta_final_json = os.path.join(directorio_base, "coordenadas_dsp.json")
    
    return ruta_final_json