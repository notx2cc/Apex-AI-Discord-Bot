# Apex-AI-Discord-Bot
An advanced, internet-connected Discord bot powered by Google Gemini 3.5 Flash. Features natural conversational memory, live web-search grounding for factual answers, and a real-time sentiment analysis engine

# 🚀 Apex AI Discord Bot

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![discord.py](https://img.shields.io/badge/Discord.py-2.4.0-5865F2.svg)
![Gemini API](https://img.shields.io/badge/Google%20GenAI-Gemini%203.5%20Flash-0F9D58.svg)
![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)

Apex is an advanced, high-performance conversational AI Discord bot powered by Google's **Gemini 3.5 Flash** model. It features live web-search grounding, allowing it to pull real-time data from the internet to answer questions, analyze trends, and chat naturally with server members.

---

## ✨ Key Features

* **💬 The AI Lounge (Natural Chat):** Set a dedicated channel where the bot will automatically read and reply to messages naturally, keeping conversational context in its memory.
* **🌐 Live Web Grounding:** Apex isn't limited to past training data. It actively searches Google behind the scenes to provide definitive, up-to-date, factual answers.
* **🧠 Dynamic Vibe Check Engine:** Run a real-time sentiment analysis on any topic, game, or internet drama. The bot scans live web trends and provides a definitive Positive/Negative verdict.
* **🧹 Context Management:** Built-in memory systems with manual `/clear` commands to reset the AI's short-term memory and keep conversations fresh.
* **🛡️ Graceful Error Handling:** Built-in rate-limit protection and quota checkers (`429 RESOURCE_EXHAUSTED`) to prevent bot crashes during high traffic.

---

## 🛠️ Slash Commands

| Command | Description | Permissions |
| :--- | :--- | :--- |
| `/ask [prompt] [vibe_check]` | Ask the AI a question, or toggle `vibe_check` to True to run a live sentiment analysis on a trend. | `@everyone` |
| `/help` | Displays the interactive user guide and command list. | `@everyone` |
| `/clear` | Wipes the AI's short-term memory for the current channel. | `@everyone` |
| `/setchannel [channel]` | Designates a specific channel for automatic natural chatting. | `Administrator` |
| `/removechannel` | Removes the automatic chatting designation from the server. | `Administrator` |

> **Pro Tip:** In the dedicated Natural Chat channel, users can simply start their message with `vibecheck [topic]` (e.g., *vibecheck Elden Ring DLC*) to instantly trigger a live sentiment analysis without using slash commands!

---

## 🚀 Installation & Setup

### 1. Clone the Repository
git clone https://github.com/notx2cc/Apex-AI-Discord-Bot.git

cd Apex-AI

---

### 2. Install Dependencies
Make sure you have Python installed, then run:

pip install -r requirements.txt

---

### 3. Environment Variables
Create a file named .env in the root directory of the project and add your API keys:

DISCORD_TOKEN=your_discord_bot_token_here

GEMINI_API_KEY=your_google_gemini_api_key_here

--- 

### 4. Run the Bot

python bot.py
