from discord import app_commands
import discord

class Lists(app_commands.Group):
    def __init__(self, bot):
        super().__init__(name="lista")
        self.guild = bot.get_guild(1100724285246558208)
        self.TW_list_channel = bot.get_channel(1100887633976119439)

        self.house_roles = ["Episkopat", "Gwardia Papieska"]

    async def initialize(self):
        house_player_list = []
        sum_players = 0
        for house_role in self.house_roles:
            house_player_list.append(await self.get_players_by_roles(house_role, self.guild.voice_channels))
            sum_players += len(house_player_list[len(house_player_list)-1])
            
        self.embed = discord.Embed(title=f"Players: {sum_players}", color=0x9900FF)

        for i in range(len(self.house_roles)):
            await self.create_embed(house_player_list[i], self.house_roles[i])

        try:
            await self.TW_list_channel.send(embed=self.embed)
        except:
            print("coś poszło nie tak, możeliwe że nie masz uprawnień do danego kanału albo dany kanał został usunięty")

    async def get_players_by_roles(self, house_role, voice_channels):
        players_list = ()
        for channel in voice_channels:
            if channel.members != []:
                for member in channel.members:
                    for role in member.roles:
                        if role.name == str(house_role):
                            if member.nick != None:
                                players_list += (member.nick,)
                            elif member.global_name != None:
                                players_list += (member.global_name,)
                            elif member.name != None:
                                players_list += (member.name,)
        return players_list
    
    async def get_players(self, voice_channels):
        channels = {}
        players_list = ()
        self.count_members = 0
        for channel in voice_channels:
            if channel.members != []:
                for member in channel.members:
                    self.count_members += 1
                    if member.nick != None:
                        players_list += (member.nick,)
                    elif member.global_name != None:
                        players_list += (member.global_name,)
                    elif member.name != None:
                        players_list += (member.name,)
                channels[channel] = players_list
                players_list = ()
        return channels

    async def create_embed(self, players_list, field_name):
        house_description = []
        house_description_2 = []
        players_count = 0
        for player in players_list:
            if players_count < 50:
                house_description += '\n {}'.format(player)
            else:
                house_description_2 += '\n {}'.format(player)
            players_count += 1
        self.embed.add_field(name=f"{field_name}: {len(players_list)}", value=''.join(house_description), inline=True)
        if players_count > 50:
            self.embed.add_field(name=f"{field_name}:", value=''.join(house_description_2), inline=True)
            
    async def default_embed(self, channel,  msg):
      try:
        self.embed = discord.Embed(title=f"Brak Ankiet", color=0x9900FF)
        await self.create_embed(msg, "-")
        await channel.send(embed=self.embed)
      except:
        await channel.send(f"ups.. coś poszło nie tak 'error default_embed'")
  
    @app_commands.command(name="roli")
    @app_commands.describe(role = "np. @DiesMeda")
    async def list_role(self, ctx, role : discord.Role):
        try:
            await ctx.response.send_message(f"Pracuje...")
            players_list = await self.get_players_by_roles(role, ctx.guild.voice_channels)
            self.embed = discord.Embed(title=f"Players: {len(players_list)}", color=0x9900FF)
            await self.create_embed(players_list, role)
            await ctx.delete_original_response()
            await ctx.channel.send(embed=self.embed)
        except:
           await ctx.response.send_message(f"ups.. coś poszło nie tak 'error list_role'")

    @app_commands.command(name="tw")
    async def list_TW(self, ctx):
        try:
            await ctx.response.send_message(f"Pracuje...")
            await self.initialize()
            await ctx.delete_original_response()
        except:
            await ctx.response.send_message(f"ups.. coś poszło nie tak 'error list_TW'")

    @app_commands.command(name="channels")
    async def list_channels(self, ctx):
        await ctx.response.send_message(f"Pracuje...")
        channels = await self.get_players(ctx.guild.voice_channels)

        self.embed = discord.Embed(title=f"Players: {self.count_members}", color=0x9900FF)

        for channel_name, players in channels.items():
            #print(f"{channel_name}: {players}")
            await self.create_embed(players, channel_name)
        await ctx.channel.send(embed=self.embed)
        await ctx.delete_original_response()