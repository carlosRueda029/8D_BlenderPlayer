import bpy
import os

def integrar_pista_binaural(scene, ruta_pista_binaural):
    """
    Carga la pista de audio binaural resultante en el Video Sequencer de Blender
    para sincronizarla con la animación 3D de las esferas.
    
    Args:
        ruta_pista_binaural (str): Ruta absoluta al archivo .wav procesado.
        
    Returns:
        bool: True si se integró con éxito, False si hubo algún error.
    """
    
    #1. Asegurarnos de que el editor de está inicializadp
    if not scene.sequence_editor:
        scene.sequence_editor_create()

    #2. Añade la pista a la secuencia con su nombre 
    nombre_pista = os.path.splitext(os.path.basename(ruta_pista_binaural))[0]
    seq = scene.sequence_editor.sequences
    
    #3. Eliminar renders anteriores para evitar superposiciones de las canciones
    for strip in seq:
        if strip.name == nombre_pista:
            seq.remove(strip)
            
    #4. Insertar la nueva pista de audio en el primer frame
    pista_sonido = seq.new_sound(
        name=nombre_pista,
        filepath=ruta_pista_binaural,
        channel=1,
        frame_start=1
    )

    pista_sonido.show_waveform = True
    return True 