import discord
from discord import app_commands
from discord.ext import commands
from google import genai
from google.genai import types  # <-- Required for System Instructions and Tools
import os
import json
import logging
import traceback
from dotenv import load_dotenv

# --- 1. PROFESSIONAL LOGGING ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("ApexBot")

# --- 2. ENVIRONMENT & INITIALIZATION ---
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not DISCORD_TOKEN or not GEMINI_API_KEY:
    logger.critical("Missing environment variables! Check your .env file.")
    exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_ID = "gemini-3.5-flash"

# --- SYSTEM INSTRUCTIONS WITH LIVE GOOGLE SEARCH UNLOCKED ---
BOT_CONFIG = types.GenerateContentConfig(
    tools=[types.Tool(google_search=types.GoogleSearch())],
    system_instruction=(
        "You are Apex, a cool, helpful, and internet-connected Discord bot. "
        "You have direct access to live Google Search results. Use them to provide up-to-date, definitive, and factual answers. "
        "Keep your responses brief, concise, and straight to the point. "
        "Do not write long essays, lists, or deep-dive explanations unless the user explicitly asks for a long answer. "
        "Converse casually like a normal person in a chat room."
    )
)

chat_sessions = {}

# --- LIVE WEB VIBE CHECK CORE ENGINE ---
def run_web_vibe_check(topic: str):
    """
    Executes a live search-grounded sentiment analysis on any given trend, meme, or topic.
    """
    vibe_config = types.GenerateContentConfig(
        tools=[types.Tool(google_search=types.GoogleSearch())],
        system_instruction=(
            "You are an expert internet culture and trend sentiment analyst. "
            "Search the live web to discover the current context and public perception of the user's query. "
            "Explain the current 'vibe' in 2-3 concise sentences. "
            "At the very end of your response, you MUST include a clean verdict line exactly formatted like this:\n"
            "VERDICT: [POSITIVE or NEGATIVE]"
        )
    )
    
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=f"What is the current internet sentiment/vibe of: {topic}",
        config=vibe_config
    )
    
    text = response.text
    
    if "VERDICT: POSITIVE" in text.upper():
        color = 0x10b981  # Green
        emoji = "✨"
    else:
        color = 0xef4444  # Red
        emoji = "⚠️"
        
    return text, color, emoji


# --- 3. DATABASE (JSON CONFIGURATION) ---
CONFIG_FILE = "server_configs.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)

server_configs = load_config()

