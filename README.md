# Manim Spanish
¡Bienvenidos a Manim Spanish! Una versión de Manim con documentación incluida totalmente en español. Manim es un proyecto creado por Grant Sanderson, conocido por su canal de YouTube llamado [3blue1brown](https://www.youtube.com/channel/UCYO_jab_esuFRV4b17AJtAw). Esta librería de Python sirve para crear animaciones matemáticas totalmente gratis y no necesitas un gran computador para hacerlas.
Manim tiene como objetivo animar en todos los sentidos de animar. Si deseas impactar en la educación matemática con grandioso diseño gráfico y animaciones espectaculares, ¡estás en el lugar correcto! Y además es gratis :grin:.

## Instalación y versiones
Antes de instalar, asegúrate de saber bien cuál es la versión que vas a querer de Manim. Existen 3 versiones principales actualmente: [ManimGL](https://github.com/3b1b/manim), [ManimCairo](https://github.com/3b1b/manim/tree/cairo-backend) y [Manim Community](https://github.com/ManimCommunity/manim), siendo [Manim Spanish]() actualmente una bifurcación de ManimGL, por lo que está la documentación completamente dirigida a usuarios de ManimGL hispanohablantes. Todo lo dicho anteriormente quiere decir, en resumen, que puedes instalar ManimGL, ManimCairo, Manim Community o Manim Spanish (bifurcación de ManimGL).

### Instalación de Manim Spanish
Si deseas instalar otra versión o hacer la instalación de Manim Spanish sin saber sobre programación, dirígete a la [documentación](docs). Si ya tienes conocimientos previos sobre Python, Git, FFmpeg y LaTeX, puedes seguir los siguientes pasos.

#### Windows
1. [Descargar e instalar FFmpeg](https://www.gyan.dev/ffmpeg/builds/).
2. Para el texto matemático debes [descargar e instalar MiKTeX](https://miktex.org/download).
3. Clonar repositorio con [Git](https://git-scm.com/downloads) e instalar los correspondientes paquetes y módulos de Python.
   ```
   git clone https://github.com/HACHEDOSO/ManimSpanish.git
   cd ManimSpanish
   pip install -e .
   ```

#### Mac OSX
1. Instalar FFmpeg y LaTeX en la terminal usando [Homebrew](https://brew.sh/index_es).
   ```
   brew install ffmpeg mactex
   ```
2. Instalar última version de Manim utilizando los siguientes comandos.
   ```
   git clone https://github.com/HACHEDOSO/ManimSpanish.git
   cd ManimSpanish
   pip install -e .
   ```

#### Linux
Ver la [documentación](docs) para instalar en Linux.

### ¿Todo resultó bien en la instalación?
Para verificar que esté todo correcto en la instalación de Manim Spanish, ve a la carpeta donde clonaste con Git a Manim Spanish dentro de la terminal.
```
cd C:\Carpeta\Donde\Clonaste\ManimSpanish
```
Luego ejecuta el siguiente comando en la terminal.
```
# El comando de ManimGL y por ende de Manim Spanish es manimgl
manimgl example_scenes.py OpeningManimExample
```
Si se abrió una ventana de video mientras se renderizaba y terminó sin errores (el comando no guardará video, sino que simplemente ejecutará una ventana), ¡felicitaciones! Has instalado Manim Spanish en tu equipo, ¡es todo tuyo! :wink:.

## Tutorial
En la [documentación de Manim Spanish](docs) podrás encontrar todos los tutoriales que necesitas para aprender a usar Manim.

## Documentación
Nuevamente menciono el enlace de la documentación. [Haz clic aquí para acceder a ella](docs). Si tienes dudas, no dudes en consultar [aquí](https://github.com/HACHEDOSO/ManimSpanish/discussions).

## ¡Podemos cambiar el aula!
