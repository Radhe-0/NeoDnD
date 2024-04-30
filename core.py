from flask import Flask, request, jsonify
import json
import os
import requests
import random


app = Flask(__name__)

prompt_dm = '''
## Tarea y contexto
+ Te llamas Caliope, pero no dirás más acerca de ti.
+ Tu función es simplemente decir que no te molesten, que no estás disponible para hablar todavía.
+ Di que no puedes aportar nada por ahora.

## Guía de estilo
+ Tu forma de expresarte es divertida y carismática
+ Usarás emojis
+ Eres breve y conciza en tus respuestas.
'''

prompt_dm_2 =  '''
## Tarea y contexto
+ Tu nombre es Calíope, y eres una Dungeon Master.
+ El mundo y los acontecimientos sólo serán visibles para ti. ¡No hagas spoilers ni reveles secretos clave!
+ Actuarás como los personajes de ser necesario.
+ Cuando un jugador intente realizar una acción que requiera tirar los dados tú le pides de forma breve que tire los dados para el atributo que se necesite.
+ Si te preguntan sobre los comandos disponibles, di que esa no es tu función, que puedes obtener ayuda del comando "/ayuda"

## Guía de estilo
+ Tu forma de expresarte es la de una dama, usarás español latino.
+ Usarás emojis
+ Eres breve y conciza en tus respuestas.
'''

prompt_chrono_crafter = 'Se te pasará un world building creado por el World Builder para una partida de dungeons and dragons. Tu tarea es generar una serie de sucesos clave que los jugadores deberán enfrentar durante su aventura en este mundo. Por favor, crea un minimum de 5 y un máximo de 10 sucesos clave, asegurándote de que estén conectados entre sí y que conduzcan a una trama interesante y emocionante. Los sucesos clave deben incluir desafíos, batallas, descubrimientos y giros inesperados. Tu respuesta NO será visible para los jugadores, será pasada a otro bot, así que no necesitas hacer nada más que lo que se te pide'
prompt_world = '''
Se te brindarán especificaciones para generar un mundo de ficción para una partida de rol que combine los siguientes géneros y elementos clave:
Información adicional: Ninguna
Describe:
- La ubicación geográfica y el entorno físico general del mundo.
- 3 Facciones o grupos sociales más importantes, incluyendo detalles sobre su poder, ideología y conflictos.
- 3 personajes clave (ninguno que sea el protagonista), destacando sus roles, motivaciones y relaciones.
- 3 nuevas razas si los géneros principales lo requieren.
- 3 lugares clave
- Evento o conflicto histórico que haya marcado el desarrollo del mundo.
- 2 secretos sobre personajes o el mundo que sean claves.
- Cuál podría ser el rol de los jugadores en este mundo.
Ten en cuenta que la respuesta NO será visible para el usuario, la leerá otro bot, así que no necesitas hacer nada más allá de lo que se te pide
'''
plantilla_hoja = 'Fuerza: x\nDestreza: x\nConstitución: x\nInteligencia: x\nSabiduría: x\nCarisma: x'
ayuda_texto = ''


generar_partida_comando = ''
@app.route('/mensaje_nuevo', methods=['POST'])
def mensaje_nuevo(): # Esta funcion maneja todos los mensajes que vayan llegando a un chat de whatsapp
    global generar_partida_comando
    data = request.get_json()
    mensaje_texto = data['mensaje_texto'] # string
    contacto = data['contacto'] # string
    es_bot = data['es_bot'] # booleano
    # TODO: No mandar mensajes que sean stickers, imagenes, videos, etc, solo texto!!!!

    print(f"{contacto}:{mensaje_texto}, {es_bot}")

    if es_bot:
        if not mensaje_texto.startswith("Generando partida") or not mensaje_texto.startswith("Ponlo"):
            agregar_a_historial(mensaje_texto, contacto, es_bot)
            return {"responde": False}

    if mensaje_texto.startswith("/dado "): # cuando un jugador quiere lanzar un dado
        respuesta_bot = prefijo_dado(mensaje_texto)
        return jsonify(respuesta_bot) # ERROR

    elif mensaje_texto.startswith("/dados "): # cuando un jugador quiere lanzar más de un dado
        respuesta_bot = prefijo_dados(mensaje_texto)
        return jsonify(respuesta_bot) # ERROR

    elif mensaje_texto.startswith("/next"): # cuando el jugador ha terminado su turno
        agregar_a_historial(mensaje_texto, contacto, es_bot)
        respuesta_bot = prefijo_next() # ERROR

    elif mensaje_texto.startswith("/caliope "): # cuando el jugador tiene una pregunta para el dungeon master
        agregar_a_historial(mensaje_texto, contacto, es_bot)
        respuesta_bot = prefijo_caliope()
        return jsonify({"responde": True, "mensaje": respuesta_bot, "doble": False})

    elif mensaje_texto.startswith("/stats"): # cuando el jugador quiere conocer sus stats
        pass

    elif mensaje_texto.startswith("/generar-partida "): # cuando el admin quiere colocar las especificaciones de la partida
        agregar_a_historial(mensaje_texto, contacto, es_bot)
        generar_partida_comando = mensaje_texto
        return jsonify({"mensaje": "Generando partida... ¡Aguarden un momento!", "responde": True})

    elif mensaje_texto.startswith("/plantilla"):
        return jsonify({"mensaje": plantilla_hoja, "responde": True, "doble": True, "mensaje2": "Ponlo en el comando '/hoja-personaje', recuerda que la suma de todos los puntos debe ser 10,\n¡Más info en la descripción del grupo!"})

    elif mensaje_texto.startswith("/hoja-personaje"): # cuando un jugador quiere enviar su hoja de personaje al contexto de la IA
        print(f"\n\nHOJA DE PERSONAJE DE {contacto}: {mensaje_texto}\n\n")
        respuesta_bot = prefijo_hoja(mensaje_texto, contacto)
        print("\n\nJSON:", respuesta_bot, "\n\n")
        return jsonify({"mensaje": '', "responde": False, 'doble': False})

    elif mensaje_texto.startswith("/ayuda"):
        return jsonify({"mensaje": ayuda_texto, "responde": True, "doble": False})

    elif mensaje_texto.startswith("Generando partida"): # Cuando el bot avisa que se está generando la partida
        if es_bot:
            respuesta_bot = prefijo_generando_partida()
            return jsonify({"mensaje": respuesta_bot, "responde": True, "doble": False})
    else:
        agregar_a_historial(mensaje_texto, contacto, es_bot)
        return jsonify({"mensaje":'', "responde": False, "doble": False})


