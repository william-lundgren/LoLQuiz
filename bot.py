import asyncio
import discord
import os
import random
from PIL import Image
import time

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


def find_leaderboard_top(player_scores, n):
    top_n = []
    for key in player_scores.keys():
        broken = False
        if len(top_n) == 0:
            top_n.append(key)
        else:
            for i, ele in enumerate(top_n):
                if player_scores.get(key) > player_scores.get(ele):
                    top_n.insert(i, key)
                    broken = True
                    break
            if not broken:
                top_n.append(key)

    string = ""

    for i, ele in enumerate(top_n[:n]):
        if i == 0:
            string += f":first_place: - {ele} - {player_scores.get(ele)} pts\n"
        elif i == 1:
            string += f":second_place: - {ele} - {player_scores.get(ele)} pts\n"
        elif i == 2:
            string += f":third_place: - {ele} - {player_scores.get(ele)} pts\n"
        else:
            string += f"{i + 1} - {ele} - {player_scores.get(ele)} pts\n"
    return string


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Start of quiz
    if message.content.startswith('$quiz'):
        leaderboard = {}
        questions = 5
        time_per_guess = 15.0

        for i in range(questions):
            img = Images.select_picture()
            champ, ability, ability_id = decode(img)

            # TODO Maybe fix resize images

            direc = f"./Ability_images/{img}"
            if len(leaderboard.keys()) > 0:
                # TODO fix and sort for more players

                e = discord.Embed(title=f"Question number {i + 1} of {questions}", description=f"__**Leaderboard:**__\n {find_leaderboard_top(leaderboard, 2)}")
            else:
                e = discord.Embed(title=f"Question number {i + 1} of {questions}", description="Guess the ability. Either name of ability or champion and what ability (p, q, w, e, r)")

            e.set_thumbnail(url=f"attachment://{''.join(img.split('%'))}")
            file = discord.File(direc, filename=img)
            await message.channel.send(embed=e, file=file)

            def check(m):
                return m.author != client.user

            try:
                Images.guess = await client.wait_for("message", check=check, timeout=time_per_guess)
                start = time.time()
            except asyncio.TimeoutError:
                # print(f"Timeout, answered?: {Images.answered}")
                await message.channel.send(f"Sorry you took too long, answer was {ability} ({champ} {ability_id.upper()})")
                continue

            while True:
                if check_answer(Images.guess.content, champ, ability, ability_id):
                    if Images.guess.author.mention in leaderboard:
                        leaderboard[Images.guess.author.mention] += 1
                    else:
                        leaderboard[Images.guess.author.mention] = 1
                    await message.channel.send(f"Correct! {Images.guess.author.mention}")
                    break
                else:
                    # TODO change to reaction instead
                    await message.channel.send(f"Not quite right, dummy.")

                    try:
                        Images.guess = await client.wait_for("message", check=check, timeout=time_per_guess - (time.time()-start))
                    except asyncio.TimeoutError:
                        await message.channel.send(f"Sorry you took too long, answer was {ability} ({champ} {ability_id.upper()})")
                        break

        e = discord.Embed(title=f"Game finished! Results:", description=f"__**Leaderboard:**__\n {find_leaderboard_top(leaderboard, 2)}")
        await message.channel.send(embed=e)

    return

with open("code.txt", "r") as f:
    code = f.readline()
client.run(code)
