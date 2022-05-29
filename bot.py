import asyncio
import discord
import os
import random

client = discord.Client()


class Images:
    available = os.listdir('./Ability_images')

    @staticmethod
    def select_picture():
        ind = random.randrange(0, len(Images.available))
        ability = Images.available[ind]
        Images.available.pop(ind)

        return ability


def decode(ability):
    space = False

    space_champs = ['Aurelion_Sol', 'Dr._Mundo', 'Jarvan_IV', 'Lee_Sin', 'Master_Yi', 'Miss_Fortune',
                    'Renata_Glasc', 'Tahm_Kench', 'Twisted_Fate', 'Xin_Zhao']

    # Strip ending and do right thing for mundo
    if ability.split("_")[0] != "Dr.":
        ability = ability.split(".")[0]
    else:
        ability = ".".join(ability.split(".")[:2])

    # Determine if champ has space in it
    for champ in space_champs:
        if champ in ability:
            space = True

    if space:
        words = ability.split("_")
        champ_name = " ".join(words[0:2])

        ability = " ".join(words[2:])

        if "%27" in ability:
            ability = ability.replace("%27", "'")
        if "%21" in ability:
            ability = ability.replace("%21", "!")
    else:
        # FIXME when ability letter in name
        champ_name = ability.split("_")[0]
        if "%27" in champ_name:
            # FIXME add acceptable answers without '
            champ_name = champ_name.replace("%27", "'")

        ability = " ".join(ability.split("_")[1:])

        if "%27" in ability:
            ability = ability.replace("%27", "'")
        if "%21" in ability:
            ability = ability.replace("%21", "!")

    return champ_name, ability


def check_answer(answer, champ, ability):
    if answer.lower() == ability.lower():
        return True


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    champ, ability = "Empty", "Empty"

    if message.author == client.user:
        return

    if message.content.startswith('$ability-quiz'):
        img = Images.select_picture()
        champ, ability = decode(img)
        print(ability)

        await message.channel.send(file=discord.File(f"./Ability_images/{img}"))

    def check(m):
        return m.author == message.author

    try:
        guess = await client.wait_for("message", check=check, timeout=10.0)
    except asyncio.TimeoutError:
        return await message.channel.send(f"Sorry you took too long, answer was {ability}")

    if check_answer(guess.content, champ, ability):
        await message.channel.send("Correct!")
    else:
        await message.channel.send(f"Not quite right, dummy. Answer was {ability}")

client.run('OTgwMjEwMzE0OTcwODA0MjM0.GtfPd6.42R2Uud802J6gsh0DxSztzDRKoHhWvCZaE8QCA')
