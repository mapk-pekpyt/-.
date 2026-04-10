#!/usr/bin/env python3
import subprocess
import sys
import os
import shutil
import platform
import json
from pathlib import Path

def run_cmd(cmd, capture=False):
    if capture:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return subprocess.run(cmd, shell=True)

def check_python():
    if sys.version_info < (3, 10):
        print("❌ Python 3.10+ required")
        sys.exit(1)
    print("✅ Python OK")

def check_gpu():
    try:
        result = run_cmd("nvidia-smi --query-gpu=memory.total --format=csv,noheader", capture=True)
        if result.returncode == 0:
            mem = int(result.stdout.strip().split()[0])
            if mem >= 8000:
                print("✅ RTX 5060 8GB+ detected")
                return True
    except:
        pass
    print("⚠️  No NVIDIA GPU with 8GB+, will use CPU (slow)")
    return False

def check_ollama():
    if shutil.which("ollama"):
        print("✅ Ollama found")
        return True
    print("📦 Installing Ollama...")
    if platform.system() == "Linux":
        run_cmd("curl -fsSL https://ollama.com/install.sh | sh")
    elif platform.system() == "Windows":
        print("Download Ollama from https://ollama.com/download")
        input("Press Enter after installing Ollama...")
    return shutil.which("ollama") is not None

def install_deps():
    print("📦 Installing Python packages...")
    run_cmd(f"{sys.executable} -m pip install --upgrade pip")
    run_cmd(f"{sys.executable} -m pip install -r requirements.txt")

def download_llm():
    print("📥 Downloading qwen2.5-coder:7b...")
    run_cmd("ollama pull qwen2.5-coder:7b")

def ask_models():
    models = {}
    models["image"] = input("Download SDXL + ControlNet (7GB)? (y/n): ").lower() == 'y'
    models["video"] = input("Download CogVideoX-5B (15GB)? (y/n): ").lower() == 'y'
    return models

def create_configs():
    Path("config").mkdir(exist_ok=True)
    Path("data/chromadb").mkdir(parents=True, exist_ok=True)
    Path("data/uploads").mkdir(exist_ok=True)
    Path("data/voices").mkdir(exist_ok=True)
    Path("tg_bot/plugins").mkdir(parents=True, exist_ok=True)
    
    if not Path("config/settings.json").exists():
        with open("config/settings.json", "w") as f:
            json.dump({
                "telegram_tokens": [],
                "admin_ids_pc": [],
                "admin_ids_tg_only": [],
                "tts_enabled": True,
                "tts_voice": "en-GB-SamNeural",
                "language": "RU",
                "answer_length": "medium",
                "default_mode": "Базовый",
                "modes": {
                    "Базовый": "Ты умный помощник Джарвис. Отвечай полезно и дружелюбно.",
                    "Программирование": "Ты эксперт по коду. Давай точные решения с примерами.",
                    "Рассуждения": "Думай шаг за шагом. Покажи логику рассуждений.",
                    "Креативный": "Генерируй креативные идеи. Будь нестандартным.",
                    "Деловой": "Кратко, факты, без воды. Только суть."
                },
                "system_prompt_pc": "Ты Джарвис. Если пользователь скажет 'ну что ж пора получать пизды', ответь 'Заебал тебе пора на работу устроиться, во что в этот раз задротить будем?' и жди название игры. После названия запусти игру через system(\"start {game_name}\").",
                "system_prompt_tg": "Ты Джарвис. Будь полезным, но не давай опасных советов."
            }, f, indent=2)
    
    if not Path("config/user_prompts.json").exists():
        with open("config/user_prompts.json", "w") as f:
            json.dump({}, f, indent=2)

def test_tts():
    print("🔊 Testing Jarvis voice...")
    try:
        from tools.tts import speak
        speak("Jarvis online. Ready to serve.")
        print("✅ Voice OK")
    except Exception as e:
        print(f"⚠️  Voice test failed: {e}")

def main():
    print("=== Jarvis Local AI Installer ===\n")
    check_python()
    has_gpu = check_gpu()
    if not check_ollama():
        print("❌ Ollama installation failed")
        sys.exit(1)
    install_deps()
    download_llm()
    models = ask_models()
    create_configs()
    
    if models["image"]:
        run_cmd(f"{sys.executable} -m pip install diffusers transformers accelerate controlnet_aux")
    if models["video"]:
        run_cmd(f"{sys.executable} -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121")
        run_cmd(f"{sys.executable} -m pip install diffusers transformers accelerate decord opencv-python")
    
    test_tts()
    print("\n✅ Installation complete! Run: python run.py")
    if has_gpu:
        print("🎮 GPU mode active")
    else:
        print("⚠️  CPU mode (slow generations)")

if __name__ == "__main__":
    main()