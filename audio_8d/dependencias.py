import bpy
import sys
import subprocess

#Comprobación del panel librerías necesarias para el funcionamiento del addon
try:
    import torch
    import demucs
    import pandas
    import scipy
    import soundfile
    import diffq
    MODULES_AVAILABLE = True
    print(f"Librerías cargadas correctamente!")
except Exception as e:
    print(f"Faltan librerías -> {e}")
    MODULES_AVAILABLE = False

#Panel de preferencias del addon (Preferencias > Addons > Audio 8D)
class AUDIO8D_PT_Dependencies(bpy.types.AddonPreferences):
    """Lógica con la comprobación de la instalación de dependencias"""
    bl_idname = __package__.split(".")[0]
    bl_label = "Dependencias del Addon"
    bl_description = "Descarga e instala el entorno de ejecución para el motor 8D"

    def draw(self, context):
        layout = self.layout

        #Comprobamos si están instaladas las librerías necesarias, si no, retorna error
        if MODULES_AVAILABLE:
            layout.label(text="Las librerías necesarias están instaladas.", icon='CHECKMARK')
        else:
            layout.label(text="Faltan librerías necesarias.", icon='ERROR')
            layout.operator("audio8d.instalar_dependencias", text="Instalar Entorno TFG", icon='IMPORT')

#Botón para instalar las dependencias necesarias
class AUDIO8D_OT_instalar_dependencias(bpy.types.Operator):
    """Instalador de dependencias necesarias para el funcionamiento del addon"""
    bl_idname = "audio8d.instalar_dependencias"
    bl_label = "Instalar Dependencias"
    bl_description = "Descarga e instala el entorno de ejecución para el motor 8D"
    
    def execute(self, context):

        #Instalación de las librerías únicamente en blender sin afectar al sistema
        python_exe = sys.executable 
        self.report({'INFO'}, "Instalando entorno completo... Mira la consola.")
        print("Iniciando instalación de dependencias... Esto puede tardar unos minutos.")
        
        try:
            #Instalación del método que permite desempaquetar los archivos .whl
            subprocess.check_call([python_exe, "-m", "pip", "install", "wheel"])
            
            #Instalación de todas las librerías necesarias
            subprocess.check_call([
                python_exe, "-m", "pip", "install",
                "--no-cache-dir",
                "torch==2.1.2+cpu", "torchaudio==2.1.2+cpu", 
                "demucs", "pandas", "scipy", "soundfile", "diffq",
                "--extra-index-url", "https://download.pytorch.org/whl/cpu"
            ])
        
        except subprocess.CalledProcessError as e:
            self.report({'ERROR'}, f"Fallo en la instalación: {e}")
            return {'CANCELLED'}
                
        self.report({'INFO'}, "Instalación completada. Reinicia Blender.")
        return {'FINISHED'}

#Registro/desregistro
def register():
    """Regista los módulos de dependencias"""
    bpy.utils.register_class(AUDIO8D_PT_Dependencies)
    bpy.utils.register_class(AUDIO8D_OT_instalar_dependencias)

def unregister():
    """Desregistra los módulos de dependencias"""
    bpy.utils.unregister_class(AUDIO8D_OT_instalar_dependencias)
    bpy.utils.unregister_class(AUDIO8D_PT_Dependencies)