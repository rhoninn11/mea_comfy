
from typing import Optional, Sequence, List
import ollama

from enum import Enum

from ollama import chat

from utils import proj_asset, Proj, Timeline
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

def warmup_chat() -> SimpleChat:
    init = Message(
        role=Role.user,
        tokens="Just and only say 'hi', thats all:D",
    )
    sch = SimpleChat()
    sch.msg_list = [init] 
    return sch

def main_chat() -> SimpleChat:
    proto_list: list[Message] = []

    proto_list.append(Message(
        role=Role.system,
        tokens="As for now moment your role is uncpecified",
    ))

    with open("src/llm.py", "r") as fd:
        code = fd.read()

    proto_list.append(Message(
        role=Role.user,
        tokens=f"can i ask you to explain this code?\n{code}\n do you know its part of your provess?",
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
            times = int(delta/every_s)
            last += every_s * times
            tokens = []
 
def pick_model() -> str:
    models: list = ollama.list().models
    prefered_model: str = "deepseek-r1:70b"

    for model_bucket in models:
        if model_bucket.model == prefered_model:
            return prefered_model
        
    if len(models) == 0:
        print("!!! no models, exit. Install something with \"ollama pull MODEL_NAME\"")
        raise IndexError()

    name = models[0].model
    return name

def ollama_streaming(ollama_stream):
    tokens = []

    start = time.perf_counter()
    for chunk in ollama_process(ollama_stream):
        print("".join(chunk), end="", flush=True)
        tokens.extend(chunk)
    print("")

    end = time.perf_counter()
    s_elapsed = (end - start)
    token_size = len(tokens)
    speed = token_size/s_elapsed
    print(f"tokens {token_size}, speed {speed} t/s, time {s_elapsed} s")
    return tokens

def chat_with_ollama(model_name, active_chat: SimpleChat) -> SimpleChat:
    ollama_input = active_chat.render()
    ollama_stream = ollama_run(model_name, ollama_input)
    all_tokens = ollama_streaming(ollama_stream)
    active_chat.add_ai_resp("".join(all_tokens))
    return active_chat

def main(): 
    proj = Proj("llm")
    INIT = True

    # samples = [ proj.asset("image_a.png"),
    #             proj.asset("image_b.png")]

    model_name = pick_model()
    if INIT:
        print(f"+++ starting with model {model_name}")
        chat_with_ollama(model_name, warmup_chat())

    main_convo = chat_with_ollama(model_name, main_chat())
    main_convo.msg_list.append(Message(
        role=Role.user,
        tokens="In which direction develop this code to create something unsusual with that?"
    ))
    chat_with_ollama(model_name, main_convo)

    
