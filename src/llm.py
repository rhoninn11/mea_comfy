
from typing import Optional, Sequence, List
import ollama

from enum import Enum

from ollama import chat

from utils import proj_asset, Proj
from proto.ollama_pb2 import *


class SimpleChat():
    msg_list: list[Message]
    counter: dict[Role, int] = {}
    
    def add_ai_resp(self, text: str):
        llm_msg = Message(role = Role.assistant, tokens=text)
        self.msg_list.append(llm_msg)

    def render(self) -> tuple[list[dict[str, any]], bool]:
        ollama_list: list = []
        for msg in self.msg_list:
            ollama_msg = {'role': Role.Name(msg.role), 'content': msg.tokens}
            ollama_list.append(ollama_msg)
        return ollama_list


def spaw_chat() -> SimpleChat:
    proto_list: list[Message] = []

    proto_list.append(Message(
        role=Role.system,
        tokens="As for now moment your role is uncpecified",
    ))

    proto_list.append(Message(
        role=Role.user,
        tokens="Tell me some story from your life in the province",
    ))
    sch = SimpleChat()
    sch.msg_list = proto_list
    return sch

def ollama_run(model_name, chat_to_process):
    return chat(
        model=model_name,
        messages=chat_to_process,
        stream=True
    )
import time
def ollama_process(ollama_stream):
    tokens = []
    last = time.perf_counter()
    every_s = 0.2
    for chunk in ollama_stream:
        token = chunk["message"]["content"]
        tokens.append(token)
        now = time.perf_counter()
        delta = now - last
        if delta > every_s:
            yield tokens
            tokens = []
            last += every_s
 
def pick_model() -> str:
    models: list = ollama.list().models
    prefered_model: str = "deepseek-r1:32b"

    for model_bucket in models:
        if model_bucket.model == prefered_model:
            return prefered_model
        
    if len(models) == 0:
        print("!!! no models, exit. Install something with \"ollama pull MODEL_NAME\"")
        raise IndexError()

    name = models[0].model
    return name

def main(): 
    proj = Proj("llm")

    samples = [ proj.asset("image_a.png"),
                proj.asset("image_b.png")]

    cultural_heritage_chat: SimpleChat = spaw_chat()
    model_name = pick_model()
    print(f"+++ starting with model {model_name}")
    
    ollama_input = cultural_heritage_chat.render()
    ollama_stream = ollama_run(model_name, ollama_input)
    all_tokens = []
    for tokens in ollama_process(ollama_stream):
        all_tokens.extend(tokens)
        print("".join(tokens))

    cultural_heritage_chat.add_ai_resp("".join(all_tokens))
