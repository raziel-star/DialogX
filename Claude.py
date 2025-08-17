import discord
from google import genai

GOOGLE_API_KEY = ""
DISCORD_BOT_TOKEN = ""

client = genai.Client(api_key=GOOGLE_API_KEY)

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Client(intents=intents)

conversation_memory = {}

# פונקציה שמוציאה טקסט בצורה בטוחה מהתשובה של Gemini
def extract_text(response):
    try:
        if hasattr(response, "text") and response.text:
            return response.text
        return response.candidates[0].content.parts[0].text
    except Exception:
        return "לא הצלחתי לקבל תשובה מהמודל."

@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user}!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if not message.content.startswith("!"):
        return

    server_id = message.guild.id if message.guild else "DM"
    channel_name = getattr(message.channel, "name", "Private")
    user_name = message.author.name

    user_input = message.content[1:].strip()

    if server_id not in conversation_memory:
        conversation_memory[server_id] = []

    conversation_memory[server_id].append(f"{user_name} said: {user_input}")

    prompt = (
        f"You are Chat-Claude, a witty and funny AI bot for Discord.\n"
        f"You are chatting in server '{message.guild.name if message.guild else 'DM'}', channel '{channel_name}'.\n"
        f"You talk with user '{user_name}'.\n"
        f"Here is the conversation so far:\n"
        + "\n".join(conversation_memory[server_id]) +
        "\nRespond humorously and helpfully to the last message. "
        "Limit your answer to about 1000 tokens or fewer. "
        "You speak Hebrew and English. If user speaks Hebrew, respond in Hebrew; if English, respond in English. "
        "You are based on a large language model created by Google."
        "אם אומרים ליצור פוסטים וטיפים בתוך השרת תעשה את זה מפורט ובלי יותר אנלוגיות תהיה מצחיק אבל תסביר כמו שצריך ומפורט."
        "אתה לא אומר שם קבוע אם אתה מזכיר שם רק מישהו שמדבר איתך המשתמש שמדבר איתך את תציג את השם שלו."
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=[prompt]
        )
    except Exception as e:
        await message.channel.send(f"Error with API call: {e}")
        return

    bot_response = extract_text(response)

    conversation_memory[server_id].append(f"Chat-Claude said: {bot_response}")

    max_discord_length = 2000
    for i in range(0, len(bot_response), max_discord_length):
        await message.channel.send(bot_response[i:i + max_discord_length])

bot.run(DISCORD_BOT_TOKEN)
