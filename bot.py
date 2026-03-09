"""
Bot Discord - Chat Événement
Mini-événements automatiques toutes les 20 minutes.
Le plus rapide à taper le mot affiché gagne 1 point.
Rôles à 5, 10, 20 et 50 victoires.
Déploiement Railway : utilise DISCORD_TOKEN, CHANNEL_ID, MONGO_URL en variables d'env.
"""
import asyncio
import json
import os
import random
import time
from pathlib import Path

import discord
from discord.ext import commands

from database import add_win, get_wins, get_leaderboard, load_scores, save_scores
from image_generator import generate_word_image

# Charger la config (priorité aux variables d'environnement pour Railway)
CONFIG_PATH = Path("config.json")
CONFIG = {}
if CONFIG_PATH.exists():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        CONFIG = json.load(f)

TOKEN = os.environ.get("DISCORD_TOKEN") or CONFIG.get("token")
CHANNEL_ID = os.environ.get("CHANNEL_ID")
if CHANNEL_ID is not None:
    CHANNEL_ID = int(CHANNEL_ID)
else:
    CHANNEL_ID = CONFIG.get("channel_id")

if not TOKEN:
    print("Définis DISCORD_TOKEN (variable d'env) ou token dans config.json")
    exit(1)
if CHANNEL_ID is None:
    print("Définis CHANNEL_ID (variable d'env) ou channel_id dans config.json")
    exit(1)
ROLES = CONFIG.get("roles", {})
INTERVAL_MINUTES = CONFIG.get("interval_minutes", 20)
WORDS_FILE = CONFIG.get("words_file", "words.txt")

ROLE_5 = ROLES.get("5_wins")
ROLE_10 = ROLES.get("10_wins")
ROLE_20 = ROLES.get("20_wins")
ROLE_50 = ROLES.get("50_wins")

# Charger les mots
with open(WORDS_FILE, "r", encoding="utf-8") as f:
    WORD_LIST = [w.strip().lower() for w in f.readlines() if w.strip()]

if not WORD_LIST:
    print("Ajoute des mots dans words.txt")
    exit(1)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# État de l'événement en cours
current_event = None
event_lock = asyncio.Lock()


async def assign_roles(member: discord.Member, wins: int) -> list[str]:
    """Assigne les rôles selon le nombre de victoires. Retourne les rôles ajoutés."""
    added = []
    roles_to_add = []

    if wins >= 50 and ROLE_50:
        roles_to_add.append((ROLE_50, "50 victoires"))
    if wins >= 20 and ROLE_20:
        roles_to_add.append((ROLE_20, "20 victoires"))
    if wins >= 10 and ROLE_10:
        roles_to_add.append((ROLE_10, "10 victoires"))
    if wins >= 5 and ROLE_5:
        roles_to_add.append((ROLE_5, "5 victoires"))

    for role_id, name in roles_to_add:
        role = member.guild.get_role(role_id)
        if role and role not in member.roles:
            try:
                await member.add_roles(role)
                added.append(name)
            except discord.Forbidden:
                pass
    return added


async def run_mini_event(channel: discord.TextChannel):
    """Lance un mini-événement : mot dans une image, le plus rapide gagne."""
    global current_event

    async with event_lock:
        if current_event and current_event.get("active"):
            return
        word = random.choice(WORD_LIST)
        winner_event = asyncio.Event()
        current_event = {
            "active": True,
            "word": word,
            "start_time": time.time(),
            "winner": None,
            "winner_event": winner_event,
        }

    image_path = f"data/current_word.png"
    generate_word_image(word, image_path)

    embed = discord.Embed(
        title="Tape le mot dans l'image. Le plus rapide gagne !",
        color=discord.Color.blue(),
    )
    embed.set_image(url="attachment://word.png")
    file = discord.File(image_path, filename="word.png")

    await channel.send(embed=embed, file=file)

    # Attendre une réponse (max 10 min) ou qu'un gagnant soit trouvé
    try:
        await asyncio.wait_for(winner_event.wait(), timeout=600)
    except asyncio.TimeoutError:
        pass
    finally:
        async with event_lock:
            ev = current_event
            current_event = {"active": False}

        if ev and ev.get("winner"):
            user_id, username, elapsed = ev["winner"]
            wins = add_win(user_id, username)
            member = channel.guild.get_member(user_id)
            if member:
                new_roles = await assign_roles(member, wins)
                roles_msg = f" Nouveau(x) rôle(s) : {', '.join(new_roles)} !" if new_roles else ""
            else:
                roles_msg = ""
            await channel.send(
                f"GG <@{user_id}>, t'as été le plus rapide en **{elapsed:.2f}s** ! (+1 point, total: {wins}){roles_msg}"
            )
        else:
            await channel.send("Personne n'a trouvé à temps ! Le mot était : **" + word + "**")


@bot.event
async def on_message(message: discord.Message):
    global current_event

    if message.author.bot:
        await bot.process_commands(message)
        return

    async with event_lock:
        ev = current_event
    if ev and ev.get("active") and message.channel.id == CHANNEL_ID:
        answer = message.content.strip().lower()
        if answer == ev["word"] and ev.get("winner") is None:
            elapsed = time.time() - ev["start_time"]
            ev["winner"] = (message.author.id, str(message.author), elapsed)
            ev["active"] = False
            current_event = ev
            if ev.get("winner_event"):
                ev["winner_event"].set()

    await bot.process_commands(message)


@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user}")
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print("Salon non trouvé. Vérifie channel_id dans config.json")
        return

    # Lancer le premier événement après 30 secondes
    await asyncio.sleep(30)

    while True:
        try:
            await run_mini_event(channel)
        except Exception as e:
            print(f"Erreur événement: {e}")
        await asyncio.sleep(INTERVAL_MINUTES * 60)


@bot.command(name="event")
@commands.has_permissions(manage_guild=True)
async def cmd_event(ctx):
    """Lance un mini-événement manuellement."""
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        await ctx.send("Salon non configuré. Vérifie config.json")
        return
    await ctx.send("Événement lancé !")
    await run_mini_event(channel)


@bot.command(name="points")
async def cmd_points(ctx, user: discord.Member = None):
    """Affiche tes points ou ceux d'un utilisateur."""
    target = user or ctx.author
    wins = get_wins(target.id)
    await ctx.send(f"{target.mention} a **{wins}** victoire(s).")


@bot.command(name="classement")
async def cmd_classement(ctx):
    """Affiche le top 10 du classement."""
    leaderboard = get_leaderboard(10)
    lines = []
    for i, (uid, name, wins) in enumerate(leaderboard, 1):
        lines.append(f"{i}. <@{uid}> - {wins} victoire(s)")
    msg = "\n".join(lines) if lines else "Aucun participant pour le moment."
    embed = discord.Embed(title="Classement Chat Événement", description=msg, color=discord.Color.gold())
    await ctx.send(embed=embed)


def main():
    bot.run(TOKEN)


if __name__ == "__main__":
    main()
