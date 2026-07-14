import re
import os
from PyQt6.QtWidgets import QApplication

class Plugin:
    name = "system_commands"
    description = "Execute system commands like shutdown or closing the assistant"
    patterns = [
        r"(?:shutdown|turn off) (?:my )?(?:computer|laptop|pc)",
        r"(?:restart|reboot) (?:my )?(?:computer|laptop|pc)",
        r"(?:close|quit|exit) deskown"
    ]

    def match(self, command: str) -> bool:
        for pattern in self.patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return True
        return False

    def execute(self, command: str, context: dict) -> str:
        cmd_lower = command.lower()
        
        if "close" in cmd_lower or "quit" in cmd_lower or "exit" in cmd_lower:
            QApplication.quit()
            return "Closing DeskOwn. Goodbye!"
            
        elif "restart" in cmd_lower or "reboot" in cmd_lower:
            os.system("shutdown /r /t 5")
            return "Restarting your computer in 5 seconds."
            
        elif "shutdown" in cmd_lower or "turn off" in cmd_lower:
            os.system("shutdown /s /t 5")
            return "Shutting down your computer in 5 seconds."
            
        return "System command not recognized."
