import tkinter as tk
from tkinter import ttk, messagebox
import json
from pathlib import Path

class SettingsWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Настройки")
        self.window.geometry("800x600")
        self.window.configure(bg='black')
        
        self.load_config()
        self.setup_ui()
    
    def load_config(self):
        with open("config/settings.json") as f:
            self.config = json.load(f)
    
    def save_config(self):
        with open("config/settings.json", "w") as f:
            json.dump(self.config, f, indent=2)
        messagebox.showinfo("Успех", "Настройки сохранены. Бот перезапустится.")
        # Restart bot logic here
    
    def setup_ui(self):
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # General tab
        general = tk.Frame(notebook, bg='black')
        notebook.add(general, text="Основные")
        
        tk.Label(general, text="Язык:", bg='black', fg='white').grid(row=0, column=0, sticky='w')
        lang_var = tk.StringVar(value=self.config["language"])
        tk.OptionMenu(general, lang_var, "RU", "EN").grid(row=0, column=1)
        
        tk.Label(general, text="Длина ответов:", bg='black', fg='white').grid(row=1, column=0, sticky='w')
        length_var = tk.StringVar(value=self.config["answer_length"])
        tk.OptionMenu(general, length_var, "shortest", "short", "medium", "long").grid(row=1, column=1)
        
        # Modes tab
        modes_frame = tk.Frame(notebook, bg='black')
        notebook.add(modes_frame, text="Режимы")
        
        self.mode_texts = {}
        row = 0
        for mode, prompt in self.config["modes"].items():
            tk.Label(modes_frame, text=mode, bg='black', fg='white').grid(row=row, column=0, sticky='nw')
            text_widget = tk.Text(modes_frame, height=5, width=60, bg='#2d2d2d', fg='white')
            text_widget.insert(tk.END, prompt)
            text_widget.grid(row=row, column=1, pady=5)
            self.mode_texts[mode] = text_widget
            row += 1
        
        tk.Button(modes_frame, text="Добавить режим", command=self.add_mode).grid(row=row, column=0, pady=10)
        
        # Prompts tab
        prompts_frame = tk.Frame(notebook, bg='black')
        notebook.add(prompts_frame, text="Промты")
        
        tk.Label(prompts_frame, text="Системный промт (ПК):", bg='black', fg='white').pack()
        self.pc_prompt = tk.Text(prompts_frame, height=8, bg='#2d2d2d', fg='white')
        self.pc_prompt.insert(tk.END, self.config["system_prompt_pc"])
        self.pc_prompt.pack(fill=tk.X, pady=5)
        
        tk.Label(prompts_frame, text="Системный промт (Telegram):", bg='black', fg='white').pack()
        self.tg_prompt = tk.Text(prompts_frame, height=8, bg='#2d2d2d', fg='white')
        self.tg_prompt.insert(tk.END, self.config["system_prompt_tg"])
        self.tg_prompt.pack(fill=tk.X, pady=5)
        
        # API tab
        api_frame = tk.Frame(notebook, bg='black')
        notebook.add(api_frame, text="API")
        
        tk.Label(api_frame, text="Telegram токены (через ;):", bg='black', fg='white').pack()
        self.tokens_entry = tk.Entry(api_frame, width=80, bg='#2d2d2d', fg='white')
        self.tokens_entry.insert(0, ";".join(self.config["telegram_tokens"]))
        self.tokens_entry.pack(pady=5)
        
        # Save button
        tk.Button(self.window, text="Сохранить и перезапустить", command=self.save_and_restart,
                  bg='green', fg='white').pack(pady=10)
    
    def add_mode(self):
        dialog = tk.Toplevel(self.window)
        tk.Label(dialog, text="Название режима:").pack()
        name_entry = tk.Entry(dialog)
        name_entry.pack()
        tk.Label(dialog, text="Промт:").pack()
        prompt_text = tk.Text(dialog, height=5)
        prompt_text.pack()
        
        def save():
            name = name_entry.get()
            prompt = prompt_text.get("1.0", tk.END).strip()
            self.config["modes"][name] = prompt
            dialog.destroy()
            self.window.destroy()
            SettingsWindow(self.window.master)
        
        tk.Button(dialog, text="Сохранить", command=save).pack()
    
    def save_and_restart(self):
        # Save all changes
        self.config["language"] = self.lang_var.get()
        self.config["answer_length"] = self.length_var.get()
        
        for mode, text_widget in self.mode_texts.items():
            self.config["modes"][mode] = text_widget.get("1.0", tk.END).strip()
        
        self.config["system_prompt_pc"] = self.pc_prompt.get("1.0", tk.END).strip()
        self.config["system_prompt_tg"] = self.tg_prompt.get("1.0", tk.END).strip()
        
        tokens = self.tokens_entry.get().split(";")
        self.config["telegram_tokens"] = [t.strip() for t in tokens if t.strip()]
        
        self.save_config()
        
        # Restart bot
        import subprocess
        subprocess.Popen(["python", "run.py"])
        self.window.quit()