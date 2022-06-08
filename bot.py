import asyncio
import discord
import os
import random
from PIL import Image

client = discord.Client()


class Images:
    available = os.listdir('./Ability_images')

    @staticmethod
    def select_picture():
        ind = random.randrange(0, len(Images.available) // 2) * 2
        ability = Images.available[ind]
        Images.available.pop(ind)

        return ability


def decode(ability):
    space = False

    space_champs = ['Aurelion_Sol', 'Dr._Mundo', 'Jarvan_IV', 'Lee_Sin', 'Master_Yi', 'Miss_Fortune',
                    'Renata_Glasc', 'Tahm_Kench', 'Twisted_Fate', 'Xin_Zhao']

    # Strip ending and do right thing for mundo
    if ability.split("_")[1] != "Dr.":
        ability = ability.split(".")[0]
    else:
        ability = ".".join(ability.split(".")[:2])

    # Determine if champ has space in it
    for champ in space_champs:
        if champ in ability:
            space = True

    ability_id = ability.split("_")[0]
    ability = "_".join(ability.split("_")[1:])

    if space:
        words = ability.split("_")
        champ_name = " ".join(words[0:2])
        ability = " ".join(words[2:])
        if "%27" in ability:
            ability = ability.replace("%27", "'")
        if "%21" in ability:
            ability = ability.replace("%21", "!")
    else:
        champ_name = ability.split("_")[0]
        if "%27" in champ_name:
            champ_name = champ_name.replace("%27", "'")

        ability = " ".join(ability.split("_")[1:])

        if "%27" in ability:
            ability = ability.replace("%27", "'")
        if "%21" in ability:
            ability = ability.replace("%21", "!")

    return champ_name, ability, ability_id


def check_answer(answer, champ_name, ability, ability_id):
    acceptable_answers = {
        "p": ["pass", "passive", "pas"],
        "r": ["ult", "ulti", "ultimate"]
    }
    # TODO Add a boolean for if only name and add to if statements. To get bonus point only if you know the whole name
    try:
        if answer.lower() == ability.lower() or ability.lower() in answer.lower():
            return True
        if len(answer.split()) < len(champ_name.split()) + len(ability_id):
            return False

        if "'" in champ_name:
            # If answer of ' champ is given with space instead of '
            if " ".join(champ_name.split("'")).lower() in answer.lower() and (ability_id.lower() == answer.split()[0].lower() or ability_id.lower() == answer.split()[-1].lower()):
                return True

            # If answer of ' champ is given with nothing instead of '
            if "".join(champ_name.split("'")).lower() in answer.lower() and (ability_id.lower() == answer.split()[0].lower() or ability_id.lower() == answer.split()[-1].lower()):
                return True

        # If guess is on form champ id or id champ and champ name is without space
        if len(answer.split()) == 2 and len(champ_name.split()) == 1:
            if answer.split()[0].lower() == ability_id.lower() and champ_name.lower() == answer.split()[1].lower():
                return True
            if answer.split()[1].lower() == ability_id.lower() and champ_name.lower() == answer.split()[0].lower():
                return True

            # Add acceptable answers for passive
            if ability_id.lower() == "p" and answer.split()[0].lower() in acceptable_answers.get(ability_id.lower()) and answer.split()[1].lower() == champ_name.lower():
                return True
            if ability_id.lower() == "p" and answer.split()[1].lower() in acceptable_answers.get(ability_id.lower()) and answer.split()[0].lower() == champ_name.lower():
                return True

            # Add acceptable answers for R
            if ability_id.lower() == "r" and answer.split()[1].lower() in acceptable_answers.get(ability_id.lower()) and answer.split()[0].lower() == champ_name.lower():
                return True
            if ability_id.lower() == "r" and answer.split()[0].lower() in acceptable_answers.get(ability_id.lower()) and answer.split()[1].lower() == champ_name.lower():
                return True

        # If guess is on form champ id or id champ and champ name is with space
        elif len(answer.split()) > 2 and len(champ_name.split()) > 1:
            if answer.split()[0].lower() == ability_id.lower() and champ_name.lower() == " ".join(answer.split()[1:]).lower():
                return True
            if answer.split()[-1].lower() == ability_id.lower() and champ_name.lower() == " ".join(answer.split()[:2]).lower():
                return True

            # Add acceptable answers for passive
            if ability_id.lower() == "p" and answer.split()[0].lower() in acceptable_answers.get(ability_id.lower()) and " ".join(answer.split()[1:]).lower() == champ_name.lower():
                return True
            if ability_id.lower() == "p" and answer.split()[-1].lower() in acceptable_answers.get(ability_id.lower()) and " ".join(answer.split()[:2]).lower() == champ_name.lower():
                return True

            # Add acceptable answers for R
            if ability_id.lower() == "r" and answer.split()[-1].lower() in acceptable_answers.get(ability_id.lower()) and " ".join(answer.split()[:2]).lower() == champ_name.lower():
                return True
            if ability_id.lower() == "r" and answer.split()[0].lower() in acceptable_answers.get(ability_id.lower()) and " ".join(answer.split()[1:]).lower() == champ_name.lower():
                return True
        return False

    except Exception as e:
        print(answer, "Error", e)
        return False


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    #print(f"Received message, \"{message.content}\"")
    # TODO Find a better solution for reference before assignment

    if message.author == client.user:
        # print("Yup thats myself", message.content)
        return

    if message.content.startswith('$quiz'):
        questions = 3
        for i in range(questions):
            img = Images.select_picture()
            champ, ability, ability_id = decode(img)

            # TODO Maybe fix resize images

            direc = f"./Ability_images/{img}"
            e = discord.Embed(title=f"Question number {i + 1} of {questions}", description="This is test description")
            print(img)
            e.set_image(url=f"attachment://{''.join(img.split('%'))}")
            print(e.image)
            file = discord.File(direc, filename=img)
            await message.channel.send(embed=e, file=file)

            def check(m):
                return m.author == message.author

            try:
                Images.guess = await client.wait_for("message", check=check, timeout=5.0)

            # TODO Make sure it only returns this if there hasnt been an answer
            except asyncio.TimeoutError:
                # print(f"Timeout, answered?: {Images.answered}")
                await message.channel.send(f"Sorry you took too long, answer was {ability} ({champ} {ability_id.upper()})")
                continue

            if check_answer(Images.guess.content, champ, ability, ability_id):
                await message.channel.send("Correct!")
            else:
                await message.channel.send(f"Not quite right, dummy. Answer was {ability} ({champ} {ability_id.upper()})")
    return

client.run('OTgwMjEwMzE0OTcwODA0MjM0.GtfPd6.42R2Uud802J6gsh0DxSztzDRKoHhWvCZaE8QCA')
