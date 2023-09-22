import os
import re
from urllib.request import urlopen, Request

import requests
from bs4 import BeautifulSoup
import openai
from dotenv import load_dotenv
from openai.openai_object import OpenAIObject

load_dotenv()

openai.api_type = "azure"
openai.api_base = "https://ai-vri-openai.openai.azure.com/"
openai.api_version = "2023-07-01-preview"
openai.api_key = os.getenv("OPENAI_API_KEY")

messages = [{"role": "system",
             "content": "Du er en AI-assistent som skal hjelpe brukeren med sanntidsinnformasjon. Du har tilgang til oppdatert innformasjon på internett"
                        " med å bruke skriptet"
                        "Hvis de første bokstavene i meldingen du sender er 'skript', så vil et skript evalueres og kjøres."
                        "Brukeren kan ikke kjøre noen av skriptene selv så de må du som AI-assistent kjøre.What a"
                        "Husk å gi et svar til brukeren etter at skripet er ferdig."
                        "Dine er 'skript:', så vil et skript kjøres som gir deg mer informasjon "
                        "internett for å hente informasjon i sanntid med å skrive meldingen \"skript:http_get("
                        "'https://example.com')\". Skriptet gir deg teksten fra nettsiden uten html"
                        "Bruk værdata fra \"skript:weather(lat,lon)\". Hvis det er noe som du ikke har kjennskap til, som "
                        "kan kreve sanntidstidsinnformasjon så kan du bruke \"skript:search('search terms')\" for å få ett"
                        "treff på internett som kan ha relevanse"},
            {"role": "user", "content": "hva er siste nytt på vg"},
            {"role": "assistant", "content": "skript:http_get(\"https://vg.no\")"},
            {"role": "user", "content": "hva blir været i Oslo?"},
            {"role": "assistant", "content": "skript:weather(59.91,10.76)"}
            ]


def weather(lat: float, lon: float) -> str:
    weather = internal_http_get(
        f'https://api.open-meteo.com/v1/forecast?latitude={lat}1&longitude={lon}&current_weather=true&hourly=temperature_2m')
    return "her er den. Bruk dataen og oppsumer for brukeren " + weather


def search(keyword: str):
    keyword = re.sub('\s', "+", keyword)

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:84.0) Gecko/20100101 Firefox/84.0",
    }

    page = requests.get(f'https://duckduckgo.com/html/?q={keyword}', headers=headers).text
    soup = BeautifulSoup(page, 'html.parser').find_all("a", class_="result__url", href=True)
    if soup:
        return "her er det første resultatet jeg fant " + internal_http_get(soup[0]['href'])
    return "jeg fant ikke resultater om dette"


def http_get(url: str) -> str:
    return "her er infoen. Bruk denne for å svare på brukerens forespørsel: " + internal_http_get(url)


def handle_incoming_message(message: str) -> None:
    messages.append({"role": "user", "content": message})
    msg2 = execute_chat_completion(messages)
    if len(msg2) >= 7 and msg2[:7] == 'skript:':
        internet_context: dict = {"role": "user", "content": eval(msg2[7:])}
        msg3 = execute_chat_completion(messages + [internet_context])
        messages.append({"role": "assistant", "content": msg3})
        print(msg3)
    else:
        messages.append({"role": "assistant", "content": msg2})
        print(msg2)


def execute_chat_completion(messages: list[dict]) -> str:
    response: OpenAIObject = openai.ChatCompletion.create(
        engine="gpt-35-turbo",
        messages=messages,
        temperature=0.25,
        max_tokens=876,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None)
    return response.choices[0].message.content


def internal_http_get(url) -> str:
    req = Request(url)
    html = urlopen(req).read()
    soup = BeautifulSoup(html, features="html.parser")

    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()  # rip it out

    # get text
    text = soup.get_text()

    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)

    return text


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    while True:
        msg = input("skriv til internettGPT: ")
        handle_incoming_message(msg)