# --- 4. CORE BOT CLASS ARCHITECTURE ---
class FancyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        self.tree.on_error = self.on_tree_error
        await self.tree.sync()
        logger.info("Application slash commands synchronized globally.")

    async def on_tree_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            seconds_left = round(error.retry_after, 1)
            embed = discord.Embed(
                title="⚠️ Rate Limit Enforced",
                description=f"Please pause for **{seconds_left}s** before requesting again.",
                color=0xf59e0b
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        elif isinstance(error, app_commands.MissingPermissions):
            embed = discord.Embed(
                title="🚫 Access Denied",
                description="You lack the structural permissions required to execute this command.",
                color=0xef4444
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # NEW: Catch the Google API Quota Limit for Slash Commands
        elif "429" in str(error) or "RESOURCE_EXHAUSTED" in str(error):
            embed = discord.Embed(
                title="⏳ AI Quota Reached",
                description="Apex has processed too many requests recently and hit its API limit. Please try again later!",
                color=0xf59e0b
            )
            try:
                if interaction.response.is_done():
                    await interaction.followup.send(embed=embed, ephemeral=True)
                else:
                    await interaction.response.send_message(embed=embed, ephemeral=True)
            except discord.errors.InteractionResponded:
                pass
            return

        logger.error(f"Uncaught command exception: {error}")
        err_embed = discord.Embed(
            title="💥 Internal System Exception",
            description="An anomaly occurred within the application core.",
            color=0xef4444
        )
        try:
            if interaction.response.is_done():
                await interaction.followup.send(embed=err_embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=err_embed, ephemeral=True)
        except Exception:
            pass

bot = FancyBot()

# --- 5. INTERACTIVE UI COMPONENTS ---
class ChatControls(discord.ui.View):
    def __init__(self, channel_id):
        super().__init__(timeout=None)
        self.channel_id = channel_id

    @discord.ui.button(label="Clear History", style=discord.ButtonStyle.secondary, emoji="🧹")
    async def clear_history(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.channel_id in chat_sessions:
            del chat_sessions[self.channel_id]
            logger.info(f"Context purged for channel ID: {self.channel_id} by {interaction.user}")
            await interaction.response.send_message("🧹 Conversation history wiped clean for this channel!", ephemeral=True)
        else:
            await interaction.response.send_message("History is already empty.", ephemeral=True)

# --- 6. DYNAMIC PRESENCE ---
async def update_presence():
    server_count = len(bot.guilds)
    activity = discord.Activity(
        type=discord.ActivityType.watching, 
        name=f"⚡ /help • 📊 {server_count} guilds"
    )
    await bot.change_presence(status=discord.Status.online, activity=activity)

@bot.event
async def on_ready():
    await update_presence()
    logger.info(f"Operational deployment successful. Authenticated as {bot.user}")

@bot.event
async def on_guild_join(guild):
    await update_presence()

@bot.event
async def on_guild_remove(guild):
    await update_presence()

# --- 7. AUTO-REPLY MESSAGE LISTENER (NATURAL CHAT LOUNGE) ---
@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    await bot.process_commands(message)

    guild_id = str(message.guild.id)
    if guild_id in server_configs and server_configs[guild_id] == message.channel.id:
        
        async with message.channel.typing():
            content_stripped = message.content.strip()
            
            # INTEGRATION: Check if user is invoking a live vibe check directly in chat
            if content_stripped.lower().startswith("vibecheck "):
                topic = content_stripped[10:].strip()
                try:
                    text, color, emoji = run_web_vibe_check(topic)
                    embed = discord.Embed(
                        title=f"{emoji} Live Web Sentiment Analysis",
                        description=text,
                        color=color,
                        timestamp=message.created_at
                    )
                    embed.set_footer(text=f"Engine: {MODEL_ID.replace('-', ' ').title()} • Live Search Active")
                    await message.channel.send(embed=embed, reference=message)
                    return
                except Exception as e:
                    logger.error(f"Chat lounge vibe check failed: {e}")
                    # Quota Check
                    if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                        await message.channel.send("⏳ **AI Quota Reached:** I've processed too many requests recently. Please give me a break!", reference=message)
                    else:
                        await message.channel.send("⚠️ My connection to the live trend index failed.", reference=message)
                    return

            # Standard chat continuation logic
            channel_id = message.channel.id
            if channel_id not in chat_sessions:
                chat_sessions[channel_id] = {
                    "chat": client.chats.create(model=MODEL_ID, config=BOT_CONFIG),
                    "model": MODEL_ID
                }
            
            chat = chat_sessions[channel_id]["chat"]

            try:
                response = chat.send_message(message.content)
                text = response.text

                if len(text) > 2000:
                    text = text[:1996] + "..."

                await message.channel.send(text, reference=message)

            except Exception as e:
                logger.error(f"Auto-reply exception: {e}")
                # Quota Check
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    await message.channel.send("⏳ **AI Quota Reached:** I've processed too many requests recently. Please give me a break!", reference=message)
                else:
                    await message.channel.send("⚠️ My communication circuits encountered an error while processing that.", reference=message)

# --- 8. ADVANCED SLASH COMMANDS ---
@bot.tree.command(name="help", description="Learn how to interact with Apex AI.")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🤖 Apex AI User Guide",
        description="I am an advanced conversational AI powered by Google Gemini. Here is how you can interact with me:",
        color=0x2b2d31
    )
    
    embed.add_field(
        name="💬 The AI Lounge (Natural Chat)",
        value="Type normally in the set channel to chat. To run a live sentiment check on any topic here, simply start your message with **`vibecheck [topic]`** (e.g., *vibecheck Elden Ring DLC*).",
        inline=False
    )
    
    embed.add_field(
        name="✨ `/ask [prompt] [vibe_check]`",
        value="Ask standard questions, or set the optional `vibe_check` toggle parameter to **True** to analyze internet sentiment dynamically.",
        inline=False
    )
    
    embed.add_field(
        name="🧹 `/clear`",
        value="Wipes my short-term memory for the current channel so we can start a brand new topic.",
        inline=False
    )

    embed.add_field(
        name="⚙️ Admin Commands",
        value="`/setchannel`: Designates the current channel for automatic natural chat.\n`/removechannel`: Stops the automatic replies.",
        inline=False
    )

    if bot.user.display_avatar:
        embed.set_thumbnail(url=bot.user.display_avatar.url)
        
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="clear", description="Wipe the AI's short-term memory for this channel.")
async def clear_command(interaction: discord.Interaction):
    channel_id = interaction.channel_id
    if channel_id in chat_sessions:
        del chat_sessions[channel_id]
        await interaction.response.send_message("🧹 Memory wiped! What would you like to talk about next?")
    else:
        await interaction.response.send_message("My memory for this channel is already empty.", ephemeral=True)

@bot.tree.command(name="setchannel", description="[ADMIN] Set a dedicated channel for automatic AI replies.")
@app_commands.checks.has_permissions(administrator=True)
async def setchannel(interaction: discord.Interaction, channel: discord.TextChannel):
    guild_id = str(interaction.guild.id)
    server_configs[guild_id] = channel.id
    save_config(server_configs)
    
    embed = discord.Embed(
        title="✅ AI Channel Configured",
        description=f"I will now automatically read and reply naturally to all messages in {channel.mention} using live web answers.",
        color=0x10b981
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="removechannel", description="[ADMIN] Stop the bot from automatically replying in the set channel.")
@app_commands.checks.has_permissions(administrator=True)
async def removechannel(interaction: discord.Interaction):
    guild_id = str(interaction.guild.id)
    if guild_id in server_configs:
        del server_configs[guild_id]
        save_config(server_configs)
        
        embed = discord.Embed(
            title="🛑 AI Channel Removed",
            description="I will no longer automatically reply to messages. You can still use `/ask`.",
            color=0xef4444
        )
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("There is no active AI channel for this server.", ephemeral=True)

@bot.tree.command(name="ask", description="Have a smart, continuous conversation with Gemini")
@app_commands.describe(
    prompt="What would you like to ask or tell the AI?",
    vibe_check="Set to True to transform this prompt into a live web trend vibe check."
)
@app_commands.checks.cooldown(1, 4.0, key=lambda i: i.user.id)
async def ask(interaction: discord.Interaction, prompt: str, vibe_check: bool = False):
    await interaction.response.defer()
    
    # INTEGRATION: Check if the optional vibe_check switch was flipped on the slash command
    if vibe_check:
        try:
            text, color, emoji = run_web_vibe_check(prompt)
            embed = discord.Embed(
                title=f"{emoji} Live Web Sentiment Analysis",
                description=text,
                color=color,
                timestamp=interaction.created_at
            )
            embed.set_author(
                name=f"Target: \"{prompt}\"",
                icon_url=interaction.user.display_avatar.url if interaction.user.display_avatar else None
            )
            embed.set_footer(text=f"Engine: {MODEL_ID.replace('-', ' ').title()} • Live Search Active")
            await interaction.followup.send(embed=embed)
            return
        except Exception as e:
            logger.error(f"Slash command ask-vibe check exception: {e}")
            # The exception here gets passed to on_tree_error, so 429s are handled automatically
            raise e

    # Standard /ask logic
    channel_id = interaction.channel_id
    if channel_id not in chat_sessions or chat_sessions[channel_id]["model"] != MODEL_ID:
        chat_sessions[channel_id] = {
            "chat": client.chats.create(model=MODEL_ID, config=BOT_CONFIG),
            "model": MODEL_ID
        }
    
    chat = chat_sessions[channel_id]["chat"]

    try:
        response = chat.send_message(prompt)
        text = response.text

        if len(text) > 1900:
            text = text[:1900] + "...\n*(Response truncated due to length)*"

        quoted_prompt = "\n".join([f"> {line}" for line in prompt.split("\n")])

        embed = discord.Embed(
            description=f"{quoted_prompt}\n\n{text}", 
            color=0x2b2d31,
            timestamp=interaction.created_at
        )

        embed.set_author(
            name=f"{interaction.user.display_name} asked:", 
            icon_url=interaction.user.display_avatar.url
        )

        if bot.user.display_avatar:
            embed.set_thumbnail(url=bot.user.display_avatar.url)

        embed.set_footer(text=f"Engine: {MODEL_ID.replace('-', ' ').title()} • Grounded Web Search Active")
        view = ChatControls(channel_id)

        await interaction.followup.send(embed=embed, view=view)

    except Exception as e:
        logger.error(f"API standard exception on execution: {e}")
        # Passing this exception up will let the on_tree_error catch the 429
        raise e 

# --- 9. RUN EXECUTION ---
bot.run(DISCORD_TOKEN, log_handler=None)
