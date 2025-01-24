
from typing import Optional, Sequence, List
import ollama

from enum import Enum
from pydantic import BaseModel

from ollama import chat

from utils import proj_asset, Proj

class Role(str, Enum):
    SYSTEM = "system"
    USER = "user"
    AI = "assistant"

ROLES = [Role.SYSTEM, Role.USER, Role.AI]

class Message(BaseModel):
    role: Role
    content: str
    images: Optional[Sequence[str]] = None

    class Config:
        use_enum_values = True

class SimpleChat(BaseModel):


    msg_list: list[Message]
    counter: dict[Role, int] = {}
    finished: bool = False
    
    def add_ai_resp(self, text: str):
        ai_msg = Message(
            role=Role.AI,
            content=text
        )
        self.msg_list.append(ai_msg)

    def render(self) -> tuple[list[dict[str, any]], bool]:
        out_list: list = []
        for msg in self.msg_list:
            out_list.append(msg.model_dump())
        finish = self.finished
        self.finished = True
        return out_list, finish


class ChatFmt:
    data: str = ""        

def spaw_chat(chat: ChatFmt, samples: list[str]) -> SimpleChat:
    msg_list = []

    sys = Message(
        role=Role.SYSTEM,
        content="As for now moment your role is uncpecified",
    )
    msg_list.append(sys)

    # usr = Message(
    #     role=Role.USER,
    #     content="I have for you one picture",
    #     images=[samples[0]]
    # )
    # msg_list.append(usr)
    
    # usr = Message(
    #     role=Role.USER,
    #     content="I and the second one of course",
    #     images=[samples[1]]
    # )
    # msg_list.append(usr)

    usr = Message(
        role=Role.USER,
        content="Tell me some story from your life in the province",
    )
    msg_list.append(usr)
    return SimpleChat(msg_list=msg_list)

def ollama_process(model_name, chat_to_process, v=False):

    stream = chat(
        model=model_name,
        messages=chat_to_process,
        stream=True
    )

    tokens = []
    for chunk in stream:
        token = chunk["message"]["content"]
        if v:
            print(token, end='', flush=True)
        tokens.append(token)

    return "".join(tokens)
 
def pick_model() -> str:
    models: list = ollama.list().models
    prefered_model: str = "llava-lama3"

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

    model_name = pick_model()
    print(f"+++ starting with model {model_name}")

    cultural_heritage_chat = spaw_chat(None, samples)
    
    while True:
        ollama_input, finished = cultural_heritage_chat.render()
        if finished:
            break
        ai_message = ollama_process(model_name, ollama_input)
        cultural_heritage_chat.add_ai_resp(ai_message)
        print("---")
        print(ai_message)
