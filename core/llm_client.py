import ollama
import json
from pathlib import Path

with open("config/settings.json") as f:
    config = json.load(f)

class LLMClient:
    def __init__(self, user_id, mode=None, length=None, platform="pc"):
        self.user_id = str(user_id)
        self.mode = mode or config.get("default_mode", "Базовый")
        self.length = length or config.get("answer_length", "medium")
        self.platform = platform
        self.history = []
        
        length_prompts = {
            "shortest": "Ответь максимально коротко, 1-2 слова.",
            "short": "Ответь коротко, 1-2 предложения.",
            "medium": "Ответь развернуто, но без воды.",
            "long": "Дай максимально подробный ответ."
        }
        self.length_prompt = length_prompts.get(self.length, length_prompts["medium"])
    
    def _get_system_prompt(self):
        mode_prompt = config["modes"].get(self.mode, config["modes"]["Базовый"])
        if self.platform == "pc":
            base = config["system_prompt_pc"]
        else:
            base = config["system_prompt_tg"]
        return f"{base}\n\n{mode_prompt}\n\n{self.length_prompt}"
    
    def chat(self, message):
        messages = [{"role": "system", "content": self._get_system_prompt()}]
        messages.extend(self.history[-20:])  # last 20 messages
        messages.append({"role": "user", "content": message})
        
        response = ollama.chat(model="qwen2.5-coder:7b", messages=messages)
        reply = response["message"]["content"]
        
        self.history.append({"role": "user", "content": message})
        self.history.append({"role": "assistant", "content": reply})
        
        # Check for game launch command
        if "пора получать пизды" in message.lower():
            import subprocess
            import re
            # Wait for next message with game name
            return "Заебал тебе пора на работу устроиться, во что в этот раз задротить будем?"
        if "задротить будем" in reply and "game_name" not in locals():
            # Store game name from next user input
            pass
            
        return reply
    
    def set_mode(self, mode):
        self.mode = mode
    
    def set_length(self, length):
        self.length = length
        length_prompts = {
            "shortest": "Ответь максимально коротко, 1-2 слова.",
            "short": "Ответь коротко, 1-2 предложения.",
            "medium": "Ответь развернуто, но без воды.",
            "long": "Дай максимально подробный ответ."
        }
        self.length_prompt = length_prompts.get(length, length_prompts["medium"])