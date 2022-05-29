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

    links = []
    used_abilities = []

    for skill in skills:
        imgs = skill.find_all("img")
        for i in imgs:
            if i.get("data-src") is not None and champ_name in i.get("data-src") and i.get("alt").split(".")[0] not in used_abilities and "scale" not in i.get("data-src"):
                links.append(i.get("data-src"))
                used_abilities.append(i.get("alt").split(".")[0])

    for i in links:
        urllib.request.urlretrieve(i, f"Ability_images/{i.split('/')[-3]}")


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
