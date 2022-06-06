import requests
from bs4 import BeautifulSoup as bs
import urllib.request


def check_valid_link(url):
    response = requests.get(url)
    html = response.content
    soup = bs(html, "lxml")
    paras = soup.find_all("a")
    tester = [l.get("title") for l in paras if l.get("title") is not None]

    for i in tester:
        if "Special:Search/" in i:
            print("Invalid link")
            print(url)


def find_abilities(url):
    split_url = url.split("/")
    champ_name = split_url[split_url.index("wiki") + 1]

    response = requests.get(url)
    html = response.content
    soup = bs(html, "lxml")

    skills = soup.select("div.skill")

    exclude = ["Aphelios", "Elise", "Gnar", "Jayce", "Jhin", "Kalista", "Kled",
               "Nidalee", "Rek%27Sai", "Renata_Glasc", "Senna", "Zeri"]
    if champ_name not in exclude:
        prnt = ""
        for i in skills:
            try:
                prnt += i.get("class")[1] + " "
            except IndexError:
                print(champ_name, i.get("class"))

        if prnt != "skill_innate skill_q skill_w skill_e skill_r ":
            print(champ_name, prnt)

    links = {}
    used_abilities = []

    # TODO
    # Deal with excluded champs in a good way. Maybe hard code for ease
    if champ_name not in exclude:
        for skill in skills:
            ability = None
            try:
                ability = skill.get("class")[1].split("_")[1]
                if ability == "innate":
                    ability = "p"
            except IndexError:
                print("Error with index", skill.get("class"))

            imgs = skill.find_all("img")
            for i in imgs:

                # Check that image not already used and isnt a small picture and that it is a champion image
                if i.get("data-src") is not None and champ_name in i.get("data-src") and i.get("alt").split(".")[0] not in used_abilities \
                        and "scale" not in i.get("data-src") and champ_name not in exclude and ability is not None:

                    # Add links as keys to the dict with the ability 'tag' as value
                    links[i.get("data-src")] = ability
                    used_abilities.append(i.get("alt").split(".")[0])

    for i in links.keys():
        ability = links.get(i)
        # TODO
        # Use this code for later idk when (to get rid of numbers in dup abilities)
        #if any(i.isdigit() for i in links):
        #    ability = ability[:-2]
        urllib.request.urlretrieve(i, f"Ability_images/{ability.upper()}_{i.split('/')[-3]}")


def test():
    t = open("exceptions.txt", "r")
    for i in t.readlines():
        print(f"\"{i.split()[0]}\"", end=", ")

    t.close()


def main():
    links = []

    with open("champ_names.txt", "r") as file:
        for i in file.readlines():
            champ = i[:-1]
            if " " in champ:
                champ = champ.split()
                if champ[0] != "Jarvan":
                    champ[1] = champ[1].capitalize()
                else:
                    champ[1] = champ[1].upper()
                champ = "_".join(champ)

            if "\'" in champ:
                champ = champ.split("\'")
                champ[1] = champ[1].capitalize()
                champ = "%27".join(champ)

            url = f"https://leagueoflegends.fandom.com/wiki/{champ}/LoL"
            links.append(url)

    for i in links:
        find_abilities(i)


if __name__ == "__main__":
    main()
