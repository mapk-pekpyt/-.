import tkinter as tk
from tkinter import scrolledtext, filedialog
import threading
import asyncio
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from core.llm_client import LLMClient
from core.memory import MemorySystem
from tools.stt import listen
from tools.tts import speak
from gui.settings_window import SettingsWindow

class JarvisGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Jarvis Local AI")
        self.root.geometry("1200x800")
        self.root.configure(bg='black')
        
        self.client = LLMClient("pc_user", platform="pc")
        self.memory = MemorySystem()
        self.current_chat = "default"
        
        self.setup_ui()
    
    def setup_ui(self):
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(self.root, bg='#1e1e1e', fg='white', 
                                                       font=('Consolas', 11), wrap=tk.WORD)
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Input frame
        input_frame = tk.Frame(self.root, bg='black')
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.input_field = tk.Entry(input_frame, bg='#2d2d2d', fg='white', 
                                     font=('Consolas', 11))
        self.input_field.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))
        self.input_field.bind('<Return>', self.send_message)
        
        voice_btn = tk.Button(input_frame, text="🎤", command=self.voice_input, 
                              bg='#2d2d2d', fg='white')
        voice_btn.pack(side=tk.LEFT, padx=2)
        
        voice_dialog_btn = tk.Button(input_frame, text="🗣️", command=self.voice_dialog, 
                                     bg='#2d2d2d', fg='white')
        voice_dialog_btn.pack(side=tk.LEFT, padx=2)
        
        upload_btn = tk.Button(input_frame, text="📎", command=self.upload_file, 
                               bg='#2d2d2d', fg='white')
        upload_btn.pack(side=tk.LEFT, padx=2)
        
        menu_btn = tk.Button(input_frame, text="☰", command=self.toggle_menu, 
                             bg='#2d2d2d', fg='white')
        menu_btn.pack(side=tk.LEFT, padx=2)
        
        settings_btn = tk.Button(input_frame, text="⚙️", command=self.open_settings, 
                                 bg='#2d2d2d', fg='white')
        settings_btn.pack(side=tk.LEFT, padx=2)
        
        # Menu frame (hidden)
        self.menu_frame = tk.Frame(self.root, bg='#2d2d2d', width=200)
    
    def send_message(self, event=None):
        message = self.input_field.get()
        if not message:
            return
        
        self.display_message(f"Вы: {message}", align="left")
        self.input_field.delete(0, tk.END)
        
        # Search memory
        history = self.memory.search_history("pc_user", message, shared=True)
        context = "\n".join(history) if history else ""
        
        full_message = f"Context:\n{context}\n\nUser: {message}" if context else message
        
        # Get response
        response = self.client.chat(full_message)
        self.display_message(f"Джарвис: {response}", align="right")
        
        # Save memory
        self.memory.add_message("pc_user", message, response, shared=True)
        
        # Check for game launch
        if "задротить будем" in response:
            self.root.after(100, self.wait_for_game)
    
    def wait_for_game(self):
        self.display_message("Джарвис: Жду название игры...", align="right")
        # Next message will be game name
        self.input_field.bind('<Return>', self.launch_game, add='+')
    
    def launch_game(self, event):
        game_name = self.input_field.get()
        import subprocess
        subprocess.Popen(f"start {game_name}", shell=True)
        self.display_message(f"🎮 Запускаю {game_name}", align="system")
        self.input_field.unbind('<Return>')
        self.input_field.bind('<Return>', self.send_message)
    
    def voice_input(self):
        text = listen()
        if text:
            self.input_field.delete(0, tk.END)
            self.input_field.insert(0, text)
            self.send_message()
    
    def voice_dialog(self):
        text = listen()
        if text:
            response = self.client.chat(text)
            speak(response)
            self.display_message(f"Вы: {text}", align="left")
            self.display_message(f"Джарвис: {response}", align="right")
    
    def upload_file(self):
        filepath = filedialog.askopenfilename()
        if filepath:
            from core.file_reader import read_file
            content = read_file(filepath)
            self.input_field.insert(0, f"Содержимое файла: {content[:200]}...")
    
    def toggle_menu(self):
        if self.menu_frame.winfo_ismapped():
            self.menu_frame.pack_forget()
        else:
            self.menu_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0,10))
    
    def open_settings(self):
        SettingsWindow(self.root)
    
    def display_message(self, message, align="left"):
        self.chat_display.insert(tk.END, message + "\n")
        self.chat_display.insert(tk.END, "─"*50 + "\n")
        self.chat_display.see(tk.END)
    
    def run(self):
        self.root.mainloop()

def run_gui():
    gui = JarvisGUI()
    gui.run()