# PromptHandler
Focus on helping people not on managing prompts.

#### Manages Tokens (within limit), removes older message automatically, Summarizes 

## Installation
```
pip install prompthandler
```
## Usage
An example code to make the model chat with you in terminal
```python
from prompthandler import Prompthandler
model = Prompthandler()
model.add_system("You are now user's girlfriend so take care of him",to_head=True) # Makes this to go on to the head. Head is not rolled so it stays the same
model.add_user("Hi")
model.chat() # you can chat with it in terminal
```
