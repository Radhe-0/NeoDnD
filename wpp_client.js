const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const fetch = require('node-fetch');

const client = new Client({
    authStrategy: new LocalAuth(),
    webVersionCache: {
        type: 'remote',
        remotePath: 'https://raw.githubusercontent.com/wppconnect-team/wa-version/main/html/2.2412.54.html',
    },
});
const ID_CHAT = "";

client.on('ready', () => {
    console.log('¡Cliente listo!');
});


client.on('qr', qr => {
    qrcode.generate(qr, { small: true });
});


client.on('message_create', async (message) => {
    const chat = await message.getChat();
    const mensaje_texto = message.body;
    const contacto = await message.getContact();
    const contacto_nombre = contacto.name;

    console.log(`${contacto_nombre}: ${mensaje_texto}`);

    if (chat.id.user = ID_CHAT) { 
        let respuesta = await nuevo_mensaje(mensaje_texto, contacto_nombre);
        console.log(`respuesta: ${respuesta["mensaje"]}, ${respuesta["responde"]}`)

        if (respuesta["responde"]) {
            message.reply(respuesta['mensaje'])
        }

        if (respuesta["doble"]) {
            console.log('\n\nAAAAAAAAAAAAAAAAAAAAAAAAAA')
            chat.sendMessage(respuesta['mensaje2'])
            
        }
    }
});


async function nuevo_mensaje(mensaje, contacto) {
    let es_bot = false;

    if (!contacto) {
        es_bot = true;
        contacto = "";
    }

    const data = {
        mensaje_texto: mensaje,
        contacto: contacto,
        es_bot: es_bot
    };

    try {
        const response = await fetch('http://127.0.0.1:5000/mensaje_nuevo', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });


        if (response.ok) {
            const responseData = await response.json();
            return responseData;

        } else {
            console.error('a. Error al enviar mensaje a la API:', response.status);
        }
    } catch (error) {
        console.error('b. Error al enviar mensaje a la API:', error);
    }
}

client.initialize();