# Prefijos o comandos
#------------------------------------------------------------------------------------------#

def prefijo_dado(mensaje_texto):
    string_num = remover_prefijo(mensaje_texto)
    num_dado = nums_dado(string_num)[0] # int
    resultado_dado = random.randint(1, num_dado)
    mensaje = f"dado: {resultado_dado}"
    return respuesta_bot


def prefijo_dados(mensaje_texto):
    string_nums = remover_prefijo(mensaje_texto)
    nums_dados = nums_dado(string_num)
    resultados_dados = [random.randint(1, i) for i in nums_dados]
    mensaje = f"-dados: {resultados_dados}"
    return mensaje


def prefijo_next(mensaje_texto, historial_chat):
    pass


def prefijo_caliope():
    global prompt_dm, prompt_dm2
    historial = get_historial_formateado_comand_r()
    if len(historial) == 1:
        ultimo_mensaje = historial[0]
        historial_sin_ultimo = []
    else:
        ultimo_mensaje = historial[-1]
        historial_sin_ultimo = historial[:-1]

    if se_ha_generado_partida():
        respuesta = call_command_r(ultimo_mensaje, historial_sin_ultimo, prompt_dm_2)
    else:
        respuesta = call_command_r(ultimo_mensaje, historial_sin_ultimo, prompt_dm)

    texto_caliope = respuesta['text']
    return texto_caliope


def generar_partida(mensaje_texto):
    global prompt_chrono_crafter, prompt_world
    especificaciones_mundo = remover_prefijo(mensaje_texto)
    world_building = call_command_r(especificaciones_mundo, [], prompt_world)['text']
    eventos_clave = call_command_r(world_building, [], prompt_chrono_crafter)['text']
    colocar_en_world_building(world_building)
    colocar_en_eventos_clave(eventos_clave)
    partida_generada = True


def prefijo_generando_partida():
    global generar_partida_comando, prompt_dm2, prompt_dm
    generar_partida(generar_partida_comando)
    world_building = get_world_building()
    eventos_clave = get_eventos_clave()
    agregar_a_historial(f"## Información sólo visible para Calíope:\n{world_building}\n{eventos_clave}", 'mensaje del servidor', False)
    historial = get_historial_formateado_comand_r()
    historial_sin_ultimo = historial[:-1]
    ultimo_mensaje = historial[-1]

    if se_ha_generado_partida():
        respuesta_bot = call_command_r(ultimo_mensaje, historial_sin_ultimo, prompt_dm_2)['text']
    else:
        respuesta = call_command_r(ultimo_mensaje, historial_sin_ultimo, prompt_dm)
    return respuesta_bot

def prefijo_hoja(mensaje_texto, contacto_nombre):
    global prompt_hoja
    mensaje_sin_prefijo = remover_prefijo(mensaje_texto)
    mensaje_y_contacto = f"nombre:{contacto_nombre}\n{mensaje_texto}"
    respuesta_bot = call_command_r(mensaje_y_contacto, [], prompt_hoja)
    print("RESPUESTAAAAAAAAAA:", respuesta_bot, "\n\n")
    return json.loads(respuesta_bot['text'])



#------------------------------------------------------------------------------------------#

