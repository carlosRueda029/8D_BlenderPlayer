import bpy
import math
import mathutils

def modificar_trayectorias(esfera, subpista, total_frames, escala):
    nombre_pista = esfera.name.replace("Pista_", "")
    
    #---ELIMINACIÓN DE LOS DATOS ANTIGUOS---
    #1. Eliminación de la reestricción follow path por si la subpista fuese dinámica
    for c in esfera.constraints:
        if c.type == 'FOLLOW_PATH':
            esfera.constraints.remove(c)
    
    #2. Eliminación del path, instanciador y marcador por si la subpista fuese dinámica
    for prefijo in ["Path_", "Instancer_", "Marcador_"]:
        obj = bpy.data.objects.get(f"{prefijo}{nombre_pista}")
        if obj:
            bpy.data.objects.remove(obj, do_unlink=True)

    #Datos del modelo para realizar los cálculos de la nueva instancia de la subpista generales  
    radio = subpista.distancia * escala 
    azimut_rad = math.radians(subpista.azimut)
    elevacion_rad = math.radians(subpista.elevacion)
    pivote = bpy.data.objects.get(f"Pivote_{nombre_pista}")
    
    #Desbloqueo temporal de la esfera hasta añadir nuevas coordenadas esféricas
    esfera.lock_location = (False, False, False)
    
    #---SIN TRAYECTORIA (NO SE DIBUJAN CURVAS Y MESH)---
    if subpista.tipo_trayectoria == 'ESTATICA':
        
        #1. Si la esfera venía de una trayectoria dinámica se ancla nuevamente a la cabeza
        if pivote and esfera.parent != pivote:
            esfera.parent = pivote
            #Reset de la posición pasada con respecto al antiguo pivote o curva
            esfera.matrix_parent_inverse = mathutils.Matrix.Identity(4)
        
        #2. Esféricas -> Cartesianas
        x = radio * math.sin(azimut_rad) * math.cos(elevacion_rad)
        y = radio * math.cos(azimut_rad) * math.cos(elevacion_rad)
        z = radio * math.sin(elevacion_rad) 
        
        #3. Asignación de la posición y bloqueo al pivote de la cabeza
        esfera.location = (x, y, z)
        esfera.lock_location = (True, True, True)
        return
        
    #---CON TRAYECTORIA (SE DIBUJAN VÉRTICES, CURVA Y MESH)---
    #1. La subpista no está sujeta al padre, sino a la curva posterior
    esfera.parent = None
    esfera.location = (0, 0, 0)
    esfera.lock_location = (True, True, True)
    
    #2. Datos del modelo para realizar los cálculos de la nueva instancia de la subpista
    inclinacion_rad = math.radians(subpista.inclinacion_orbita)
    resolucion = subpista.resolucion_espacial
    tipo = subpista.tipo_trayectoria

    #3. ---Asignación de la resolución---
    salto_frames = 61 - resolucion
    num_puntos = total_frames // salto_frames

    #Siempre habrá cuatro puntos independientemente de la duración del audio
    if num_puntos < 4:
        num_puntos = 4
    
    #4. ---Generación de los vértices del Halo según la trayectoria asignada---
    coordenadas_blender = []
    radio_xy = radio * math.cos(elevacion_rad)
    z_offset = radio * math.sin(elevacion_rad)
    matriz_inclinacion = mathutils.Euler((0, inclinacion_rad, 0), 'XYZ').to_matrix()
    
    #5. Asignación de vértices
    for i in range(num_puntos + 1):
        progreso = i / num_puntos 
        angulo_actual = (progreso * 2 * math.pi) + azimut_rad
        
        if tipo == 'CIRCULAR':
            x_base = radio_xy * math.sin(angulo_actual)
            y_base = radio_xy * math.cos(angulo_actual)
            
        elif tipo == 'CUADRADA':
            r_cuadrado = radio_xy / max(abs(math.sin(angulo_actual)), abs(math.cos(angulo_actual)))
            x_base = r_cuadrado * math.sin(angulo_actual)
            y_base = r_cuadrado * math.cos(angulo_actual)

        #Se aplica un producto vectorial entre la matriz de inclinación y el punto obtenido
        z_base = z_offset
        vector_rotado = matriz_inclinacion @ mathutils.Vector((x_base, y_base, z_base))
        coordenadas_blender.append(vector_rotado)
        
    #6. ---Generación de la curva sobre la que se apoyan los vértices---
    #Metadatos de la curva
    curve_data = bpy.data.curves.new(name=f"Curva_{nombre_pista}", type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.use_path = True
    
    #Contención de bisel en la curva (tubo)
    curve_data.bevel_depth = 0.001 * escala
    curve_data.bevel_resolution = 2 
    
    #Asignación de los vértices a un spline polinómico
    spline = curve_data.splines.new('POLY') 
    spline.points.add(len(coordenadas_blender) - 1)
    for i, coord in enumerate(coordenadas_blender):
        spline.points[i].co = (coord.x, coord.y, coord.z, 1.0)
    
    #7. Generación del camino que seguirá dicha curva con los datos de la misma
    path_obj = bpy.data.objects.new(f"Path_{nombre_pista}", curve_data)
    
    #8. Asignación del pivote a la curva y el material/color de la subpista
    if pivote:
        path_obj.parent = pivote
        path_obj.matrix_parent_inverse = mathutils.Matrix.Identity(4)
    path_obj.location = (0, 0, 0)
    
    mat_existente = bpy.data.materials.get(f"Mat_{nombre_pista}")
    if mat_existente:
        path_obj.data.materials.append(mat_existente)
    
    col_oyente = bpy.data.collections.get("Audio8D_Escena")
    coleccion_destino = col_oyente if col_oyente else bpy.context.collection
    coleccion_destino.objects.link(path_obj)
    
    #9. ---Inclusión del MeshInstancer y marcadores en la curva---
    #Metadatos de la malla con las coordenadas de la subpista. Instancer con SOLO vértices -> coordenadas_blender
    malla_instancer = bpy.data.meshes.new(f"MeshInstancer_{nombre_pista}")
    malla_instancer.from_pydata([c.to_tuple() for c in coordenadas_blender], [], [])
    
    #Emparenta con el centroide para instanciar los vértices de la malla
    instancer_obj = bpy.data.objects.new(f"Instancer_{nombre_pista}", malla_instancer)
    if pivote:
        instancer_obj.parent = pivote
        instancer_obj.matrix_parent_inverse = mathutils.Matrix.Identity(4)
    
    #Reglas de instanciación de los vértices
    instancer_obj.location = (0, 0, 0)
    instancer_obj.instance_type = 'VERTS'
    instancer_obj.show_instancer_for_viewport = False
    coleccion_destino.objects.link(instancer_obj)
    
    bpy.ops.mesh.primitive_ico_sphere_add(radius=0.01 * escala, subdivisions=1)
    marcador = bpy.context.active_object
    marcador.name = f"Marcador_{nombre_pista}"
    if mat_existente:
        marcador.data.materials.append(mat_existente)
    
    #Reestructura las colecciones según se generan los tipos
    marcador.parent = instancer_obj
    if marcador.name in bpy.context.collection.objects:
        bpy.context.collection.objects.unlink(marcador)
    coleccion_destino.objects.link(marcador)
    
    # ---Asignación de reestricciones a la subpista (Curva con vértices y mesh)---
    constraint = esfera.constraints.new(type='FOLLOW_PATH')
    constraint.target = path_obj
    constraint.use_curve_follow = True
    constraint.forward_axis = 'FORWARD_Y' 
    constraint.up_axis = 'UP_Z'
    constraint.use_fixed_location = True 
    
    #Keyframes principales
    constraint.offset_factor = 0.0
    constraint.keyframe_insert(data_path="offset_factor", frame=0)
    constraint.offset_factor = 1.0
    constraint.keyframe_insert(data_path="offset_factor", frame=total_frames)
    
    if esfera.animation_data and esfera.animation_data.action:
        for fcurve in esfera.animation_data.action.fcurves:
            if fcurve.data_path == f"constraints[\"{constraint.name}\"].offset_factor":
                for keyframe in fcurve.keyframe_points:
                    keyframe.interpolation = 'LINEAR'


def actualizar_trayectoria_ui(self, context):
    """Recoge la subpista que se está modificando y 

    Args:
        context (_type_): _description_
    """
    total_frames = context.scene.frame_end
    propiedades_globales = context.scene.audio8d 
    escala = propiedades_globales.escala 
    
    pistas = {
        "Vocals": propiedades_globales.vocals,
        "Bass": propiedades_globales.bass,
        "Drums": propiedades_globales.drums,
        "Other": propiedades_globales.other
    }
    
    for nombre, props in pistas.items():
        if props == self:
            esfera = bpy.data.objects.get(f"Pista_{nombre}")
            if esfera:
                modificar_trayectorias(esfera, self, total_frames, escala)
            break