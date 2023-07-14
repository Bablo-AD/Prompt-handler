from .brain import chatgpt_api
import tiktoken

class message_history(chatgpt_api):
    """
    This class represents the message history for a conversation.
    """

    def __init__(self,MAX_TOKEN=4096,api_key=None,temperature=0,model="gpt-3.5-turbo-0613"):
        # Initializes the message history.
        self.head_messages = []
        self.body_messages = []
        self.update_messages()
        self.MAX_TOKEN = MAX_TOKEN

        self.head_tokens = 0
        self.body_tokens = 0
        self.tokens = 0
        if api_key != None:
            super().__init__(api_key=api_key,temperature=temperature,model=model)

    def update_messages(self):
        self.messages = self.head_messages + self.body_messages

    def calibrate(self): # We have to improve this to include the summarization stuff
        """
        self.calibrates the message history. Right now it does by comparing the token of the whole message with the MAX_TOKEN and remove the top message of from the body
        """
        self.tokens = self.get_token_for_message(self.messages,model_name=self.model)
        self.head_tokens = self.get_token_for_message(self.head_messages,model_name=self.model)
        self.body_tokens = self.get_token_for_message(self.body_messages,model_name=self.model)
        if self.tokens >= self.MAX_TOKEN:
            for i in self.body_messages:
                self.body_messages.remove(i)
                if self.get_token_for_message(messages=self.messages) >=self.MAX_TOKEN:
                    pass
                else:
                    break
        
    def add(self, role, content, to_head=False):
        """
        Adds a message to the message history.

        Args:
            role (str): The role of the message (user, assistant, etc.).
            content (str): The content of the message.
            to_head (bool): Specifies whether the message should be appended to the head_messages list.
                            If False, it will be appended to the body_messages list.
        
        Returns:
            dict: The last message in the message history.
        """
        if to_head:
            self.head_messages.append({"role": role, "content": content})
        else:
            self.body_messages.append({"role": role, "content": content})

        self.update_messages()
        self.calibrate()
        return self.messages[-1]
    
    def add_user(self, content, to_head=False):
        """
        Adds a user message to the message history.

        Args:
            content (str): The content of the user message.
            to_head (bool): Specifies whether the message should be appended to the head_messages list.
                            If False, it will be appended to the body_messages list.
        
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
            to_head (bool): Specifies whether the message should be appended to the head_messages list.
                            If False, it will be appended to the body_messages list.
        
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
            to_head (bool): Specifies whether the message should be appended to the head_messages list.
                            If False, it will be appended to the body_messages list.
        
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
        self.calibrate()
    
    def get_last_message(self):
        """
        Returns the last message in the message history.

        Returns:
            dict: The last message in the message history.
        """
        return self.messages[-1]

    def get_token_for_message(self,messages, model_name="gpt-3.5-turbo-0613"):
        """Returns the number of tokens used by a list of messages."""
        
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

