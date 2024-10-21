import discord
from discord.ext import commands
import json
import os
from dotenv import load_dotenv
from keep_alive import keep_alive

from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Le bot est en ligne"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start

load_dotenv()
token = os.environ['TOKEN']

class BotMain(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Bot connecté en tant que {self.bot.user}!')


  
# Créer une instance du bot
intents = discord.Intents.all()
intents.message_content = True
intents.voice_states = True
intents.guilds = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Charger ou initialiser les données utilisateur
if os.path.exists('userdata.json'):
    with open('userdata.json', 'r') as f:
        user_data = json.load(f)
else:
    user_data = {}

# Sauvegarder les données utilisateur
def save_user_data():
    with open('userdata.json', 'w') as f:
        json.dump(user_data, f)

# Vérifier et attribuer des rôles
async def check_roles(member):
    user_id = str(member.id)
    if user_id in user_data:
        messages = user_data[user_id]['messages']
        voice_time = user_data[user_id]['voice_time']

        if messages >= 5 and 'Level 1' not in [role.name for role in member.roles]:
            role = discord.utils.get(member.guild.roles, name='Level 1')
            if role:
                await member.add_roles(role)

        if voice_time >= 3600 and 'Level 2' not in [role.name for role in member.roles]:
            role = discord.utils.get(member.guild.roles, name='Level 2')
            if role:
                await member.add_roles(role)

@bot.event
async def on_ready():
    print(f'Bot {bot.user} is online!')

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = str(message.author.id)
    if user_id not in user_data:
        user_data[user_id] = {'messages': 0, 'voice_time': 0}

    user_data[user_id]['messages'] += 1
    save_user_data()
    await check_roles(message.author)  # Vérifier les rôles après chaque message
    await bot.process_commands(message)

@bot.event
async def on_voice_state_update(member, before, after):
    user_id = str(member.id)

    if user_id not in user_data:
        user_data[user_id] = {'messages': 0, 'voice_time': 0}

    if before.channel is None and after.channel is not None:
        user_data[user_id]['start_time'] = discord.utils.utcnow()

    elif before.channel is not None and after.channel is None:
        if 'start_time' in user_data[user_id]:
            duration = (discord.utils.utcnow() - user_data[user_id]['start_time']).total_seconds()
            user_data[user_id]['voice_time'] += duration
            del user_data[user_id]['start_time']
            save_user_data()
            await check_roles(member)  # Vérifier les rôles après la mise à jour de l'état vocal

@bot.command()
async def level(ctx):
    user_id = str(ctx.author.id)
    if user_id in user_data:
        messages = user_data[user_id]['messages']
        voice_time = user_data[user_id]['voice_time']
        await ctx.send(f'Vous avez envoyé {messages} messages et passé {voice_time:.2f} secondes en vocal.')
    else:
        await ctx.send('Vous n\'avez pas encore de données.')






@bot.command()
async def example_embed(ctx: commands.Context) -> discord.Message:
    test_embed = discord.Embed(
        title="Titre de test",
        description="Je suis une description de test",
        colour=discord.Color.red()
    )

    test_embed.add_field(
        name="Je suis un champ de texte",
        value="Je suis une valeur de champ de texte"
    )


    test_embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
    test_embed.set_thumbnail(url=ctx.guild.icon.url)
    test_embed.set_image(url=ctx.author.display_avatar.url)
    test_embed.set_footer(icon_url=ctx.guild.icon.url, text="Je suis un footer")


    return await ctx.send(embed=test_embed)


@bot.command()
async def rules_embed(ctx:commands.Context) -> discord.Message:
    has_PA = ctx.author.guild_permissions.administrator
    if not has_PA:
        return await ctx.send("Vous n'avez pas les permissions pour utiliser cette commande.")
    
    rules_embed = discord.Embed(
        title="Bienvenue sur BSquad ! Avant de rejoindre les autres membres du serveur, nous te conseillons de lire les règles afin de ne pas rencontrer des sanctions !",
        colour=discord.Color.red()
    )

    return await ctx.send(embed=rules_embed)

@bot.command()
async def rules_embed2(ctx:commands.Context) -> discord.Message:
    has_PA = ctx.author.guild_permissions.administrator
    if not has_PA:
        return await ctx.send("Vous n'avez pas les permissions pour utiliser cette commande.")
    
    rules_embed_2 = discord.Embed()
    rules_embed_2.set_image(url="https://cdn.discordapp.com/attachments/1292914120928002113/1296846696101187625/Regles.gif?ex=6715c05a&is=67146eda&hm=139031ec407006534cea6c8ab030d1ac142fdf705ccc7e2709c5597c4e017737&")

    return await ctx.send(embed=rules_embed_2)

@bot.command()
async def rules(ctx:commands.Context, *, message:str) -> discord.Message:
    await ctx.send(message)


# Charger les cogs
async def setup():
    await bot.add_cog(BotMain(bot))

# Remplacez 'YOUR_TOKEN' par le token de votre bot
keep_alive()

bot.run(token)
