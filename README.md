# DilogX Bot powerd AI

This project is an advanced Discord bot powered by a custom intent recognition engine using PyTorch.  
It can understand user input using a predefined vocabulary and respond accordingly using a trained neural model.

---

## 🔧 Features

- 💬 Natural-language understanding (NLU) using intent classification  
- 🧠 Custom neural network model built with PyTorch  
- 📖 Vocabulary-based training system (easy to expand)  
- 🤖 Discord bot integration (always online & responsive)  
- 🌍 Supports Hebrew & English (customizable)  
- 🛠️ Easily extendable command/intent structure

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/yourproject.git
cd yourproject
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

Make sure you have Python 3.10+ and `torch`, `discord.py`, and `numpy` installed.

### 3. Add your tokens

Create a `.env` file or edit the config in `Claude.py`:

```env
DISCORD_TOKEN=your_discord_bot_token
```

---

## 🧠 Training the Model

The model uses a simple bag-of-words + feedforward network trained on a vocabulary of question-intent pairs.

To customize or expand the bot’s understanding, edit the `intents.json` file and retrain:

```bash
python Claude.py
```

---

## 💬 Running the Bot

Once trained, the bot will start and connect to your Discord server:

```bash
python Claude.py
```

You should see:

```
🧠 Training complete - Vocabulary: XXX, Intents: XXX
✅ Bot is now running as Chat-Claude#XXXX
```

---

## 📁 Project Structure

```
📦 yourproject/
├── Claude.py               # Main bot script
├── model.py                # PyTorch model
├── intents.json            # List of patterns and responses
├── data.pth                # Trained model state
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

---

## 🧩 Customization

You can modify `intents.json` to define new intents, patterns, and bot responses.

Each intent has:
- `tag`: internal identifier
- `patterns`: what users might say
- `responses`: how the bot should respond

Example:
```json
{
  "tag": "greeting",
  "patterns": ["hello", "hi", "what's up"],
  "responses": ["Hey there!", "Hi!", "What's going on?"]
}
```

---

## 🖥 Hosting 24/7

To keep the bot online permanently, you can host it on:

- Google Cloud VM
- Replit (with UptimeRobot)
- Railway / Render
- Heroku

---

## 📜 License

This project is open-source and free to use under the MIT License.

---

Made with ❤️ and Python.
