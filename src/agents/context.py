
class ContextAttributeError(BaseException):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class Context:
    def __init__(self) -> None:
        self.msg = []
        pass

    def add_system_prompt(self, prompt: str):
        pt = {
            'role': 'system',
            'content': prompt
        }

        # replace the last system prompt if it exists or insert to 0 if it doesn't
        if len(self.msg) > 0 and self.msg[0]['role'] == 'system':
            self.msg[0] = pt
        else:
            self.msg.insert(0, pt)

    def add_user_prompt(self, prompt: str):
        pt = {
            'role': 'user',
            'content': prompt
        }
        self.msg.append(pt)

    def remove_last_prompt(self):
        self.msg.pop(-1)

    def add_assistant_prompt(self, prompt: str):
        pt = {
            'role': 'assistant',
            'content': prompt
        }

        self.msg.append(pt)
