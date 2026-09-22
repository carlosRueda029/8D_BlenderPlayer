import os
from ..plugins.demucs import separadorIA
from ..plugins.procesador8d import procesadorDSP


class KernelAudio8D:
    """Kernel encargado de orquestar y delegar los datos a los plugins adecuados"""

    @staticmethod
    def cargarPistaEstereo(ruta_pista):
        """Obtiene la ruta de la pista que se quiere separar y llama al módulo encargado del proceso de
        separación por pistas.

        Args:
            ruta_pista (String): ruta del archivo de audio que quiere procesar

        Returns:
            dict: diccionario con la ruta de las cuatro subpistas
        """

        try:
            print(f"[KERNEL]: Iniciando separación de IA para: {ruta_pista}")
            stems = separadorIA.ejecutar_separacion(ruta_pista)

            if not stems:
                raise ValueError("El plugin de Demucs no devolvió los stems esperados.")
        
        except Exception as error_separacion:
            raise RuntimeError(f"Error interno en el procesamiento del plugin IA: {str(error_separacion)}")
 
        return stems

    @staticmethod
    def iniciarProcesamiento8D(ruta_json):
        """Aplica el procesamiento 8D a las subpistas según la información contenida en el JSON

        Args:
            ruta_json (string): _description_

        Raises:
            RuntimeError: _description_

        Returns:
            string: devuelve la ruta de la pista temporal para cargarla en el timeline
        """

        try:
            ruta_pista_binaural = procesadorDSP.aplicarProcesamiento8D(ruta_json)
            print(f"[KERNEL]: Iniciando procesamiento 8D para {ruta_json}")

            return ruta_pista_binaural

        except Exception as error_procesamiento:
            raise RuntimeError(f"Error interno en el procesamiento del plugin DSP: {str(error_procesamiento)}")