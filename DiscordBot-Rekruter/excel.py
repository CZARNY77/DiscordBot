import os
import json
import discord
from discord.ext import commands
import datetime
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials


class Excel(commands.Cog):
    def __init__(self, interaction = None):
        credentials_info = json.loads(os.getenv('credentials_key'))
        self.credentials = service_account.Credentials.from_service_account_info(credentials_info)
        self.DISCOVERY_SERVICE_URL = 'https://sheets.googleapis.com/$discovery/rest?version=v4'
        self.service = build('sheets', 'v4', credentials=self.credentials, discoveryServiceUrl=self.DISCOVERY_SERVICE_URL)
        self.spreadsheet_id = os.getenv('excel_link')
        self.spreadsheet_TW_id = os.getenv('TW_excel_link')
        self.player_sheet = "Gracze"
        self.player_sheet_id = '1175773292'
        self.archives_sheet = "Archiwum"
        self.interaction = interaction
        if interaction != None:
          self.members = interaction.guild.members
          self.log_channel = interaction.guild.get_channel(1100724286139940948)

    async def add_player_to_excel(self, player_name, in_house, recruit, comment):
        try:
            values = self.get_values(self.spreadsheet_id, self.player_sheet)
            row_num = len(values[0][0]) + 1
            member_mention = ""
            player_found = False
          
            for v in values[0][0]:
              if v.lower() == str(player_name).lower():
                player_found = True
                await self.create_embed(4, player_name)
            if player_found:
              pass
            for member in self.members:
              if str(member.nick).lower() == str(player_name).lower():
                member_mention = member
                break

              elif str(member.global_name).lower() == str(player_name).lower():
                member_mention = member
                break

              elif str(member.name).lower() == str(player_name).lower():
                member_mention = member
                break
              else:
                  member_mention = "-"

            
            # wartość do wpisania
            range_name = f'{self.player_sheet}!{chr(ord("A"))}{row_num}:{chr(ord("E"))}{row_num}'
            body = {
              'values': [[str(player_name),
                         datetime.now().strftime("%Y-%m-%d"), str(member_mention), str(in_house), str(recruit)]]
            }
            # tworzenie zapytania
            service = build('sheets', 'v4', credentials=self.credentials, discoveryServiceUrl=self.DISCOVERY_SERVICE_URL)
            service.spreadsheets().values().update( spreadsheetId=self.spreadsheet_id, range=range_name, valueInputOption='RAW', body=body).execute()
            await self.create_embed(1, player_name, in_house, recruit, comment, member_mention)
        except HttpError as error:
            print(f'Coś poszło nie tak przy wpisywaniu do excela gracza {player_name}: {error}') # dodać kanał z logami
            await self.create_embed(0, player_name)

    async def del_msg(self, ctx):
        async for message in ctx.channel.history(limit=1):
            await message.delete()

    async def del_player_to_excel(self, player_name, comment):
        try:
            values = self.get_values(self.spreadsheet_id, self.player_sheet)
            row_num = 0
            data = []
            player_found = False
          
            for v in values[0][0]:
              if v.lower() == str(player_name).lower():
                player_found = True
                break
              row_num += 1
            if player_found:
              for v in values[0]:
                try:
                  data.append(v[row_num])
                except:
                  data.append(" ")
              row_number_to_delete = row_num+1
              values = self.get_values(self.spreadsheet_id, self.archives_sheet)
              row_num = len(values[0][0]) + 1
                
              # wartość do wpisania
              range_name = f'{self.archives_sheet}!{chr(ord("A"))}{row_num}:{chr(ord("N"))}{row_num}'
              body = {'values': [data]}
              # tworzenie zapytania
              service = build('sheets', 'v4', credentials=self.credentials, discoveryServiceUrl=self.DISCOVERY_SERVICE_URL)
              service.spreadsheets().values().update( spreadsheetId=self.spreadsheet_id, range=range_name, valueInputOption='RAW', body=body).execute()
              await self.delete_row(row_number_to_delete)
              await self.create_embed(2, player_name, comment=comment)
            else:
              print("nie znaleziono gracza!!!")
              await self.create_embed(3, player_name)

        except HttpError as error:
            print(f'Coś poszło nie tak przy przenoszeniu do archiwum gracza {player_name}: {error}')
            await self.create_embed(0, player_name)

    def get_values(self, spreadsheet_id, sheet):
      result = self.service.spreadsheets().values().batchGet(spreadsheetId=spreadsheet_id, ranges=sheet, majorDimension='COLUMNS').execute()
      values = []
      for res in result.get('valueRanges'):
          values.append(res.get('values', []))
      return values

    async def delete_row(self, row_num):
      requests = [
          {
              "deleteDimension": {
                  "range": {
                      "sheetId": self.player_sheet_id,
                      "dimension": "ROWS",
                      "startIndex": row_num - 1,
                      "endIndex": row_num
                  }
              }
          }
      ]
      body = {"requests": requests}
      self.service.spreadsheets().batchUpdate(spreadsheetId=self.spreadsheet_id, body=body).execute()

    async def create_embed(self, error, player_name, in_house=None, recruit=None, comment=None, member_mention=None):
      ping = ""
      if error == 1:
        embed = discord.Embed(
          title=f'Gracz: {player_name}, DC: {member_mention}',
          color=discord.Color.blue()
        )
        embed.add_field(name="Jest w rodzie?", value=in_house, inline=True)
        embed.add_field(name="Czy przeszedł rekrutacje?", value=recruit, inline=True)
        embed.add_field(name="Komentarz:", value=comment, inline=False)
      elif error == 2:
        embed = discord.Embed(
          title=f'Gracz: {player_name}',
          description='Został pomyślnie usunięty',
          color=discord.Color.blue()
        )
        embed.add_field(name="Komentarz:", value=comment, inline=False)
      elif error == 3:
        ping = self.interaction.user.mention
        embed = discord.Embed(
          title=f'Gracz: {player_name}',
          description='Nie został znaleziony',
          color=discord.Color.blue()
        )
      elif error == 4:
        ping = self.interaction.user.mention
        embed = discord.Embed(
          title=f'Gracz: {player_name}',
          description='Gracz o takim samym nicku już istnieje',
          color=discord.Color.blue()
        )
      else:
        ping = self.interaction.user.mention
        embed = discord.Embed(
          title=f'Gracz {player_name}',
          description='Error, wyślij jeszcze raz, jeśli nie pomaga zgłoś to do zarządu.',
          color=discord.Color.blue()
        )
      embed.set_author(name=self.interaction.user.global_name, icon_url=self.interaction.user.avatar)

      await self.log_channel.send(content = ping,embed=embed)
  
    async def reset_list_TW(self, lineup_sheet):
      values = self.get_values(self.spreadsheet_TW_id, lineup_sheet)
      col_numbers = [2, 3, 7, 9, 11, 13, 15]
      for col_num in col_numbers:
        value = values[0][col_num]
        row_num = len(value)

        # wartość do wpisania
        range_name = f'{lineup_sheet}!{chr(ord("A")+col_num)}5:{chr(ord("A")+col_num)}'
        body = {
          'values': [["" for _ in range(1)] for _ in range(row_num - 4)]
        }
        # tworzenie zapytania
        service = build('sheets', 'v4', credentials=self.credentials, discoveryServiceUrl=self.DISCOVERY_SERVICE_URL)
        service.spreadsheets().values().update( spreadsheetId=self.spreadsheet_TW_id, range=range_name, valueInputOption='RAW', body=body).execute()

    def get_name_sheet(self):
      spreadsheet = self.service.spreadsheets().get(spreadsheetId=self.spreadsheet_TW_id).execute()
      temp = []
      arkusze = spreadsheet['sheets']
      name_sheets = [arkusz['properties']['title'] for arkusz in arkusze]
      for name_sheet in name_sheets:
        if "Lineup" in name_sheet:
          temp.append(discord.SelectOption(label=name_sheet, value=name_sheet))
      return temp