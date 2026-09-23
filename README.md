# 🎵 8D BlenderPlayer

![Blender](https://img.shields.io/badge/Blender_LTS_3.6.26-F5792A?style=for-the-badge&logo=blender&logoColor=white)
![Python](https://img.shields.io/badge/Python_3.10-3776AB?style=for-the-badge&logo=python&logoColor=white)
![JSON](https://img.shields.io/badge/JSON-000000?style=for-the-badge&logo=json&logoColor=white)
![Demucs](https://img.shields.io/badge/Demucs_mdx__extra__q-4B0082?style=for-the-badge)
![MIT KEMAR](https://img.shields.io/badge/MIT_KEMAR_HRTF_database-A31F34?style=for-the-badge)


Hi there! **8D_BlenderPlayer** is my final BSc thesis project. It's a Blender add-on that generates, customizes, plays and exports your stero into spatial music. It blends an intuitive UI with AI stem separation and DSP engine to pass from an _.wav_ &rarr; _spatialized .wav_. It's build up entirely on Python, JSON to parse information and a HRTF (_Head-Releated Transfer Function_) database to convolve the audio.

---

## 🏗️ Project Architecture
The project follows a microkernel architecture that separates blender _bpy_ operators and UI from the attached plugins _demucs_ and _procesador8d_ which do the two most demanding processes, separate an stereo audio into it's main components and the spatializer DSP engine.

---

## What 8D BlenderPlayer solves?
The project main objective is to zoom closer this technologies and new type of inmersive music to the general public/engineer/artist. It's capabilities has been made up to be understandable to anyone who interacts with it prioritizing the use of open-source tools. The architecture and reason of design is built up to make it easier to install and try new DSP and AI modules that can solve, integrate and speed up the whole process. The UI is made up to weigh less the cognitive fatigue of the user so it can focus on designing the designated spatial audio and learn how properties interact between each other. The models of AI choosen are basic, this means anyone with relative low charge CPU can interact with it, breaking barriers for those with low computer specs. Finally, the add-on remembers the full stereo songs spatialized or simply AI stem separated so it can skip an already done process.

---

## 🎥 Visual example
Here is a visual example of an already separated stero song being modified, spatialized and saved:

---
## ⚙️ Functional deployment

### Install prerequisites
* **Blender LTS 3.6.26** or lower version
* **Python 3.10**
* **.ZIP of the _audio_8d_ folder** (included on the repository!) 

---

### Step-by-Step Installation
1. Clone the full repository.

2. Inside the repository there's an  `audio_8d.zip` already compressed, if not sure, zip the uncompressed folder yourself. 

3. Open Blender and select **Edit &rarr; Preferences &rarr; Add-on** and load the `audio_8d.zip`.

4. If it's your first time installing it &rarr; reboot Blender, reopen the add-on manager and install the preferences on the button it appears. Screen will freeze since it's installing everything, it takes a little time.

5. If everything correctly a labeled "Audio 8D" will be available on the sidebar of the 3D View.

## Add-on usage considerations
- Since it generates aux files, all the `.blend` an `.wav` that might be used are recommended to be stored on a dedicated folder.
- The initial AI stem separator is for low computer resources, modify it if in possesion of a dedicated GPU card or use another that fit your specs.
- After the first stem separation, a low poly representation of the head and different spheres representing each instrument will apear. The UI code parameters mirror them, (_select Viewport Shading to see them_) use it to navigate and understand where and when u wanna spatialize the different stems of the track.
- Static and dynamic trayectories can be mixed.
- Headphones are mandatory, the add-on isn't prepared for speakers response.
- All of the possible spatial properties are definied by the user, but I recommend tweaking at it's maximum the `Resolución espacial` parameter to hear and sense changes clearly.

---

## 📓 BSc Thesis in deep documentation 
As the project was my BSc, it's fully deep reasoning of objectives, design, implementation, tests and more can be reviewed along other considerations can be read in the document [BSc Thesis - 8D_BlenderPlayer](BSc%20Thesis%20-%208D_BlenderPlayer.pdf) done for ETSE (_Escola Tècnica Superior d'Enginyeria_) in
UV (_Universitat de Valencia_).


