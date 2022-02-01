from aiohttp import ClientSession
import discord
from discord.ext import commands

class Place():
  def __init__(self):
    self.Description = ""
    self.ID = self.North = self.East = self.South = self.West = self.Up = self.Down = 0

class Character():
  def __init__(self):
    self.Name = self.Description = ""
    self.ID = self.CurrentLocation = 0

class Item():
  def __init__(self):
    self.ID = self.Location = 0
    self.Description = self.Status = self.Name = self.Commands = self.Results = ""
# def Main():
#     Items = []
#     Characters = []
#     Places = []
#     Filename = input("Enter filename> ") + ".gme"
#     print()
#     GameLoaded, Characters, Items, Places = LoadGame(Filename, Characters, Items, Places)
#     if GameLoaded:
#         PlayGame(Characters, Items, Places)
#     else:
#         print("Unable to load game.")
#         input()

class maze(commands.Cog):
    def __init__(self,client):
        self.client = client

def setup(client):
    client.add_cog(maze(client))

def main():
    print(__name__)

main()