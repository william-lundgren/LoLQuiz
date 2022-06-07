import asyncio
import discord
import os
import random
from PIL import Image

client = discord.Client()


class Images:
    available = os.listdir('./Ability_images')
    answered = False
    guess = None
    correct = False
    champ, ability, ability_id = "Empty", "Empty", "Empty"
    result = False

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
            # FIXME add acceptable answers without '
            champ_name = champ_name.replace("%27", "'")

        ability = " ".join(ability.split("_")[1:])

        if "%27" in ability:
            ability = ability.replace("%27", "'")
        if "%21" in ability:
            ability = ability.replace("%21", "!")

    return champ_name, ability, ability_id


def check_answer(answer, champ_name, ability, ability_id):
    # TODO
    # add acceptable answer like ult and ultimate for r and pass and passive for p (maybe also 1,2,3,4)
    # Make a dict of acceptable answers with "correct" ability as key and list of all valid answers as value
    # Also add to make sure q w e r works. is in ability name ust need to change decode method maybe
    # TODO Add a boolean for if only name and add to if statements. To get bonus point only if you know the whole name
    try:
        if answer.lower() == ability.lower() or ability.lower() in answer.lower():
            return True

        # Add acceptable answer for qwer instead of only name

        # If guess is on form champ id or id champ and champ name is without space
        if len(answer.split()) == 2 and len(champ_name.split()) == 1:
            if answer.split()[0].lower() == ability_id.lower() and champ_name.lower() == answer.split()[1].lower():
                return True
            if answer.split()[1].lower() == ability_id.lower() and champ_name.lower() == answer.split()[0].lower():
                return True

            # Add acceptable answers for passive
            if ability_id.lower() == "p" and answer.split()[0].lower() == ("pass" or "passive") and answer.split()[1].lower() == champ_name.lower():
                return True
            if ability_id.lower() == "p" and answer.split()[1].lower() == ("pass" or "passive") and answer.split()[0].lower() == champ_name.lower():
                return True

            # Add acceptable answers for R
            if ability_id.lower() == "r" and answer.split()[1].lower() == ("ult" or "ulti" or "ultimate") and answer.split()[0].lower() == champ_name.lower():
                return True
            if ability_id.lower() == "r" and answer.split()[0].lower() == ("ult" or "ulti" or "ultimate") and answer.split()[1].lower() == champ_name.lower():
                return True

        # If guess is on form champ id or id champ and champ name is with space
        elif len(answer.split()) > 2 and len(champ_name.split()) > 1:
            if answer.split()[0].lower() == ability_id.lower() and champ_name.lower() == " ".join(answer.split()[1:]).lower():
                return True
            if answer.split()[-1].lower() == ability_id.lower() and champ_name.lower() == " ".join(answer.split()[:2]).lower():
                return True

            # Add acceptable answers for passive
            # TODO fix so it work with this stuff like above too
            if ability_id.lower() == "p" and answer.split()[0].lower() == ("pass" or "passive") and answer.split()[1].lower() == champ_name.lower():
                return True
            if ability_id.lower() == "p" and answer.split()[1].lower() == ("pass" or "passive") and answer.split()[0].lower() == champ_name.lower():
                return True

            # Add acceptable answers for R
            if ability_id.lower() == "r" and answer.split()[1].lower() == ("ult" or "ulti" or "ultimate") and answer.split()[
                0].lower() == champ_name.lower():
                return True
            if ability_id.lower() == "r" and answer.split()[0].lower() == ("ult" or "ulti" or "ultimate") and answer.split()[
                1].lower() == champ_name.lower():
                return True

    except IndexError:
        print(answer, "Error")

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    print(f"Received message, \"{message.content}\"")
    # FIXME Find a better solution for reference before assignment

    if message.author == client.user:
       # print("Yup thats myself", message.content)
        return

    valid_guess = True

    if message.content.startswith('$ability-quiz'):
        Images.answered = False
        Images.checked = False
        Images.result = False
        img = Images.select_picture()
        Images.champ, Images.ability, Images.ability_id = decode(img)

        # TODO Maybe fix resize images
        await message.channel.send(file=discord.File(f"./Ability_images/{img}"))

    def check(m):
        return m.author == message.author

    try:
        Images.guess = await client.wait_for("message", check=check, timeout=10.0)
        if Images.guess.content == "$ability-quiz":
            valid_guess = False
        if len(Images.guess.content) > 0:
            Images.answered = True

    # FIXME Make sure it only returns this if there hasnt been an answer
    except asyncio.TimeoutError:
        #print(f"Timeout, answered?: {Images.answered}")
        if not Images.answered and Images.ability != "Empty":
            Images.guess = None
            return await message.channel.send(f"Sorry you took too long, answer was {Images.ability} ({Images.champ} {Images.ability_id.upper()})")

    if Images.guess is not None and valid_guess:
        if check_answer(Images.guess.content, Images.champ, Images.ability, Images.ability_id) and not Images.result:
            await message.channel.send("Correct!")
            Images.correct = True
            Images.result = True
        elif not Images.correct and Images.ability != "Empty" and not Images.result:
            Images.result = True
            await message.channel.send(f"Not quite right, dummy. Answer was {Images.ability} ({Images.champ} {Images.ability_id.upper()})")


client.run('OTgwMjEwMzE0OTcwODA0MjM0.GtfPd6.42R2Uud802J6gsh0DxSztzDRKoHhWvCZaE8QCA')
