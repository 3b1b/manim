<hr/>
<div><p align=center><i> ESPAÑOL </i></p></div>

# Manim personalizado

Esta es mi versión personal que uso para hacer mis proyectos. Tiene algunas modificaciónes y adiciones, los códigos de mis proyectos están en las carpetas "proy_act" y "proy_term".

Debido a las modificaciones que hice no podrás compilar mis proyectos en la [versión original de Manim](https://github.com/3b1b/manim), por lo que recomiendo que uses esta versión si es que quieres compilarlos. Tengo un curso tanto en [español](https://github.com/Elteoremadebeethoven/AnimacionesConManim/) como en [inglés](https://github.com/Elteoremadebeethoven/AnimationsWithManim) que puede ser de interés a las personas que quieran aprender desde cero (aún sin conocimientos de LaTeX y/o Python).

Las principales modificaciones que tiene esta versión de Manim son:
* Configuración para escribir textos en español (prueba con `utf8` o `latin1` en "tex_template.tex")
* Nuevos colores predefinidos.
* Nuevos objetos: Brackets y paréntesis personalizados (similares a Brace) etcétera.
* Nuevas paqueterías añadidas de LaTeX: Fuentes, símbolos de química, música, etcétera.
* Imágenes SVG que utilizo en mis videos.
* Animación de conversación por [Miroslav Olšák](https://github.com/mkoconnor).
* Activa mp4 en alta definición usando ```--hd```.

# Indicaciones.
Probablemente te falte instalar ```pydub``` y ```pyreadline```, instálalo usando pip.

## Instalación de las fuentes emerald en Linux y MacOS

Si usas Mac o GNU/Linux, seguramente tendrás problemas con las fórmulas TeX porque uso la paqueterìa emerald, así que te recomiendo que las instales con las siguientes instrucciones (funciona igual para GNU/Linux y Mac, necesitas tener instalado wget):
```
mkdir -p `kpsewhich --var-value=TEXMFHOME`
cd `kpsewhich --var-value=TEXMFHOME`
wget http://mirror.ctan.org/fonts/emerald.zip
unzip emerald.zip
cp -r emerald/. . && rm -rf emerald/
rm emerald.zip
updmap --enable Map emerald.map  -user
texhash
```
## Habilitar el uso de Tikz en MacOS

Algunas de mis animaciones utilizan la paquetería Tikz y pgfplots de LaTeX, pero en MacOS la conversión de .dvi a .svg cuando se usan estas paqueterías no es completa, por lo que es necesario forzar esa conversión. 
Lo primero que necesitas es ubicar el archivo libgs.dylib, esto lo puedes hacer escribiendo en la terminal:
```
sudo find / -name "libgs.dylib"
```
Ingresas la contraseña de tu usuario y lo buscará, en mi caso es:
```
/usr/local/Cellar/ghostscript/9.26_1/lib/
```
Si no lo tienes instalado, lo puedes instalar con ```brew install ghostscript```.

Una vez hecho esto abre el archivo manimlib/utils/tex_file_writing.py y la linea 88 habilita el siguiente comando:
```python3
"--libgs='/usr/local/Cellar/ghostscript/9.26_1/lib/libgs.dylib'" , # Enable this line with the directory pf libgs.dylib
```
Cambia ```/usr/local/Cellar/ghostscript/9.26_1/lib/libgs.dylib```por el directorio que tu tengas. 
