import bpy
import math

def generar_entorno(propiedades):
    """Función principal (Vista) que orquesta la generación del entorno 3D en Blender con gestión de errores.
    Lee el Modelo de Datos y delega la creación de colecciones, el oyente y las subpistas para dibujar la escena.

    Args:
        propiedades (Audio8DProperties): Modelo de datos principal que contiene la configuración 
        persistente del proyecto, incluyendo escalas y parámetros temporales.
    """
    
    errores = []

    #---LIMPIAR ENTORNO EXISTENTE---
    try:
        limpiar_entorno()
    except Exception as error_limpieza:
        errores.append(f"Error en la limpieza: {str(error_limpieza)}")

    #---GENERAR OYENTE---
    try:
        generar_oyente(propiedades)

    except Exception as error_oyente:
        errores.append(f"Error en Oyente: {str(error_oyente)}")

    #---GENERAR SUBPISTAS---
    try:
        generar_subpistas(propiedades)

    except Exception as error_subpista:
        errores.append(f"Error en Subpistas: {str(error_subpista)}")

    #---GENERAR TRAYECTORIAS DE SUBPISTAS

    if errores:
        print("Errores en la generación:", errores)


#---FUNCIONES GENERALES---
def generar_oyente(propiedades):
    """Genera la representación visual de la cabeza del oyente y sus oídos en la colección principal.
    Sitúa al oyente basándose en la elevación base del modelo, actuando como el centroide o punto de referencia 
    (0,0,0 relativo) para los cálculos geométricos de la audición binaural.

    Args:
        propiedades (Audio8DProperties): Modelo de datos general que define la escala visual y la altura a la 
        que se debe colocar al oyente.
    """

    # Colección de los elementos principales
    col_oyente = configurar_coleccion("Audio8D_Escena")
    escala = propiedades.escala
    z_head = propiedades.elevacion_base * escala 
    
    #1. Cabeza del oyente
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.0875 * escala, location=(0, 0, z_head))
    cabeza = bpy.context.active_object
    cabeza.name = "Oyente_Cabeza"
    col_oyente.objects.link(cabeza)
    bpy.context.collection.objects.unlink(cabeza)
    bloquear_transformaciones(cabeza)
    
    #2. Orejas del oyente heredando a cabeza
    for lado, posX in [("L", -0.0875 * escala), ("R", 0.0875 * escala)]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.015 * escala, location=(posX, 0, 0))
        oido = bpy.context.active_object
        oido.name = f"Oyente_Oido_{lado}"
        oido.parent = cabeza
        col_oyente.objects.link(oido)
        bpy.context.collection.objects.unlink(oido)
        bloquear_transformaciones(oido)
        
    #3. Nariz del oyente apuntando al frente (+Y) heredando a cabeza
    loc_y_nariz = (0.0875 + 0.02) * escala 
    bpy.ops.mesh.primitive_cone_add(radius1=0.015 * escala, depth=0.04 * escala, location=(0, loc_y_nariz, 0))
    nariz = bpy.context.active_object
    nariz.name = "Oyente_Nariz"
    nariz.rotation_euler = (math.radians(-90), 0, 0)
    nariz.parent = cabeza
    col_oyente.objects.link(nariz)
    bpy.context.collection.objects.unlink(nariz)
    bloquear_transformaciones(nariz)


def generar_subpistas(propiedades):
    """Genera y posiciona las representaciones visuales (esferas) en el espacio 3D para cada una de 
    las subpistas separadas (Vocals, Bass, Drums, Other). Vincula los objetos 3D con sus respectivos vectores 
    directores, inyectando las coordenadas espaciales iniciales de vuelta al modelo de datos.

    Args:
        propiedades (Audio8DProperties): Modelo de datos general del que se extraen los punteros individuales 
        (PropiedadesSubpistas) de cada instrumento.
    """

    col_oyente = configurar_coleccion("Audio8D_Escena")
    escala = propiedades.escala
    cabeza = bpy.data.objects.get("Oyente_Cabeza")

    pistas_config = {
        "Vocals": (propiedades.vocals, (0.0, 0.5, 1.0, 1.0), (0, 1, 0)),
        "Bass":   (propiedades.bass,   (0.2, 0.8, 0.2, 1.0), (0, -1, 0)),
        "Other":  (propiedades.other,  (1.0, 0.8, 0.0, 1.0), (-1, 0, 0)),
        "Drums":  (propiedades.drums,  (1.0, 0.2, 0.2, 1.0), (1, 0, 0))
    }

    #Generación y asignación de cada una de las subpistas
    for nombre, (props, color, (dirX, dirY, dirZ)) in pistas_config.items():
            #Asignación del color al modelo
            props.color_ui = color

            #Inicialización de la distancia según las distancias cartesianas predefinidas
            distancia = props.distancia * escala
            loc_x = dirX * distancia
            loc_y = dirY * distancia
            loc_z = dirZ * distancia

            #Asignación de los valores esféricos (azimut, elevación) -> radio obviado al ya establecerse antes!
            _, azimut, elevacion = cartesianas_a_esfericas(dirX, dirY, dirZ)
            props.azimut = azimut
            props.elevacion = elevacion

            #1. Pivote central desde el que rotará la esfera emparentado a la cabeza
            bpy.ops.object.empty_add(type='SPHERE', radius=0.1 * escala, location=(0, 0, 0))
            pivote = bpy.context.active_object
            pivote.name = f"Pivote_{nombre}"
            pivote.parent = cabeza 
            col_oyente.objects.link(pivote)
            bpy.context.collection.objects.unlink(pivote)
            bloquear_transformaciones(pivote)
            
            #2. Crear la Esfera de la subpista en su posición estática final
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05 * escala, location=(loc_x, loc_y, loc_z))
            esfera = bpy.context.active_object
            esfera.name = f"Pista_{nombre}"

            mat = crear_material(f"Mat_{nombre}", color)
            esfera.data.materials.append(mat)
            
            #3. Emparentar a su pivote para futuras órbitas 
            esfera.parent = pivote
            col_oyente.objects.link(esfera)
            bpy.context.collection.objects.unlink(esfera)
            bloquear_transformaciones(esfera)


