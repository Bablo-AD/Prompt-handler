from .models import openai_chat_gpt
import tiktoken

class PromptHandler(openai_chat_gpt):
    """
    This class represents a conversation prompt history for interacting with the GPT-3.5-turbo model (or other OpenAI models).
    """

    def __init__(self, MAX_TOKEN=4096, api_key=None, temperature=0, model="gpt-3.5-turbo-0613",calibration_type="summary"):
        """
        Initializes the PromptHandler with the specified settings.

        Args:
            MAX_TOKEN (int): The maximum number of tokens allowed for the generated completion.
            api_key (str): The OpenAI API key.
            temperature (float): The temperature parameter controlling the randomness of the output.
            model (str): The name of the OpenAI model to use.
            calibration_type: currently there are two suppored types summary(generates summary of conversation) - default, truncate deletes previous conversations
        """
        # Initializes the message history.
        self.headers = []
        self.body = []
        self.head_tokens = 0
        self.body_tokens = 0
        self.tokens = 0
        self.calibration_type = calibration_type
        if 'gpt' in model:
            super().__init__(MAX_TOKEN=MAX_TOKEN, api_key=api_key, temperature=temperature, model=model)
        self.update()
    def dump(self):
        """
        Get a dict of head,body and messages
        """
        self.update_messages()
        return {'head':self.headers,'body':self.body,'messages':self.messages}
        
    def load(self,dictionary):
        """
        Load the data from the dictionary
        """
        self.headers = dictionary['head']
        self.body = dictionary['body']
        self.messages = dictionary['messages']
        self.update()

    def get_completion(self, message='', update_history=True, temperature=None):
        """
        Generates a completion for the conversation history.

        Args:
            message (str): The user's message to be added to the history.
            update_history (bool): Flag to update the conversation history.
            temperature (float): Control the randomness of the output.

        Returns:
            str: The completion generated by the model.
            int: The number of tokens used by the completion.
        """
        self.update()
        if message == '':
            self.calibrate()
            completion_output = self.get_completion_for_message(self.messages, temperature)
            if update_history:
                self.add_assistant(completion_output[0])
                return self.get_last_message()['content']
            else:
                return completion_output
        else:
            if update_history:
                self.add_user(message)
                self.calibrate()
                completion_output = self.get_completion_for_message(self.messages, temperature)
                self.add_assistant(completion_output[0])
                return self.get_last_message()['content']
            else:
                temporary_message = self.messages.copy()
                temporary_message.append({"role": "user", "content": message})
                completion_output = self.get_completion_for_message(temporary_message, temperature)
                return completion_output

    def chat(self, update_history=True, temperature=None):
        """
        Starts a conversation with the model. Accepts terminal input and prints the model's responses.

        Args:
            update_history (bool): Flag to update the conversation history.
            temperature (float): Control the randomness of the output.
        """
        print(self.get_completion(update_history=update_history, temperature=temperature))
        while True:
            user_input = input()
            if user_input == '\\break':
                break
            print(self.get_completion(message=user_input, update_history=update_history, temperature=temperature))
    
    def update(self):
        """
        Combines the headers and body messages into a single message history and also the tokens.
        """
        self.update_messages()
        self.update_tokens()
    def update_messages(self):
        """
        Combines the headers and body messages into a single message history.

        Returns:
            list: The combined list of messages representing the conversation history.
        """
        self.messages = self.headers + self.body
        return self.messages
    
    def update_tokens(self):
        """
        Updates the count of tokens used in the headers, body, and entire message history.

        Returns:
            tuple: A tuple containing the total tokens used, tokens used in headers, and tokens used in body.
        """
        self.head_tokens = self.get_token_for_message(self.headers, model_name=self.model)
        self.body_tokens = self.get_token_for_message(self.body, model_name=self.model)
        self.tokens = self.get_token_for_message(self.messages, model_name=self.model)
        return self.tokens, self.head_tokens, self.body_tokens

    def calibrate(self, MAX_TOKEN=None,calibration_type=None):
        """
        Calibrates the message history by removing older messages if the total token count exceeds MAX_TOKEN.

        Args:
            MAX_TOKEN (int): The maximum number of tokens allowed for the generated completion.
            calibration_type: currently there are two suppored types summary(generates summary of conversation) - default, truncate deletes previous conversations
        """
        if MAX_TOKEN is None:
            MAX_TOKEN = self.MAX_TOKEN
        if calibration_type is None:
            calibration_type = self.calibration_type
        self.update_tokens()
        if self.head_tokens >= MAX_TOKEN:
            raise Exception("HEAD TOKENS are greater than MAX TOKEN: Try reducing the Head prompts or increase MAX TOKEN")
        if self.tokens >= MAX_TOKEN:
            if calibration_type == 'truncate':
                del self.body[0]
            elif calibration_type == 'summary':
                self.add_system("Summarize this conversation")
                out = self.get_completion_for_message(self.body)
                self.body = []
                self.add_system(out[0])
            self.update_messages()
            self.calibrate()
        
    def add(self, role, content, to_head=False):
        """
        Adds a message to the message history.

        Args:
            role (str): The role of the message (user, assistant, etc.).
            content (str): The content of the message.
            to_head (bool): Specifies whether the message should be appended to the headers list.
                            If False, it will be appended to the body list.
        
        Returns:
            dict: The last message in the message history.
        """
        if to_head:
            self.headers.append({"role": role, "content": content})
        else:
            self.body.append({"role": role, "content": content})

        self.update_messages()
        return self.messages[-1]
    
    def add_user(self, content, to_head=False):
        """
        Adds a user message to the message history.
        Args:
            content (str): The content of the user message.
            to_head (bool): Specifies whether the message should be appended to the headers list.
                            If False, it will be appended to the body list.
        
        Returns:
            dict: The last message in the message history.
        """
        self.add("user", content, to_head)
        return self.messages[-1]
    
    def add_assistant(self, content, to_head=False):
        """
        Adds an assistant message to the message history.
        Args:
            content (str): The content of the assistant message.
            to_head (bool): Specifies whether the message should be appended to the headers list.
                            If False, it will be appended to the body list.
        
        Returns:
            dict: The last message in the message history.
        """
        self.add("assistant", content, to_head)
        return self.messages[-1]
    
    def add_system(self, content, to_head=False):
        """
        Adds a system message to the message history.
        Args:
            content (str): The content of the system message.
            to_head (bool): Specifies whether the message should be appended to the headers list.
                            If False, it will be appended to the body list.
        
        Returns:
            dict: The last message in the message history.
        """
        self.add("system", content, to_head)
        return self.messages[-1]

    def append(self, content_list):
        """
        Appends a list of messages to the message history.

        Args:
            content_list (list): List of messages to be appended.
        """
        self.messages.extend(content_list)
    
    def get_last_message(self):
        """
        Returns the last message in the message history.

        Returns:
            dict: The last message in the message history.
        """
        return self.messages[-1]

    def get_token_for_message(self, messages, model_name="gpt-3.5-turbo-0613"):
        """
        Returns the number of tokens used by a list of messages.

        Args:
            messages (list): List of messages to count tokens for.
            model_name (str): The name of the OpenAI model used for token encoding.

        Returns:
            int: The number of tokens used by the provided list of messages.
        """
        try:
            encoding = tiktoken.encoding_for_model(model_name)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        if model_name == "gpt-3.5-turbo-0613":  # note: future models may deviate from this
            num_tokens = 0
            for message in messages:
                num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
                for key, value in message.items():
                    num_tokens += len(encoding.encode(value))
                    if key == "name":  # if there's a name, the role is omitted
                        num_tokens += -1  # role is always required and always 1 token
            num_tokens += 2  # every reply is primed with <im_start>assistant
            return num_tokens
        else:
            raise NotImplementedError(f"""num_tokens_from_messages() is not presently implemented for model {model}.
        See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")
