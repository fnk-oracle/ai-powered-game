# AI-Powered Fantasy RPG Game

This project is an AI-powered text-based RPG game that uses large language models to generate interactive storytelling experiences. It features dynamic inventory tracking, avatar generation via Stable Diffusion, and a Gradio-based UI for seamless user interaction.

---

## 🎮 Features

- **AI-Generated Storytelling**: Narratives are powered by LLaMA-3 (via Together API).
- **Inventory Tracking**: Items gained or lost are detected and updated automatically.
- **Gradio Interface**: Clean web UI with live chat-style interaction.
- **Avatar Generation**: Uses Replicate's Stable Diffusion to generate character portraits from text prompts.
- **Session Memory** *(optional)*: Can be extended to remember past interactions.

---

## 📂 Directory Structure

```
AI Powered Game/
├── main.py                # Game entry point
├── helper.py              # Utility functions (API key, game state, etc.)
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── avatars/               # Stores generated avatar images
└── game_state.json        # Saved game data
```

---

## ⚖️ Setup & Installation

### 1. Clone the repo
```bash
git clone <your-repo-url>
cd AI\ Powered\ Game
```

### 2. Create virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set your API Keys
Export them in your shell or use a `.env` file:
```bash
export TOGETHER_API_KEY="your_together_api_key"
export REPLICATE_API_TOKEN="your_replicate_token"
```

---

## 🚀 Run the Game
```bash
python main.py
```
Then open the local Gradio link (http://127.0.0.1:7860) in your browser.

---

## 🌐 Avatar Generation
- At game start, a Stable Diffusion model (via Replicate) creates an avatar.
- Prompt style: fantasy-themed (e.g., "elven ranger with a green cloak, fantasy art")
- Images are saved to `avatars/` folder.

---

## 📃 Saving and Loading Game State
- Game state is saved as a JSON file.
- Includes character, world info, and inventory.
- Can be loaded to resume game sessions.

---

## ⚙️ Future Ideas
- NPC avatars and world map rendering
- Multiple characters and party-based adventures
- User-defined prompt styles or RPG classes
- HuggingFace Space deployment (`gradio deploy`)

---

## 📁 Requirements
- Python 3.10+
- Gradio
- Together API (LLaMA-3)
- Replicate API (Stable Diffusion)

---

## 📖 Credits
- [Together.ai](https://www.together.ai/) for LLMs
- [Replicate](https://replicate.com) for image generation
- [Gradio](https://gradio.app/) for UI framework

