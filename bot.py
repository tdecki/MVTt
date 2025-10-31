import discord
from discord.ext import commands
import json
from flask import Flask
import threading
import os

app = Flask('')

@app.route('/')
def home():
    return "Bot je aktivní!"

def run():
    port = int(os.environ.get("PORT", 8080))  # Render nastaví PORT automaticky
    app.run(host='0.0.0.0', port=port)

threading.Thread(target=run).start()

# Prefix bota a intent
intents = discord.Intents.default()
intents.message_content = True  # aby bot mohl číst příkazy
bot = commands.Bot(command_prefix="!", intents=intents)

# Název souboru s daty
DATA_FILE = "data.json"

# Načti data ze souboru (nebo vytvoř prázdná)
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

# Ulož data do souboru
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Načti data při spuštění
data = load_data()

@bot.event
async def on_ready():
    print(f"Přihlášen jako {bot.user}")

@bot.command()
async def zapsat(ctx, minuty: int):
    user_id = str(ctx.author.id)
    username = ctx.author.name

    if user_id not in data:
        data[user_id] = {"name": username, "minutes": 0}

    data[user_id]["minutes"] += minuty
    save_data(data)
    await ctx.send(f"✅ {username}, přičetl jsem ti **{minuty} minut**. Celkem máš **{data[user_id]['minutes']} minut**.")

@bot.command()
async def info(ctx):
    if not data:
        await ctx.send("ℹ️ Zatím nikdo nic nezapsal.")
        return

    # Seřadíme podle minut
    sorted_data = sorted(data.values(), key=lambda x: x["minutes"], reverse=True)

    message = "**📊 Přehled zapsaných minut:**\n"
    for i, user in enumerate(sorted_data, start=1):
        message += f"{i}. {user['name']} – {user['minutes']} minut\n"

    await ctx.send(message)

@bot.command()
async def vymazat(ctx):
    # Kontrola, aby to mohl použít jen administrátor
    if ctx.author.guild_permissions.administrator:
        data.clear()
        save_data(data)
        await ctx.send("🗑️ Všechna data byla vymazána (nový měsíc začíná).")
    else:
        await ctx.send("❌ Tento příkaz může použít jen administrátor.")

# Spuštění bota – vlož sem svůj token
import os
bot.run(os.getenv("DISCORD_TOKEN"))
