import os

import openai
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
