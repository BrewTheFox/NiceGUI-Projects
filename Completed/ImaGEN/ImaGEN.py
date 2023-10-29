from nicegui import ui, app
import requests
import re
import json
from transformers import pipeline
from translate import Translator
import base64


async def EjecutarJS(comando):
    await ui.run_javascript(comando)
    if "var textoEstatico =" in comando:
        ui.notify('Texto Copiado Exitosamente', color='green')

    


def obtener_Fondo():
    #Realiza una peticion a el api de Picsum para obtener el fondo#
    Imagen = requests.get('https://picsum.photos/1920/1080?grayscale', allow_redirects=True)
    return Imagen


def b64(QueConvertir):
    with open('Imagen.jpg', 'wb') as imagen:
        imagen.write(requests.get(QueConvertir).content)
        imagen.close()
    with open('Imagen.jpg', 'rb') as imagen:
        cadena = base64.b64encode(imagen.read())
        imagen.close()
    with ui.dialog() as dialog:
        with ui.card():
            ui.input('TextoBase64').value = cadena.decode('utf-8')
            ui.button('Cerrar', on_click=lambda:dialog.close())
    dialog.open()

    


def describir(url):
    #Utiliza transformers para describir la imagen#
    descriptor = pipeline("image-to-text",model="Salesforce/blip-image-captioning-base")
    descrito = descriptor(url)
    with ui.dialog() as dialog:
        with ui.card():
            traducir = Translator(from_lang='en', to_lang='es')
            ui.input('Descripcion').value = traducir.translate(str(descrito[0]['generated_text']))
            with ui.row():
                ui.button('Copiar', on_click=lambda:EjecutarJS('var textoEstatico = "'+ traducir.translate(str(descrito[0]['generated_text'])) +'"; var elementoTemp = document.createElement("textarea"); elementoTemp.value = textoEstatico; document.body.appendChild(elementoTemp); elementoTemp.select(); document.execCommand("copy"); document.body.removeChild(elementoTemp);'))
                ui.button('Cerrar', on_click=lambda:dialog.close())
    dialog.open()



@ui.page("/")
def HomePage():

    ui.html('''  <style>
    /* Tu código CSS con la animación y el estilo del texto aquí */
    @keyframes gradientAnimation {
      0% {
        background-position: 0% 50%;
      }
      50% {
        background-position: 100% 50%;
      }
      100% {
        background-position: 0% 50%;
      }
    }
    
    .gradient-text {
      background: linear-gradient(45deg, #ff00cc, #3333ff, #66ff33);
      background-size: 200% 200%;
      color: transparent;
      -webkit-background-clip: text;
      background-clip: text;
      animation: gradientAnimation 5s infinite;
    }
  </style>''') #CSS hecho por ChatGPT, yo no se hacer CSS
    
    ui.colors(primary='#515148')
    #Llama a la funcion obtener fondo cuando la pagina carga, coloca la imagen como fondo#
    fondo = obtener_Fondo()
    urlfondo = fondo.url
    ui.image(urlfondo).style('max-width: 1600px; max-height: 900px; object-fit: fill;', ).classes("absolute-center items-center")
    #Acredita al autor :>#
    id = re.search(r"/id/(\d+)/", urlfondo).group(1)
    prename = requests.get("https://picsum.photos/id/"+ id +"/info")
    name = json.loads(str(prename.text))
    with ui.card().classes("absolute-center items-center").style('height: auto;'):
        with ui.row():
            ui.label('Autor: ' + name["author"]).style('background: #959595; background: radial-gradient(circle farthest-corner at center center, #F6F8F9 0%, #E5EBEE 30%, #D7DEE3 60%, #F5F7F9 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;').classes('text-lg') #Obtiene el autor de la imagen#
            ui.link("📩", name["download_url"]).classes('text-lg')
        with ui.row():
            ui.button('Describir', on_click=lambda:describir(name["download_url"])).classes("gradient-text")
            ui.button('Imagen a Base64', on_click=lambda:b64(fondo.url)).classes("gradient-text")
            ui.button('Cambiar', on_click=lambda:EjecutarJS('location.reload()')).style('flat style="color: #FF0080"')
        ui.label("Arctic Softworks").classes("gradient-text text-lg")

ui.run(dark=True)
