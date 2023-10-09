class Pings():
    async def initialize(self, ctx):
        self.ctx = ctx
        self.msg = await self.get_msg(self.ctx)
        self.role = await self.get_role()
        self.players_list = await self.get_players_list()
        self.fields = self.msg.embeds[0].fields

    async def ping_unchecked(self):
        if self.players_list is None:
            return
        
        max_fields = len(self.fields)
        for i in range(2, max_fields):
            players = self.fields[i].value[4:].splitlines()
            if len(players) > 0 and players is not None:
                for player in players:
                    player = player.replace('\\', '')

                    for p_list in self.players_list:
                        if p_list.nick != None:
                            if player == p_list.nick:
                                self.players_list.remove(p_list)
                                break
                        elif p_list.global_name != None:
                            if player == p_list.global_name:
                                self.players_list.remove(p_list)
                                break
                        else:
                            if player == p_list.name:
                                self.players_list.remove(p_list)
                                break
        await self.create_msg_to_send(self.players_list)
        #print(self.players_list)

    async def ping_tentative(self):
        if self.players_list is None:
            return
        ping_players = []

        for field in self.fields:
            if "Tentative" in field.name:
                players = field.value[4:].splitlines()
                if len(players) > 0 and players is not None:
                    for player in players:
                        player = player.replace('\\', '')

                        for p_list in self.players_list:
                            if p_list.nick is not None:
                                if player == p_list.nick:
                                    ping_players.append(p_list)
                                    break
                            elif p_list.global_name != None:
                                if player == p_list.global_name:
                                    ping_players.append(p_list)
                                    break
                            else:
                                if player == p_list.name:
                                    ping_players.append(p_list)
                                    break
        
        await self.create_msg_to_send(ping_players)

    async def get_role(self):
        if self.msg is None:
            return None
        return self.msg.content

    async def get_msg(self, ctx):
        messages = [message async for message in ctx.channel.history(limit=30)]
        for msg in messages:
            if msg.author.name == 'Apollo':
                return msg
        return None

    async def get_players_list(self):
        players_list = []
        for member in self.ctx.guild.members:
            for role in member.roles:
                if f"<@&{role.id}>" == self.role:
                    players_list.append(member)
        if len(players_list) > 0:
            return players_list
        else:
            await self.msg_author.send("Error, Najpewniej została wybrana zła rola, albo nik jej nie posiada")
        return None
    
    async def create_msg_to_send(self, list):
        msg_to_send = ""
        count = 0
        for player in list:
            count += 1
            msg_to_send += f"<@{player.id}> "
        try:
            await self.ctx.send(f'{msg_to_send} ({count})')
        except:
            await self.msg_author.send("Nie ma nikogo do pingowania")

    async def del_msg(self):
        async for message in self.ctx.channel.history(limit=1):
            self.msg_author = message.author
            await message.delete()