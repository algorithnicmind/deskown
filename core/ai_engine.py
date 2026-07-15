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

    def chat(self, message: str, task_runner=None, context: dict = None) -> str:
        self.messages.append({"role": "user", "content": message})
        self._trim_history()

        tools = []
        if task_runner:
            tools = task_runner.get_ollama_tools()

        while True:
            try:
                response = self.client.chat(
                    model=self.model,
                    messages=self.messages,
                    tools=tools if tools else None
                )
                
                msg = response.get("message", {})
                self.messages.append(msg)

                tool_calls = msg.get("tool_calls")
                if not tool_calls:
                    return msg.get("content", "")

                for tool_call in tool_calls:
                    function_name = tool_call["function"]["name"]
                    arguments = tool_call["function"]["arguments"]
                    
                    if task_runner:
                        result = task_runner.execute_tool(function_name, arguments, context)
                    else:
                        result = "No task runner available."
                    
                    self.messages.append({
                        "role": "tool",
                        "content": str(result),
                        "name": function_name
                    })

                self._trim_history()

            except Exception as e:
                error_msg = f"Error: {e}"
                self.messages.append({"role": "assistant", "content": error_msg})
                return error_msg

    def chat_stream(self, message: str, task_runner=None, context: dict = None):
        """Streaming doesn't work well with tool calls natively in a simple loop, 
        so we fallback to synchronous chat if tools are used, or just do a standard stream."""
        # For simplicity, if task_runner is provided, we just use synchronous chat and yield it
        if task_runner:
            result = self.chat(message, task_runner, context)
            yield result
            return

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
                content = chunk.get("message", {}).get("content", "")
                if content:
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
