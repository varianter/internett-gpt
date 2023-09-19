import os
from urllib.request import urlopen
from bs4 import BeautifulSoup
import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_type = "azure"
openai.api_base = "https://ai-vri-openai.openai.azure.com/"
openai.api_version = "2023-07-01-preview"
openai.api_key = os.getenv("OPENAI_API_KEY")

messages = [{"role": "system",
             "content": "Du er en AI-assistent som har et skript som skal hjelpe deg når du trenger tillgang til internett for å hente informasjon i sanntid med å skrive meldingen \"skript:http_get('https://example.com')\". Vent med å svare brukeren til du har fått svar fra skript kallet. Ettersom du er i 2023 bør du bruke dette skriptet for å få oppdatert informasjon."},
            {"role": "user", "content": "hva er siste nytt på vg"},
            {"role": "assistant", "content": "skript:http_get(\"https://vg.no\")"},
            {"role": "user", "content": "hva er siste nytt på tv2?"}]

response = openai.ChatCompletion.create(
    engine="gpt-35-turbo",
    messages=messages,
    temperature=0.25,
    max_tokens=876,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
    stop=None)


def http_get(url):
    html = urlopen(url).read()
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
    msg: str = response.choices[0].message.content
    if len(msg) >= 7:
        first_six = msg[:7]
        if first_six == 'skript:':
            messages.append({"role": "user", "content": eval(msg[7:])})
            response = openai.ChatCompletion.create(
                engine="gpt-35-turbo",
                messages=messages,
                temperature=0.25,
                max_tokens=876,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None)

    print(response.choices[0].message.content)
