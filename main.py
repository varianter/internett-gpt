import os
from urllib.request import Request, urlopen

import openai
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai.openai_object import OpenAIObject

load_dotenv()

openai.api_type = "azure"
openai.api_base = "https://ai-vri-openai.openai.azure.com/"
openai.api_version = "2023-07-01-preview"
openai.api_key = os.getenv("OPENAI_API_KEY")


def handle_incoming_message(message: str) -> None:
    # implementer i del 1
    pass


# Metoden tar imot en liste med dict. dictene har verdiene med role : user/assitant/system og content: din melding
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


if __name__ == '__main__':
    while True:
        msg = input("skriv til internettGPT: ")
        handle_incoming_message(msg)


# Under er hjelpemetoder som kan være relevant i del 2

def http_get(url: str) -> str:
    return internal_http_get(url)


def weather(lat: float, lon: float) -> str:  # Kaller et public api med værdata
    return internal_http_get(
        f'https://api.open-meteo.com/v1/forecast?latitude={lat}1&longitude={lon}&current_weather=true&hourly=temperature_2m')


def search(keyword: str):  # Finner første søkeresultat på duckduckgo.com og gir en oppsummering på dette
    keyword = re.sub('\s', "+", keyword)

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:84.0) Gecko/20100101 Firefox/84.0",
    }  # Her emulerer vi en brukeragent for å få lov til å gjennomføre søket. Ikke gjør dette i produksjon

    page = requests.get(f'https://duckduckgo.com/html/?q={keyword}', headers=headers).text
    soup = BeautifulSoup(page, 'html.parser').find_all("a", class_="result__url", href=True)
    if soup:
        return internal_http_get(soup[0]['href'])
    return "ingen treff"


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
