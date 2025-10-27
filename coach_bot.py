import os
import discord
import openai
from dotenv import load_dotenv

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not DISCORD_TOKEN:
    raise RuntimeError("DISCORD_TOKEN not set. Please add it to your .env file.")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not set. Please add it to your .env file.")

openai.api_key = OPENAI_API_KEY

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

async def ask_openai(prompt: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful goals and planning coach. "
                    "Provide supportive, practical advice to help users set goals "
                    "and outline step-by-step plans to achieve them. Respond in a "
                    "friendly, encouraging tone."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=200,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()

@client.event
async def on_ready():
    print(f"Logged in as {client.user} (ID: {client.user.id})")
    print("------")

@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

    content = message.content.strip()
    lower_content = content.lower()

    if lower_content.startswith("$hello"):
        await message.channel.send(
            "Hello! I'm your coaching bot. Ask me about your goals by typing `$coach` followed by your "
            "goal or question, and I'll help you plan actionable steps."
        )
        return

    if lower_content.startswith("$coach"):
        question = content[len("$coach"):].strip()
        if not question:
            await message.channel.send(
                "Please provide a goal or question after the `$coach` command."
            )
            return

        async with message.channel.typing():
            try:
                reply = await ask_openai(question)
                await message.channel.send(reply)
            except Exception as exc:
                await message.channel.send(
                    "Sorry, I ran into an error while processing your request."
                )
                print(f"Error while handling question '{question}':", exc)
        return

def main() -> None:
    client.run(DISCORD_TOKEN)

if __name__ == "__main__":
    main()
