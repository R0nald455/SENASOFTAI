# app.py
#Se importan las librerias necesarios para el funcionamiento del sistema
from flask import Flask, render_template, request, redirect, url_for,json,jsonify
from PIL import Image
import os
import uuid
import requests
import azure.cognitiveservices.speech as speechsdk

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

@app.route('/', methods=['GET', 'POST'])



# ... Código previo ...

@app.route('/', methods=['GET', 'POST'])
def index():



    # Renderiza la plantilla y pasa 'os' al contexto
    return render_template('index.html', os=os)


#Se define la funcion audio utilizada para mencionar las traducciones
def audio(tag_name):
    #se estrablece la key 
    key = "4baf4501910d46fcab901eb20cacae43"
    #Se configura el sdk enviando la key y la region donde esta el servicio
    speech_config = speechsdk.SpeechConfig(subscription=key, region="eastus")
    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
    # se escoge el bot de quien va a leer la instrucciones
    speech_config.speech_synthesis_voice_name='en-US-RyanMultilingualNeural'
    #se etavlece la configuracion del sintentizador para el funcionamiento del sistema
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    # Se establece lo que va a decir el servicio con un espacio para dejar tiempo entre traduccion y traduccion
    text = "                                           "+tag_name+" "
    #se realiza el llamado al sintetizador se le pasa el texto y se obtiene el audio 
    speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()
    #Se evalua si el  proceso termino satisfactoriamente o si sucedio algun error o fue cancelado
    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized for text [{}]".format(text))
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print("Error details: {}".format(cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")
                


#se define la funcion traductor y se le pasa el tagname a traducir
def traductor(text):
        # se agregan los endponit y la key del servicio con la region 
        key = "f809460a0b1f447ea9543506a5feb737"
        endpoint = "https://api.cognitive.microsofttranslator.com/"
        location = "eastus"
        #se declara el path y se realiza la construccion de la url del servicio
        path = '/translate'
        constructed_url = endpoint + path
        #se definen los parametros que seran usados en la transaccion
        params = {
            'api-version': '3.0',
            'from': 'es', # idioma de origen
            'to': ['pt-pt', 'ja','en'] #idiomas de destino
        }
        #se definen los headers que seran enviados
        headers = {
            'Ocp-Apim-Subscription-Key': key,#la llave de nuestro servicio
            'Ocp-Apim-Subscription-Region': location,#la region donde se encuentra el servicio
            'Content-type': 'application/json',#el tipo de contenido que se le va a enviar
            'X-ClientTraceId': str(uuid.uuid4())
        }
        # se construye el body con el texto a traducir
        body = [{
            'text': text
        }]
        #se realiza el llamado a la API enviando la url, los parametros, headers y el body como json
        request = requests.post(constructed_url, params=params, headers=headers, json=body)
        #se obtiene el archivo json de resultados 
        response = request.json()
        texts = [translation["text"] for translation in response[0]["translations"]]
        # Inicializar el índice del bucle
        i = 0
        # Recorrer la lista 'texts' y agregar al array de resultados para ser enviados al front
        resultados=[text]
        while i < len(texts):
            resultados.append(texts[i])#se agregan al array resultados 
            i += 1
        return resultados#se retorna el array resultados
        
        
#se define la funcion de clasificacion mediante URL de imagenes
def ClasificacionURLimagen(img):
        # URL a la que se desea realizar la solicitud POST
            predictionUrl="https://anlisistextov2.cognitiveservices.azure.com/customvision/v3.0/Prediction/2ed9fc82-7fd7-4caa-aa2a-706ff7201143/classify/iterations/Clasificador/url"
            body = {'url': img}
            #se comvierte el body a un archivo json para ser enviado    
            body_string = json.dumps(body)
            # Datos que que se desean enviar en el cuerpo de la solicitud 
            data = {
                'Prediction-Key': 'd876a5f5153b415daad195249dc49e4b',
                'Content-Type': 'application/json',
                'Body': body_string
            }
            # Realiza la solicitud POST
            response = requests.post(predictionUrl, json=body, headers=data)
            # se obtiene la respuesta en un archivo json
            response_data = response.json()
            #se  obtinen los datos de predictions para ser analizados
            predictions = response_data.get('predictions', [])
            for prediction in predictions:
                probability = prediction.get('probability', 0.0)  # Obtiene la probabilidad
                tag_name = prediction.get('tagName', 'Desconocido')#se obtiene el tagname
                if((probability*100)>70):#se evalua la probabilidad de que la imagen corresponda con la categoria
                    resultados=traductor(tag_name)#se realiza el llamado a la funcion traductor para que el tagname sea traducido
                    #se realiza la redaccion del texto enviar al servicio de azure
                    texto="La imagen seleccionada corresponde a"+tag_name+"su traduccion al portugues,japones e ingles es "+resultados[1]+resultados[2]+resultados[3]
                    audio(texto)
                    #se retornan los resultados 
                    return resultados


#se define la funcion de deteccion de objetos
def Detectorobjetos(url):    
    #se establece la url  para acceder al servicio
    predictionUrl="https://eastus.api.cognitive.microsoft.com/customvision/v3.0/Prediction/7bd42c28-f1a8-49df-b221-dbfec5c5ea50/detect/iterations/Objetos/url"
    #se establece la url en una vaiable
    img = url
    #se establecen los headers que seran enviados al servicio
    data = {
        "Prediction-Key": "fa79eabca38c491486b40514e1f4dca1",
        "Content-Type": "application/json",
    }
    #se establece el body para ser enviado
    body = {'url' : img }
    #se realiza el requerimiento post al servicio
    response = requests.post(predictionUrl, headers=data, json=body)
    #se obtienen los resultados del servicio
    result = response.json()
    #se obtienen los resultados de predictions
    predictions = result["predictions"]
    #se retornan los resultados
    return predictions 
#se define la funcion de reconocimiento facial
def face(url):
    #se establecen la key y el endpoint del servicio
    key = "be0ae0fa7046496293c9992ef6458d92"
    endpoint = "https://pruebareconocimientofacial01.cognitiveservices.azure.com/"
    #se establece la imagen en una variable 
    img = url
    #se establecen los headers para ser enviados al servicio
    data = {
        "Ocp-Apim-Subscription-Key": 'be0ae0fa7046496293c9992ef6458d92',
        "Content-Type": "application/json"
    }
    #se establece el body donde se encuentran
    body = {
        "url": img
    }
    #se realiza  el requerimiento al servicio de azure
    response = requests.post(f"{endpoint}/face/v1.0/detect?detectionModel=detection_01", headers=data, json=body)
    #se obtienen los resultados del servicio
    result = response.json()
    #se obtienen los resultados del analisis
    analysis = result
    #se retornan lso resultados
    return analysis


#se define la funcion para subir imagenes
def subirImagen(file):
        if file:
            # Guarda el archivo cargado en la carpeta de uploads
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            # Procesa la imagen para redimensionarla y finalmente guardarla
            image = Image.open(filename)
            image.thumbnail((200, 200))
            image.save(filename)
            #se retorna el nombre con el que fue guardada la imagen
            return filename


#se realiza la definicion de la ruta del formulario 
@app.route('/formulario', methods=['POST'])
#se definie la funcion de procesamiento del formulario
def procesar_formulario():
    if request.method == 'POST':
        # Obtener los datos del formulario
        url = request.form.get('url')
        #se realiza el llamado a la funcion del servicio de clasificacion
        resultados=ClasificacionURLimagen(url)
        #se redirecciona al usuario 
        return render_template('result.html', data=resultados)
    
#se establece la ruta 
@app.route('/objetos', methods=['POST'])
def objetos():
    if request.method == 'POST':
        #se obtienen las urls del formulario para ser procesadas 
        url1 = request.form.get('url1')
        url2 = request.form.get('url2')
        url3 = request.form.get('url3')
        #se llaman las funciones y se establece el guardado de los resultados 
        resultados1= Detectorobjetos(url1)
        resultados2=Detectorobjetos(url2)
        #se redirecciona a los resultados
        return render_template('objetos.html',data=resultados1),render_template('objetos.html',data=resultados2)
    
    
    
@app.route('/rostros', methods=['POST'])
def rostros():
    if request.method == 'POST':
        # Obtener los datos del formulario
        url1 = request.form.get('url')
        #se realiza el llamado a la funcion de reconocimiento facial 
        resultados1= face(url1)
        #se realiza la redireccion del usuario
        return render_template('rostros.html',data=resultados1)
    
#Se realiza la definicion de main y se establecen las reglas de ejecucion
if __name__ == '__main__':
    app.run(debug=True)




                
                

    