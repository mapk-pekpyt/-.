from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import json
import asyncio
from pathlib import Path
import importlib.util
import sys

sys.path.append(str(Path(__file__).parent.parent))
from core.llm_client import LLMClient
from core.memory import MemorySystem
from tools.tts import _speak_async
from tools.stt import listen
from tools.search import search_duckduckgo
from tools.image_gen import generate_image
from tools.video_gen import generate_video

with open("config/settings.json") as f:
    config = json.load(f)

memory = MemorySystem()
user_clients = {}
generation_queue = asyncio.Queue()
generation_tasks = {}

class GenerationManager:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.processing = False
    
    async def add_generation(self, user_id, gen_type, prompt, callback):
        position = self.queue.qsize() + 1
        await self.queue.put((user_id, gen_type, prompt, callback))
        await callback(f"⏳ Подождите, вы в очереди на генерацию. Ожидайте ~{position*2} минут")
        if not self.processing:
            await self.process_queue()
    
    async def process_queue(self):
        self.processing = True
        while not self.queue.empty():
            user_id, gen_type, prompt, callback = await self.queue.get()
            if gen_type == "image":
                result = await generate_image(prompt)
            else:
                result = await generate_video(prompt)
            await callback(f"✅ Готово: {result}")
        self.processing = False

gen_manager = GenerationManager()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎭 Режим", callback_data="mode"),
         InlineKeyboardButton("📏 Длина ответа", callback_data="length")],
        [InlineKeyboardButton("🎙️ Голосовой диалог", callback_data="voice_toggle"),
         InlineKeyboardButton("🖼️ Сгенерировать фото", callback_data="gen_image")],
        [InlineKeyboardButton("🎬 Сгенерировать видео", callback_data="gen_video"),
         InlineKeyboardButton("🔍 Поиск в интернете", callback_data="search")],
        [InlineKeyboardButton("💾 Личный промт", callback_data="personal_prompt"),
         InlineKeyboardButton("❓ Помощь", callback_data="help")]
    ]
    await update.message.reply_text("Jarvis online. Чем могу помочь?", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    # Get or create client
    if user_id not in user_clients:
        user_clients[user_id] = LLMClient(user_id, platform="tg")
    
    # Search history
    history = memory.search_history(user_id, text)
    context_text = "\n".join(history) if history else ""
    
    full_prompt = f"Context from past conversations:\n{context_text}\n\nUser: {text}" if context_text else text
    
    response = user_clients[user_id].chat(full_prompt)
    
    # Save to memory
    memory.add_message(user_id, text, response)
    
    await update.message.reply_text(response)
    
    # Voice response if enabled
    if config.get("tts_enabled", True):
        voice_file = await _speak_async(response)
        await update.message.reply_voice(voice=open(voice_file, 'rb'))

async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Download voice, convert to text, then handle as message
    voice = await update.message.voice.get_file()
    # Use speech recognition
    # ... implementation
    pass

def load_plugins():
    plugin_dir = Path("tg_bot/plugins")
    for py_file in plugin_dir.glob("*.py"):
        spec = importlib.util.spec_from_file_location(py_file.stem, py_file)
        module = importlib.util.module_from_spec(spec)
        sys.modules[py_file.stem] = module
        spec.loader.exec_module(module)
        if hasattr(module, "register_handlers"):
            module.register_handlers(application)

async def start_bot():
    app = Application.builder().token(config["telegram_tokens"][0]).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.VOICE, voice_handler))
    
    load_plugins()
    
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    # Keep running
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(start_bot())