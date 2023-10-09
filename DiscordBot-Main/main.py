import os
from keep_alive import keep_alive
import discord
import datetime
from datetime import datetime
from discord.ext import tasks, commands
from discord import ChannelType
from discord import app_commands
from presence import Pings
from excel import Excel
from list import Lists

intents = discord.Intents.all()
intents.message_content = True
intents.messages = True
intents.members = True

permissions = discord.Permissions.all()
permissions.read_message_history = True
permissions.manage_messages = True

bot = commands.Bot(intents=intents, command_prefix='>')


@bot.event
async def on_ready():
    print("Bot is Ready. " + datetime.now().strftime("%H:%M"))
    loop_always.start()
    try:
        bot.tree.add_command(Lists(bot))
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(f'error: {e}')

@tasks.loop(seconds=60)
async def loop_always():
    day = datetime.now().strftime("%A")
    if day == "Tuesday" or day == "Saturday":
        time = datetime.now().strftime("%H:%M")
        if time == "18:10" or time == "18:50" or time == "17:50":
            print("Lista TW")
            server = bot.get_guild(1100724285246558208)
            sheet = Excel(bot)
            players_list = await sheet.get_players(server)
            await sheet.connect_with_excel(players_list, "TW")
            del sheet
            list = Lists(bot)
            await list.initialize()
            del list
        if time == "18:00":
            print("apollo")
            sheet = Excel(bot)
            await sheet.get_apollo_list()


@bot.tree.command(name="warthog")
@app_commands.describe(member="np. @Krang")
async def warthog(ctx: discord.Interaction, member: discord.Member):
    if member.id == 373563828513931266:
        await ctx.response.send_message(content=f"Chciałbyś!!!", ephemeral=True)
        await member.send(f"{ctx.user} próbowam użyć warthog'a na tobie!")
        member = ctx.user
        await member.send("https://cdn.discordapp.com/attachments/1140638404795695134/1140638477231345685/62df4bc7fe215bf26b369b749fa8ab1bc22a88a969d7d37a330ef10f31645857.gif")
    else:
        await ctx.response.send_message(content="warthog wystarował, wiadomość usunie się utomatycznie po wylądowaniu", ephemeral=True)
    await member.send("✈️✈️✈️ Startujemy ✈️✈️✈️")
    await ctx.delete_original_response()
    for channel in ctx.guild.voice_channels:
        if channel.type == ChannelType.voice:
            temp_channel = bot.get_channel(channel.id)
            try:
                await member.move_to(temp_channel)
            except:
                await member.send("Nie uciekaj!!!")
                return
    await member.send("Wylądowaliśmy")

#@bot.event
#async def on_message(message):
#    if "krang" in message.content or "Krang" in message.content:
#      await message.channel.send("https://media.discordapp.net/attachments/997273379973378050/1054915646258942012/zyndram_pat.gif")
  
@bot.command(name="ping")
async def ping(ctx):
    ping = Pings()
    await ping.initialize(ctx)
    await ping.del_msg()
    await ping.ping_unchecked()


@bot.command(name="ping_t")
async def ping_t(ctx):
    ping = Pings()
    await ping.initialize(ctx)
    await ping.del_msg()
    await ping.ping_tentative()


@bot.command()
async def list_TW(ctx):
    excel = Excel(bot)
    players_list = await excel.get_players(ctx.guild)
    await excel.del_msg(ctx)
    await excel.connect_with_excel(players_list, "TW")


@bot.command()
async def list_adt(ctx):
    try:
        excel = Excel(bot)
        await excel.get_apollo_list()
        await excel.del_msg(ctx)
    except:
        await ctx.send("ups... coś poszło nie tak 'error: get_apollo_list")

@bot.command()
async def ankieta(ctx):
    try:
        excel = Excel(bot)
        players = await excel.get_all_players()
        players = await excel.get_excel_players(players)
        players = await excel.change_to_text(players)
        await excel.del_msg(ctx)
        list = Lists(bot)
        await list.default_embed(ctx.channel, players)
        del list
    except:
        await ctx.send("ups... coś poszło nie tak 'error: ankieta")

@bot.command()
async def ankieta_ping(ctx):
    try:
        excel = Excel(bot)
        players = await excel.get_all_players()
        players = await excel.get_excel_players(players)
        await excel.del_msg(ctx)
        msg_to_send = ""
        i = 0
        for player in players:
          i += 1
          msg_to_send += player.mention
          if i >= 90:
            i = 0
            await ctx.channel.send(msg_to_send)
            msg_to_send = ""
        await ctx.channel.send(msg_to_send)
    except:
        await ctx.send("ups... coś poszło nie tak 'error: ankieta_ping")


keep_alive()
try:
    bot.run(os.environ['TOKEN'])
except discord.HTTPException as e:
    print("\n\n\nBLOCKED BY RATE LIMITS\nRESTARTING NOW\n\n\n")
    os.system("kill 1")
    os.system("python restarter.py")
    if e.status == 429:
        print("The Discord servers denied the connection for making too many requests")
    else:
        raise e
