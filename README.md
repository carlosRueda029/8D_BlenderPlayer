# TFG-CRM
Repositorio personal del trabajo de fin de grado de Ingeniería Multimedia de Carlos Rueda Martínez.

# INSTALACIÓN DEL ADDON!!
- 1. Clona el repositorio donde quieras
- 2. Dentro de TFG-CRM verás un archivo "audio_8d.zip", este es el módulo a instalar.
- 3. Después de cargar el .zip en el apartado de preferencias verás que no tiene las dependencias instaladas. Pulsa en el botón y espera (Blender se va a quedar congelado cargando las librerías, abre la consola para ver cómo va la instalación antes de pulsar al botón)
- 4. Reinicia blender después de la instalación y el addon debería de estar incrustado en el panel derecho.

# CONSIDERACIONES!
- 1. Debido a que el addon genera archivos auxiliares, recomiendo que guardes el proyecto en una carpeta aparte y que dentro de ella metas los archivos .wav con los que quieras trabajar junto con el .blend (que también debes guardar en esa carpeta), el resto lo realiza el plugin!
- 2. El módulo de separación de pistas suele tardar un rato dependiendo de la longitud de la pista, prueba con una pista que dure un 1 - 1:30 min aproximadamente.
- 3. Cuando finalice el primer proceso habrá una esfera representando la cabeza y una nariz para orientar hacia donde quieres situar las pistas (selecciona el icono del Viewport Shading arriba a la derecha para ver los colores de las pistas y tener una referencia visual).
- 4. Pese a que no está hecho el módulo de exportación (que no es nada apenas), después de modificar las propiedades y renderizar la canción esta se guarda en el secuenciador de vídeo con lo que al pulsar play puedes ver como las esferas rotan conforme a la trayectoria coincidiendo con la pista binaural.
- 5. Es posible mezclar trayectorias estáticas y dinámicas.
- 6. Para notar el resultado es indispensable que uses auriculares.
- 7. Recomiendo bastante que la propiedad de resolución espacial en las pistas dinámicas lo subas al máximo para que interpole bien, si lo bajas se escucharán clicks en la canción final.

# Requisitos para la instalación:
- Blender LTS 3.6.26 o menor.
- Python 3.10

## Teoría e ideas:
- Bases de datos con HRTF (Head-Releated Transfer Functions) para generar presets de escucha guardables
- Generar perfiles de escucha en base a datos de tablas
- Se entiende que solo se podrían utilizar auriculares puesto que los altavoces no generan espacialidad
- Interés en Sofa puesto que audio3d y pyBinSim las utilizan.
- Formateo en JSON para los presets.

## Ejemplos de tecnologías:
- Mutagen python: modificar metadatos de la información
- Demucs/Spleeter: tecnología de IA para separar pistas
- Audio3d: librería de procesamiento de señal a través de una sala virtual (convoluciones)
- pyBinSim: síntesis binaural dinámica con la aplicación de tablas HRTF
- KEMAR y SofaConventions.org como bases de datos con tablas HRTF.  


## Métricas y obtención de datos (presets?):
- SAM (Spatial Audio Metrics): recursos de código abierto para facilitar el análisis de datos dentro del dominio del audio espacial.
- ITD (Interaural Time Difference): diferencia de tiempo que tarda en viajar un sonido de un oído a otro
- ILD (Interaural Level Difference): diferencia de intensidad del sonido entre los oídos.
- Centroide Espectral: medida utilizada en el procesamiento digital de señales de audio para caracterizar el espectro de un sonido. Indica donde se encuentra el centro de masa del espectro.

## Documentación:
Comparación entre Demucs y Spleeter: https://beatstorapon.com/blog/demucs-vs-spleeter-the-ultimate-guide/