#---FUNCIONES AUXILIARES---
def configurar_coleccion(nombre, padre=None):
    """Crea o recupera una colección en el Outliner de Blender para organizar jerárquicamente la escena 3D 
    y facilitar la eliminación del entorno al actualizarlo.

    Args:
        nombre (str): Nombre identificativo de la colección.
        padre (bpy.types.Collection, optional): Colección padre donde se anidará la nueva jerarquía. 
        Por defecto es None (se ancla a la colección maestra de la escena).

    Returns:
        bpy.types.Collection: Instancia nativa de la colección de Blender creada o recuperada.
    """

    if nombre not in bpy.data.collections:
        col = bpy.data.collections.new(nombre)
        
        if padre and padre in bpy.data.collections:
            bpy.data.collections[padre].children.link(col)
        else:
            bpy.context.scene.collection.children.link(col)
    
    return bpy.data.collections[nombre]

def bloquear_transformaciones(obj):
    """Bloquea las propiedades de transformación (Locación, Rotación, Escala) de un objeto 3D.
    Garantiza la integridad de los cálculos matemáticos del motor DSP evitando que el usuario altere 
    las coordenadas arrastrando el objeto libremente en el visor 3D, forzando el uso exclusivo del Controlador 
    (Mesa de Mezclas).

    Args:
        obj (bpy.types.Object): Instancia del objeto de Blender cuyas matrices de transformación van a ser 
        bloqueadas en la interfaz de usuario.
    """

    obj.lock_location = (True, True, True)
    obj.lock_rotation = (True, True, True)
    obj.lock_scale = (True, True, True)


def crear_material(nombre, color):
    """Genera un material visual con un color base (Principled BSDF) para diferenciar psico-visualmente las 
    esferas de cada subpista en el visor 3D.

    Args:
        nombre (str): Nombre identificativo del material.
        color (tuple): Vector de 4 flotantes (R, G, B, A) comprendidos entre 0.0 y 1.0 que define el color 
        en el espacio RGBA.

    Returns:
        bpy.types.Material: Instancia nativa del material de Blender generado y configurado.
    """
    
    mat = bpy.data.materials.new(name=nombre)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    
    if bsdf:
        bsdf.inputs['Base Color'].default_value = color
    
    return mat

def cartesianas_a_esfericas(x, y, z):
    """Convierte las coordenadas espaciales cartesianas (X, Y, Z) extraídas del visor de Blender a coordenadas 
    esféricas polares (Radio, Azimut, Elevación). Aplica las correcciones trigonométricas necesarias para adaptar 
    los ejes de la vista 3D al sistema polar requerido por la base de datos HRIR (KEMAR) para la posterior 
    convolución.
        Azimut -> Frente (+Y) = 0, Derecha (+X) = 90, Detrás (-Y) = 180, Izquierda (-X) = 270
        Elevación -> Arriba (+Z) = 90, Abajo (-Z) = -90

    Args:
        x (float): Componente X de la subpista en el espacio 3D (Eje interaural, Izquierda/Derecha).
        y (float): Componente Y de la subpista en el espacio 3D (Eje de profundidad, Delante/Atrás).
        z (float): Componente Z de la subpista en el espacio 3D (Eje vertical, Arriba/Abajo).

    Returns:
        tuple: Tupla de 
    """
    #Cálculo del radio
    r = math.sqrt(x**2 + y**2 + z**2)

    #Distancia, azimut y elevación
    dist_xy = math.sqrt(x**2 + y**2)
    azimut = math.degrees(math.atan2(x, y)) % 360
    elevacion = math.degrees(math.atan2(z, dist_xy))
    
    return r, azimut, elevacion


def limpiar_entorno():
    """
    Busca la colección principal del addon y elimina de forma segura todos 
    los objetos y sus datos para evitar duplicados en caso de reseleccionar canción.
    """

    col_oyente = bpy.data.collections.get("Audio8D_Escena")
    if col_oyente:

        # Forzamos una lista estática de los objetos para evitar errores de mutación al borrar
        for obj in list(col_oyente.objects):
            # Guardamos la referencia a los datos internos (Mesh o Curve)
            datos_internos = obj.data
            
            # 1. Eliminamos el objeto de la escena
            bpy.data.objects.remove(obj, do_unlink=True)
            
            # 2. Limpiamos la base de datos de Blender para no dejar bloques huérfanos (.001)
            if datos_internos:
                if isinstance(datos_internos, bpy.types.Mesh):
                    bpy.data.meshes.remove(datos_internos)
                elif isinstance(datos_internos, bpy.types.Curve):
                    bpy.data.curves.remove(datos_internos)