import os
from keep_alive import keep_alive
import discord
import datetime
from datetime import datetime
from discord.ext import tasks, commands
from discord import app_commands, ui, ChannelType
from excel import Excel


intents = discord.Intents.all()
intents.message_content = True
intents.messages = True
intents.members = True

permissions = discord.Permissions.all()
permissions.read_message_history = True
permissions.manage_messages = True

bot = commands.Bot(intents=intents, command_prefix='>')

class MyView(discord.ui.View):
    def __init__(self) -> None:
      super().__init__(timeout = None)
      
    @discord.ui.button(label="Dodaj Gracza", custom_id="button-1", style=discord.ButtonStyle.success, emoji="🗂")
    async def button_add_player(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(MyModelAddPlayer(interaction))

    @discord.ui.button(label="Usuń Gracza", custom_id="button-2", style=discord.ButtonStyle.danger , emoji="💀")
    async def button_del_player(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == 373563828513931266:
          await interaction.response.send_modal(MyModelDelPlayer(interaction))
          return
        for role in interaction.user.roles:
          if role.id == 1100724285305274439 or role.id == 1100724285305274441:
            await interaction.response.send_modal(MyModelDelPlayer(interaction))
            return
        await interaction.response.send_message('Nie masz uprawnień!!', ephemeral=True)
        return

class MyReset(discord.ui.View):
    def __init__(self) -> None:
      super().__init__(timeout = None)
      
    @discord.ui.button(label="Wyczyść tabele", custom_id="button-3", style=discord.ButtonStyle.primary)
    async def button_reset_TW(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('wybierz lineup!! (**UWAGA** wybranie odrazu czyści !!!)', ephemeral=True, view=MySelect())

class MySelect(discord.ui.View):
    excel = Excel()
    select_options = excel.get_name_sheet()
    @discord.ui.select(placeholder = "Który lineup", options=select_options)
    async def select_reset_TW(self, interaction: discord.Interaction, select_item: discord.ui.Select):
      try:
        await interaction.response.send_message('Czyszczenie...', ephemeral=True)
        excel = Excel(interaction)
        await excel.reset_list_TW(select_item.values[0])
        await interaction.edit_original_response(content='Czyszczenie wykonane!!!')
      except:
        await interaction.response.send_message('coś poszło nie tak!!', ephemeral=True)

class MyModelAddPlayer(discord.ui.Modal, title='Formularz'):
    def __init__(self, interaction):
      super().__init__()
      self.interaction = interaction
      
    name = ui.TextInput(label='Nazwa (Pamiętaj najpier zmień nick!)', placeholder="Rien")
    in_house = ui.TextInput(label='Czy w rodzie?', placeholder="tak/nie", required=False)
    rekrut = ui.TextInput(label='Czy przeszedł rekrutacje?', placeholder="tak/nie", required=False)
    comment = ui.TextInput(label='Komentarz (opcjonalne)', style=discord.TextStyle.long, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Formularz został wysłany. Na {interaction.guild.get_channel(1100724286139940948).mention} zobacz podsumowanie.', ephemeral=True)
        excel = Excel(self.interaction)
        await excel.add_player_to_excel(self.name, self.in_house, self.rekrut, self.comment)

class MyModelDelPlayer(discord.ui.Modal, title='Formularz'):
    def __init__(self, interaction):
      super().__init__()
      self.interaction = interaction
      
    name = ui.TextInput(label='Nazwa', placeholder="Rien")
    comment = ui.TextInput(label='Info dlaczego został wywalony (opcjonalne)', style=discord.TextStyle.long, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Formularz został wysłany. Na {interaction.guild.get_channel(1100724286139940948).mention} zobacz podsumowanie.', ephemeral=True)
        excel = Excel(self.interaction)
        await excel.del_player_to_excel(self.name, self.comment)

@bot.event
async def on_ready():
    bot.add_view(MyView())
    bot.add_view(MyReset())
    print("Bot is Ready. " + datetime.now().strftime("%H:%M"))
  
@bot.command()
async def rekrutacja(ctx):
    await ctx.send("Jakiś tekst, Demi wymyśl coś!!", view=MyView())

@bot.command()
async def reset_TW(ctx):
    await ctx.send("Przycisk do czyszczenia tabel na TW, używaj go z głową!! \nJakby spał obudz mnie wchodząc w ten link: https://diesmeda-rekruter.czarny77.repl.co", view=MyReset())

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
