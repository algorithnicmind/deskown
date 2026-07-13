import ollama as ollama_client

import config


class AIEngine:
    def __init__(self, model: str = None, host: str = None):
        self.model = model or config.OLLAMA_MODEL
        self.host = host or config.OLLAMA_HOST
        self.messages = [
            {"role": "system", "content": config.SYSTEM_PROMPT}
        ]
        self.client = ollama_client.Client(host=self.host)

    def chat(self, message: str) -> str:
        self.messages.append({"role": "user", "content": message})
        self._trim_history()

        try:
            response = self.client.chat(model=self.model, messages=self.messages)
            content = response["message"]["content"]
            self.messages.append({"role": "assistant", "content": content})
            return content
        except Exception as e:
            error_msg = f"Error: {e}"
            self.messages.append({"role": "assistant", "content": error_msg})
            return error_msg

    def chat_stream(self, message: str):
        self.messages.append({"role": "user", "content": message})
        self._trim_history()

        full_response = ""
        try:
            stream = self.client.chat(
                model=self.model,
                messages=self.messages,
                stream=True,
            )
            for chunk in stream:
                content = chunk["message"]["content"]
                full_response += content
                yield content

            self.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            error_msg = f"Error: {e}"
            self.messages.append({"role": "assistant", "content": error_msg})
            yield error_msg

    def clear_history(self):
        self.messages = [
            {"role": "system", "content": config.SYSTEM_PROMPT}
        ]

    def set_model(self, model: str):
        self.model = model

    def get_history(self) -> list[dict]:
        return [m for m in self.messages if m["role"] != "system"]

    def _trim_history(self):
        system_msgs = [m for m in self.messages if m["role"] == "system"]
        non_system = [m for m in self.messages if m["role"] != "system"]

        if len(non_system) > config.MAX_HISTORY:
            non_system = non_system[-config.MAX_HISTORY:]

        self.messages = system_msgs + non_system
