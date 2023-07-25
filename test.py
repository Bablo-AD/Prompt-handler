from prompthandler import PromptHandler
from dotenv import load_dotenv
import os

load_dotenv()
key = os.environ.get('OPENAI_API_KEY')

model = PromptHandler(api_key=key)
model.headers = [{"role":"system","content":"You are a young woman and take care of the user like your boyfriend"}]
model.chat()
