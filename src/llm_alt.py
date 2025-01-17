
# from typing import Optional, Sequence
# import ollama

# from enum import Enum
# from pydantic import BaseModel

# from ollama import chat

# from utils import proj_asset

# class Role(str, Enum):
#     SYSTEM = "system"
#     USER = "user"
#     AI = "assistant"

# class Message(BaseModel):
#     role: Role
#     content: str
#     images: Optional[Sequence[str]] = None

#     class Config:
#         use_enum_values = True

# def main(): 
#     sample_file = proj_asset("comfy/txt_to_img_flux_b.png")
    
#     models = ollama.list().models
#     if len(models) == 0:
#         print("!!! no models, exit. Install something with \"ollama pull MODEL_NAME\"")

#     name = models[0].model
#     print(f"+++ starting with model {name}")

#     sys_msg = Message(
#         role=Role.SYSTEM,
#         content="You are now roleplaing an older man his speach became wise after all this years"
#             "you have some problems with alcohol, not counting some other addictions, "
#             "tough lack, as they said. "
#             "But allways start your response with \"Oh my dear\"",
#     )

    

#     usr_msg = Message(
#         role=Role.USER,
#         content="What do you see on that picture",
#         images=[sample_file]
#     )

#     ust_msg_2 = Message(
#         role=Role.USER,
#         content="What do you think, who is wearing them?"
#     )

#     dialog = [sys_msg.model_dump(), usr_msg.model_dump()]

#     def chat_run(dialog):
#         stream = chat(
#             model=name,
#             messages=dialog,
#             stream=True
#         )

#         tokens = []
#         for chunk in stream:
#             token = chunk["message"]["content"]
#             print(token, end='', flush=True)
#             tokens.append(token)

#         return "".join(tokens)
#     full_text = chat_run(dialog)
#     print("\n---")
#     print(full_text)
#     print("---")
#     ai_msg = Message(
#         role=Role.AI,
#         content=full_text
#     )
#     dialog.append(ai_msg.model_dump())
#     dialog.append(ust_msg_2.model_dump())
#     full_text = chat_run(dialog)
#     print("\n--")
#     print(full_text)
#     print("---")


#     print("")
        