def remover_prefijo(mensaje_texto):
    prefijos = ["/dado ", "/dados ", "/next ", "/duda ", "/stats", "/generar-partida ", "/hoja-personaje"]
    for prefijo in prefijos:
        if mensaje_texto.startswith(prefijo):
            return mensaje_texto[len(prefijo):]
    return mensaje_texto


def nums_dado(s):
    try:
        nums = [int(x) for x in s.replace(",", "").split()]
        if all(isinstance(x, int) for x in nums):
            return nums
        else:
            raise ValueError("Invalid input string")
    except ValueError:
        raise ValueError("Invalid input string")


def call_command_r(mensaje, historial_chat, system_prompt):
    api_key = 'UCX18MSt5m94VZ7qNQhJgTdEVrpEgIHuudjM8Gvu'
    url = 'https://api.cohere.ai/v1/chat'
    headers = {'accept': 'application/json','Content-Type': 'application/json', 'Authorization': f'Bearer {api_key}'}
    body = {"chat_history": historial_chat, "message": f"{mensaje}", "model": "command-r", "preamble": system_prompt}

    try:
        response = requests.post(url, headers=headers, json=body)

        if response.status_code == 200:
            data = response.json()
            dict_respuesta = {"text": data['text'], 'input_tokens': data['meta']['tokens']['input_tokens'], 'output_tokens': data['meta']['tokens']['output_tokens']}
            print(f"INPUT_TOKENS:{dict_respuesta['input_tokens']}\nOUTPUT_TOKENS:{dict_respuesta['output_tokens']}\n\n")
            return dict_respuesta
        else:
            raise Exception(f'Error HTTP {response.status_code}')
    except Exception as error:
        print('Error:', error)
        raise error


def get_historial_formateado_comand_r():
    # Esta función devuelve el historial formateado según se necesite en la API de command R
    historial_path = 'historial_chat.json'
    historial_formateado = []

    with open(historial_path, 'r') as f:
        historial = json.load(f)

    for diccionario in historial:
        if diccionario['es_bot']:
            nuevo_diccionario = {"role":"CHATBOT", "message": diccionario["mensaje"]}
        else:
            nuevo_diccionario = {"role":"USER", "message": diccionario["mensaje"]}
        historial_formateado.append(nuevo_diccionario)

    return historial_formateado # retorna el historial sin el ultimo mensaje


def get_historial():
    historial_path = 'historial_chat.json'

    with open(historial_path, 'r') as f:
        historial = json.load(f)
        return historial


def agregar_a_historial(mensaje_texto, contacto, es_bot):
    historial_path = 'historial_chat.json'

    with open(historial_path, 'r') as f: # 'historialchat.json' siempre estará ahí
        historial = json.load(f)

    if es_bot:
        historial.append({'mensaje': mensaje_texto, "es_bot": es_bot})
    else:
        if len(historial) > 0:
            if historial[-1]["es_bot"]:
                historial.append({"mensaje": f"{contacto}: {mensaje_texto}", "es_bot": False})
            else:
                historial[-1]['mensaje'] += f'\n{contacto}: {mensaje_texto}'

        else:
            historial.append({'mensaje': f"{contacto}: {mensaje_texto}", "es_bot": False})

    with open(historial_path, 'w') as f:
        json.dump(historial, f, indent=4)


def colocar_en_world_building(texto):
    try:
        with open("world_building.txt", "w") as archivo:
            archivo.write(texto + "\n")
    except Exception as e:
        print("Error al escribir en el archivo:", e)


def colocar_en_eventos_clave(texto):
    try:
        with open("eventos_clave.txt", "w") as archivo:
            archivo.write(texto + "\n")
    except Exception as e:
        print("Error al escribir en el archivo:", e)


def get_world_building():
    try:
        with open("world_building.txt", "r") as archivo:
            texto = archivo.read()
        return texto
    except Exception as e:
        print("Error al leer el archivo:", e)
        return None


def get_eventos_clave():
    try:
        with open("eventos_clave.txt", "r") as archivo:
            texto = archivo.read()
        return texto
    except Exception as e:
        print("Error al leer el archivo:", e)
        return None


def se_ha_generado_partida():
    historial = get_historial()
    generado = False

    for dicc in historial:
        if "Radhe: /generar-partida" in dicc['mensaje']:
            return True

    return generado

def text_to_json(text):
    if not any(line.strip().startswith(":") for line in text.splitlines()):
        print("Error: texto no tiene estructura de clave-valor")
        return {}

    result = {}
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        key, _, value = line.partition(":")
        try:
            result[key] = int(value)
        except ValueError:
            print(f"Error: valor '{value}' no válido en línea '{line}'")
            continue

    return result


if __name__ == '__main__':
    generada = se_ha_generado_partida()
    print("\n\nSE HA GENERADO PARTIDA:", generada, "\n\n")

    app.run(debug=True)

