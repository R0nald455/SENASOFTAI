# app.py

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

def audio(tag_name):
    key = "4baf4501910d46fcab901eb20cacae43"
    endpoint = "https://eastus.api.cognitive.microsoft.com/sts/v1.0/issuetoken"

    speech_config = speechsdk.SpeechConfig(subscription=key, region="eastus")
    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

    # The language of the voice that speaks.
    speech_config.speech_synthesis_voice_name='ko-KR-GookMinNeural'

    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    # Get text from the console and synthesize to the default speaker.
    print("Enter some text that you want to speak >")
    text = "                                           "+tag_name+" "

    speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()

    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized for text [{}]".format(text))
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print("Error details: {}".format(cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")
                



def traductor(text):
        # Add your key and endpoint
        key = "f809460a0b1f447ea9543506a5feb737"
        endpoint = "https://api.cognitive.microsofttranslator.com/"

        # location, also known as region.
        # required if you're using a multi-service or regional (not global) resource. It can be found in the Azure portal on the Keys and Endpoint page.
        location = "eastus"

        path = '/translate'
        constructed_url = endpoint + path

        params = {
            'api-version': '3.0',
            'from': 'es',
            'to': ['pt-pt', 'ja','en']
        }

        headers = {
            'Ocp-Apim-Subscription-Key': key,
            # location required if you're using a multi-service or regional (not global) resource.
            'Ocp-Apim-Subscription-Region': location,
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }

        # You can pass more than one object in body.
        body = [{
            'text': text
        }]

        request = requests.post(constructed_url, params=params, headers=headers, json=body)
        response = request.json()
        texts = [translation["text"] for translation in response[0]["translations"]]
        # Inicializar el índice del bucle
        i = 0

        # Recorrer la lista 'texts' e imprimir cada elemento
        resultados=[text]
        while i < len(texts):
            resultados.append(texts[i])
            i += 1
        return resultados
        
        
        
def ClasificacionURLimagen(img):
        # URL a la que deseas realizar la solicitud POST
            predictionUrl="https://anlisistextov2.cognitiveservices.azure.com/customvision/v3.0/Prediction/2ed9fc82-7fd7-4caa-aa2a-706ff7201143/classify/iterations/Clasificador/url"
            body = {'url': img}

            body_string = json.dumps(body)

            # Datos que deseas enviar en el cuerpo de la solicitud 
            data = {
                'Prediction-Key': 'd876a5f5153b415daad195249dc49e4b',
                'Content-Type': 'application/json',
                'Body': body_string
            }

            # Realiza la solicitud POST
            response = requests.post(predictionUrl, json=body, headers=data)
            response_data = response.json()
            predictions = response_data.get('predictions', [])
            for prediction in predictions:
                probability = prediction.get('probability', 0.0)  # Obtén la probabilidad
                tag_name = prediction.get('tagName', 'Desconocido')
                if((probability*100)>70):
                    print(f"Probabilidad: {probability}")
                    print(f"Etiqueta: {tag_name}") 
                    resultados=traductor(tag_name)
                    audio(resultados[1])
                    audio(resultados[2])
                    audio(resultados[3])
                    return resultados


def Detectorobjetos(url):    
    predictionUrl="https://eastus.api.cognitive.microsoft.com/customvision/v3.0/Prediction/7bd42c28-f1a8-49df-b221-dbfec5c5ea50/detect/iterations/Objetos/url"
    predictionKey = "fa79eabca38c491486b40514e1f4dca1"
    img = url

    data = {
        "Prediction-Key": "fa79eabca38c491486b40514e1f4dca1",
        "Content-Type": "application/json",
    }

    body = {'url' : img }


    print("Analyzing image...\n")
    response = requests.post(predictionUrl, headers=data, json=body)
    result = response.json()
    
    

    predictions = result["predictions"]
    
    return predictions 


def face(url):
    key = "be0ae0fa7046496293c9992ef6458d92"
    endpoint = "https://pruebareconocimientofacial01.cognitiveservices.azure.com/"


    img = url

    data = {
        "Ocp-Apim-Subscription-Key": 'be0ae0fa7046496293c9992ef6458d92',
        "Content-Type": "application/json"
    }

    body = {
        "url": img
    }

    print("Analyzing image...\n")
    response = requests.post(f"{endpoint}/face/v1.0/detect?detectionModel=detection_01", headers=data, json=body)
    result = response.json()

    analysis = result
    for face in analysis:
        print(f"Face location: {face['faceRectangle']}\n")

def subirImagen(file):
        if file:
            # Guarda el archivo cargado en la carpeta de uploads
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)

            # Procesa la imagen (en este caso, simplemente la redimensiona)
            image = Image.open(filename)
            image.thumbnail((200, 200))
            image.save(filename)
            return filename
        
        
        
   




















@app.route('/formulario', methods=['POST'])
def procesar_formulario():
    if request.method == 'POST':
        # Obtener los datos del formulario
        url = request.form.get('url')
        resultados=ClasificacionURLimagen(url)
        # Realizar cualquier procesamiento necesario con los datos del formulario
        # Por ejemplo, puedes guardarlos en una base de datos o realizar validaciones

        # Devolver una respuesta al usuario
        
        
        return render_template('result.html', data=resultados)
    
@app.route('/objetos', methods=['POST'])
def objetos():
    if request.method == 'POST':
        # Obtener los datos del formulario
        """  file = request.files['file']
        file2 = request.files['file1']
        file3 = request.files['file2'] """
        url="https://humanidades.com/wp-content/uploads/2017/02/pato-2-e1560917879703.jpg"
        resultados1= Detectorobjetos(url)
        """ resutados2= objetos(url)
        resultados3=  "objetos(url)" """
        
        return render_template('objetos.html',data=resultados1)
    
    
    
@app.route('/rostros', methods=['POST'])
def rostros():
    if request.method == 'POST':
        # Obtener los datos del formulario
        """  file = request.files['file']
        file2 = request.files['file1']
        file3 = request.files['file2'] """
        url="https://trucoslondres.com/wp-content/uploads/2017/04/people-1.jpg"
        resultados1= face(url)
        """ resutados2= objetos(url)
        resultados3=  "objetos(url)" """
        
        return render_template('rostros.html',data=resultados1)
    
    
if __name__ == '__main__':
    app.run(debug=True)




                
                

    