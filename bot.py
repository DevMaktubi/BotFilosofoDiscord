import os

import discord
import io
import aiohttp
from PIL import Image, ImageDraw, ImageFont
import requests
import shutil
import textwrap
from dotenv import load_dotenv

import re

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()


async def downloadIMG(imgurl):
    filename = imgurl.split("/")[-1]

    r = requests.get(imgurl, stream=True)

    if r.status_code == 200:
        r.raw.decode_content = True

        with open(filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)
        return filename
    else:
        print("Não deu pra baixar a imagem...")
        return None

    # font = ImageFont.truetype("Pillow/Tests/fonts/FreeMono.ttf", 40)
    # d = ImageDraw(out)


async def alterIMG(filename, frase, autor, color):
    image = Image.open(filename)
    base = image.resize((960, 720))
    width, height = base.size

    font = ImageFont.truetype(
        "Pillow/Tests/fonts/arial.ttf", 60)

    Fillregex = r"(?:#)(?:[a-fA-F0-9]{3,6})\b"

    if (not(re.search(Fillregex, color))):
        fill = '#d9a3d8'
    else:
        fill = color

    d = ImageDraw.Draw(base)

    text = f'"{frase}"'
    text2 = f'-{autor}'

    d.text(xy=((width/2) - 400, height/2), text=textwrap.fill(text, 25),
           font=font, fill=fill)
    d.text(xy=((width/2), height - 100),
           text=textwrap.fill(text2, 20), font=font, fill=fill)

    newfilename = 'alteredimg.jpg'
    # out = Image.alpha_composite(base, txt)

    base.save(newfilename)
    os.remove(filename)
    return newfilename


@ client.event
async def on_ready():
    print(f'{client.user} conectado!')


@ client.event
async def on_message(message):
    if(message.author.bot == True):
        return

    mensagem = message.content
    regex = r"(^[A-Za-z0-9À-ÿ ,.]{5,50}\;[A-Za-z0-9À-ÿ ,.]{2,16}(;#[0-9a-fA-F]{6})?$)|^.*\.(jpg|JPG|jpeg|png|PNG|JPEG)$"
    if mensagem.startswith('$'):
        channel = message.channel
        msg = mensagem[1:]
        if(not(re.search(regex, msg))):
            await channel.send(f'Exemplo de comando: \n $Philosopher é um deus;PhilosopherBOT;#ffff00 (para escolher a cor em HEXADECIMAL) e a foto anexada na mensagem.')
            return

        frase = msg.split(';')[0]
        autor = msg.split(';')[1]
        color = msg.split(';')[2]
        print(color)

        if(len(message.attachments) == 1):
            my_url = message.attachments[0].url
            try:
                filename = await downloadIMG(my_url)
            except:
                print("Imagem não tem URL ou é inválida")
            finalIMG = await alterIMG(filename, frase, autor, color)
            await channel.send(file=discord.File(finalIMG))
            os.remove(finalIMG)
            return

        await channel.send(f'"{frase}" \n -{autor}')


client.run(TOKEN)
