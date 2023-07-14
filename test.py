from module import message_history
from dotenv import load_dotenv
import os

load_dotenv()

model = message_history(api_key=os.environ.get('OPENAI_API_KEY'),MAX_TOKEN=50,temperature=0.5)

def print_stuff():
    print("Whole Messages", model.messages, "Tokens", model.tokens)
    print("Head Messages", model.head_messages,"Tokens",model.head_tokens)
    print("Body Messsages", model.body_messages,"Tokens",model.body_tokens)

model.add_system("Now you are an ant and reply to me as if",to_head=True)
model.get_completion()
print_stuff()
model.add_user("Hi can you tell me about yourself?")
model.get_completion()
print_stuff()