import os
import re
from urllib.request import urlopen, Request

import requests
from bs4 import BeautifulSoup
import openai
from dotenv import load_dotenv
from openai.openai_object import OpenAIObject
import datetime

load_dotenv()

openai.api_type = "azure"
openai.api_base = "https://ai-vri-openai.openai.azure.com/"
openai.api_version = "2023-07-01-preview"
openai.api_key = os.getenv("OPENAI_API_KEY")
current_date = datetime.date.today()

messages = [{"role": "system",
             "content": "Du er en vennlig AI-assistent"}
            ]


def weather(lat: float, lon: float) -> str:  # Kaller et public api med værdata
    weather = internal_http_get(
        f'https://api.open-meteo.com/v1/forecast?latitude={lat}1&longitude={lon}&current_weather=true&hourly=temperature_2m')
    return "Takk for at du kjørte skriptet. Her er værdataen fra det. " + weather


def search(keyword: str):  # Finner første søkeresultat på duckduckgo.com og gir en oppsummering på dette
    keyword = re.sub('\s', "+", keyword)

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:84.0) Gecko/20100101 Firefox/84.0",
    }  # Her emulerer vi en brukeragent for å få lov til å gjennomføre søket. Ikke gjør dette i produksjon

    page = requests.get(f'https://duckduckgo.com/html/?q={keyword}', headers=headers).text
    soup = BeautifulSoup(page, 'html.parser').find_all("a", class_="result__url", href=True)
    if soup:
        return "Takk for at du kjørete skriptet. Her er det første treffet. Gi en oppsumering av resultatet til brukeren. " + internal_http_get(
            soup[0]['href'])
    return "jeg fant ikke resultater om dette"


def http_get(url: str) -> str:
    return "Takk for at du kjørte skriptet. Her er resultatene. Vennligst oppsumer disse: " + internal_http_get(url)


def handle_incoming_message(message: str) -> None:
    messages.append({"role": "user", "content": message})
    msg2 = execute_chat_completion(messages)
    print(msg2)
    messages.append({"role": "assistant", "content": msg2})


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


def internal_http_get(url: str) -> str:
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

    return text[:5000]  # Vi kan ikke få all tekst hvis det er veldig mye


if __name__ == '__main__':
    while True:
        msg = input("skriv til internettGPT: ")
        handle_incoming_message(msg)
