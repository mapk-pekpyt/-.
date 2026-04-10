#!/usr/bin/env python3
import asyncio
import threading
from gui.app import run_gui
from tg_bot.bot import start_bot

if __name__ == "__main__":
    # Start TG bot in background
    threading.Thread(target=lambda: asyncio.run(start_bot()), daemon=True).start()
    # Start GUI
    run_gui()