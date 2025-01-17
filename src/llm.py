
from typing import Optional, Sequence, List
import ollama

from enum import Enum
from pydantic import BaseModel

from ollama import chat

from utils import proj_asset

class Role(str, Enum):
    SYSTEM = "system"
    USER = "user"
    AI = "assistant"

class Message(BaseModel):
    role: Role
    content: str
    images: Optional[Sequence[str]] = None

    class Config:
        use_enum_values = True

class SimpleChat(BaseModel):
    system: List[Message] = []
    user: list[Message] = []
    ai: list[Message] = []
    
    def add_ai_resp(self, text: str):
        ai_msg = Message(
            role=Role.AI,
            content=text
        )
        self.ai.append(ai_msg)
    
    def render_dialog(self) -> tuple[list[dict[str, any]], bool]:
        msg_list = [self.system[0].model_dump()]
        for i, usr_msg in enumerate(self.user):
            msg_list.append(usr_msg.model_dump())
            if len(self.ai) <= i:
                break
            msg_list.append(self.ai[i].model_dump())

        finished = len(self.user) == len(self.ai)
        return msg_list, finished

        

def about_pic_chat(img_file) -> SimpleChat:
    sys_msg = Message(
        role=Role.SYSTEM,
        content="You are now roleplaing an older man his speach became wise after all this years, "
            "you have some problems with alcohol, not counting some other addictions, "
            "tough lack, as they said. "
            "But allways start your response with \"Oh my dear\" and always try to be speculative",
    )

    usr_msg = Message(
        role=Role.USER,
        content="What do you see on that picture",
        images=[img_file]
    )

    ust_msg_2 = Message(
        role=Role.USER,
        content="Who do you think, could that be? What type of personality would choose to put these on"
    )

    a = SimpleChat(
        system=[sys_msg.model_dump()],
        user=[usr_msg.model_dump(), ust_msg_2.model_dump()],
        ai=[]
    )
    return a

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
    models = ollama.list().models
    if len(models) == 0:
        print("!!! no models, exit. Install something with \"ollama pull MODEL_NAME\"")

    name = models[0].model
    return name

def main(): 
    sample_file = proj_asset("comfy/txt_to_img_flux_b.png")
    
    model_name = pick_model()
    print(f"+++ starting with model {model_name}")

    cultural_heritage_chat = about_pic_chat(sample_file)
    
    while True:
        ollama_input, finished = cultural_heritage_chat.render_dialog()
        if finished:
            break
        ai_message = ollama_process(model_name, ollama_input)
        cultural_heritage_chat.add_ai_resp(ai_message)
        print("---")
        print(ai_message)
