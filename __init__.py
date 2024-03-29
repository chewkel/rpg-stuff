from io import BytesIO
from tkinter import font
import discord
from discord.colour import Color
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions
import random
from discord import Member
# from keep_alive import keep_alive
import os
import os.path,time
from datetime import datetime
import time
import threading
from random import choice
from copy import deepcopy
from dataIO import fileIO
import asyncio
import pickle
import sys
from PIL import Image, ImageDraw, ImageFont
from easy_pil import *
import pytz

config_location = fileIO("config/config.json", "load")
Shards = config_location["Shards"]
Prefix = config_location["Prefix"]

client = commands.AutoShardedBot(shard_count = Shards, command_prefix=Prefix)

@client.event
async def on_command(command):
	info = fileIO("config/config.json", "load")
	info["Commands_used"] = info["Commands_used"] + 1
	fileIO("config/config.json", "save", info)

VS = 1.0

@client.event
async def on_ready():
  await client.change_presence(status=discord.Status.online, activity=discord.Game('Under construction'))
  print('Bot is online')#Shows bot is ready to go
  
@client.command(aliases=["r"])
@commands.is_owner()
async def restart(ctx):
  embed=discord.Embed(title=":white_check_mark:",desc="Successfully Restarted")
  await ctx.send(embed=embed)
  os.system("restart")
  os.execv(sys.executable, ['python'] + sys.argv)
  await ctx.send("succesfully restarted")

@client.command()
async def info(ctx):
    info = fileIO("config/config.json", "load")
    em = discord.Embed(title="My info:", type="rich", description="1) Prefix: {}\n2) Name: {}\n3) User ID: {}\n4) Version: {}\n5) Shards: {}\n6) Total commands used: {}".format(Prefix, client.user.name, client.user.id, VS, Shards, info["Commands_used"]), color=discord.Color.blue())
    em.set_thumbnail(url=client.user.avatar_url)
    await ctx.send(embed=em)

@commands.guild_only()
@commands.is_owner()
@client.command()
async def load(ctx,extension):
    client.load_extension(f'cogs.{extension}')

@commands.guild_only()
@commands.is_owner()
@client.command()
async def unload(ctx,extension):
    client.unload_extension(f'cogs.{extension}')

@commands.guild_only()
@commands.is_owner()
@client.command()
async def reload(ctx,extension):
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')


#Start comamnd to create a user profile for the rpg game
@client.command()
async def start(ctx):
    author = ctx.author
    message = ctx.message
    await _create_user(author)
    info = fileIO("players/{}/info.json".format(author.id), "load")
    if info["race"] and info["class"] == "None":
        await ctx.send("<@{}> Stats created.\n\nWelcome to Chewy RPG!\nMay i ask what race you are?\n`Choose one of the following`\nOrc\nHuman\nTenti".format(author.id))
        def pred(m):
            return m.author == message.author and m.channel == message.channel
        answer1 = await client.wait_for("message", check=pred)
        values = ["orc", "Orc", "human", "Human", "tenti", "Tenti", "{}start".format(Prefix)]
        if str(answer1.content) in values:
            if answer1.content == "{}start".format(Prefix):
                return
            elif answer1.content == "orc" or answer1.content == "Orc":
                info["race"] = "Orc"
                fileIO("players/{}/info.json".format(author.id), "save", info)
                await _pick_class(ctx)
            elif answer1.content == "human" or answer1.content == "Human":
                info["race"] = "Human"
                fileIO("players/{}/info.json".format(author.id), "save", info)
                await _pick_class(ctx)
            elif answer1.content == "tenti" or answer1.content == "Tenti":
                info["race"] = "Tenti"
                fileIO("players/{}/info.json".format(author.id), "save", info)
                await _pick_class(ctx)
        else:
            await ctx.send("Next time choose one of the options.")
    else:
        await ctx.send("You're already setup.")
#fight command
@client.command()
async def fight(ctx):
    author = ctx.author
    message = ctx.message
    await _create_user(author)
    info = fileIO("players/{}/info.json".format(author.id), "load")
    einfo = fileIO("core/enemies/enemies.json", "load")
    if info["race"] and info["class"] == "None":
        await ctx.send("{} please start your character using {}start".format(author.id, Prefix))
        return
    if info["health"] <= 0:
        await ctx.send("<@{}> You cannot fight with 0 HP.".format(author.id))
        return
    if info["selected_enemy"] == "None":
        elocation = info["location"]
        if elocation == "Golden Temple":
            monster = ["Rachi", "Debin", "Oofer"]
        if elocation == "Saker Keep":
            monster = ["Draugr", "Stalker", "Souleater"]
        if elocation == "The Forest":
            monster = ["Wolf", "Goblin", "Zombie"]
        if elocation == "Aquaris":
            monster = ["fish"]
        monsterz = random.choice((monster))
        enemy = monsterz
        monster_hp_min = einfo["locations"][elocation]["enemies"][enemy]["min_health"]
        monster_hp_max = einfo["locations"][elocation]["enemies"][enemy]["max_health"]
        ehp_min = monster_hp_min
        ehp_max = monster_hp_max
        enemy_hp = random.randint(ehp_min, ehp_max)
        await ctx.send("You wonder around {} and find a {}, would you like to fight it?\n**Y** or **N**".format(info["location"], enemy))
        def pred(m):
            return m.author == message.author and m.channel == message.channel
        answer1 = await client.wait_for("message", check=pred)
        values = ["y", "Y", "yes", "Yes", "n", "N", "no", "No", "{}fight".format(Prefix)]
        if str(answer1.content) in values:
            if answer1.content == "{}fight".format(Prefix):
                return
            if answer1.content == "y" or answer1.content == "Y" or answer1.content == "yes" or answer1.content == "Yes":
                #need to insert the enemy side story.
                info["selected_enemy"] = enemy
                info["enemyhp"] = enemy_hp
                fileIO("players/{}/info.json".format(author.id), "save", info)
                await ctx.send("You start fighting a {}...\nPlease use `{}fight` to start fighting it.".format(enemy, Prefix))
            elif answer1.content == "n" or answer1.content == "N" or answer1.content == "no" or answer1.content == "No":
                await ctx.send("Ok then.")
        else:
            await ctx.send("Please choose one of the options next time.")
    else:
        #Define our user stats here.
        user_location = info["location"]
        user_enemy = info["selected_enemy"]
        user_enemy_hp = info["enemyhp"]
        user_skills = info["skills_learned"]
        user_wep = info["equip"]
        user_armor = info["wearing"]
        user_hp = info["health"]
        user_name = info["name"]
        #Define wep dmg.
        ainfo = fileIO("core/enemies/weapons.json", "load")
        user_wep_define = ainfo[user_wep]
        min_dmg = ainfo[user_wep]["min_dmg"]
        max_dmg = ainfo[user_wep]["max_dmg"]
        user_dmg = random.randint(min_dmg, max_dmg)
        #Define enemy stats.
        enemy_define = info["selected_enemy"]
        enemy_define_hp = info["enemyhp"]
        enemy_min_dmg = einfo["locations"][user_location]["enemies"][user_enemy]["min_dmg"]
        enemy_max_dmg = einfo["locations"][user_location]["enemies"][user_enemy]["max_dmg"]
        enemy_dmg = random.randint(enemy_min_dmg, enemy_max_dmg)
        enemy_min_gold = einfo["locations"][user_location]["enemies"][user_enemy]["min_drop"]
        enemy_max_gold = einfo["locations"][user_location]["enemies"][user_enemy]["max_drop"]
        enemy_gold = random.randint(enemy_min_gold, enemy_max_gold)
        enemy_xp_min = einfo["locations"][user_location]["enemies"][user_enemy]["min_xp"]
        enemy_xp_max = einfo["locations"][user_location]["enemies"][user_enemy]["max_xp"]
        enemy_xp = random.randint(enemy_xp_min, enemy_xp_max)

        options = []
        options_show = []

        options.append("{}gight".format(Prefix))
        if "Stab" in info["skills_learned"]:
            options.append("Stab")
            options.append("stab")
            options_show.append("Stab")
        if "Swing" in info["skills_learned"]:
            options.append("Swing")
            options.append("swing")
            options_show.append("Swing")
        if "Cast" in info["skills_learned"]:
            options.append("Cast")
            options.append("cast")
            options_show.append("Cast")
        if "Shoot" in info["skills_learned"]:
            options.append("Shoot")
            options.append("shoot")
            options_show.append("Shoot")

        await ctx.send("<@{}> what skill would you like to use?\n\n`Choose one`\n{}".format(author.id, "\n".join(options_show)))
        def pred(m):
            return m.author == message.author and m.channel == message.channel
        answer1 = await client.wait_for("message", check=pred)
        if str(answer1.content) in options:
            if answer1.content == "Stab" or answer1.content == "stab":
                move = "Stab"
            elif answer1.content == "Swing" or answer1.content == "swing":
                move = "Swing"
            elif answer1.content == "Cast" or answer1.content == "cast":
                move = "Cast"
            elif answer1.content == "Shoot" or answer1.content == "shoot":
                move = "Shoot"
            #Lootbag# 10% chance to obtain one from an enemy.
            lootbag = random.randint(1, 10)
            enemy_hp = user_enemy_hp
            enemy_hp_after = int(enemy_hp) - int(user_dmg)
            user_hp_after = int(user_hp) - int(enemy_dmg)
            gold_lost = random.randint(0, 250)
            await ctx.send("```diff\n- {} has {} HP\n+ {} has {} HP\n\n- {} hits {} for {} dmg.\n+ {} uses {} and hits for {} dmg.\n\n- {} has {} hp left\n+ {} has {} hp left.```".format(user_enemy, user_enemy_hp, user_name, user_hp, user_enemy, user_name, enemy_dmg, user_name, move, user_dmg, user_enemy, enemy_hp_after, user_name, user_hp_after))
            user_hp = user_hp_after
            enemy_hp = enemy_hp_after
            if enemy_hp <= 0 and user_hp <= 0:
                await ctx.send("```diff\n- {} has killed you.\n- You lost {} gold```".format(user_enemy, gold_lost))
                info["gold"] = info["gold"] - gold_lost
                if info["gold"] < 0:
                    info["gold"] = 0
                info["health"] = 0
                info["selected_enemy"] = "None"
                info["enemieskilled"] = ["enemieskilled"] + 1
                info["deaths"] = info["deaths"] + 1
                fileIO("players/{}/info.json".format(author.id), "save", info)
            elif user_hp <= 0:
                await ctx.send("```diff\n- {} has killed you\n- You lost {} gold```".format(user_enemy, gold_lost))
                info["gold"] = info["gold"] - gold_lost
                if info["gold"] < 0:
                    info["gold"] = 0
                info["deaths"] = info["deaths"] + 1
                fileIO("players/{}/info.json".format(author.id), "save", info)
            elif enemy_hp <= 0:
                await ctx.send("```diff\n+ You killed {}\nYou gained {} gold.```".format(user_enemy, enemy_gold))
                info["selected_enemy"] = "None"
                info["gold"] = info["gold"] + enemy_gold
                info ["exp"] = info["exp"] + enemy_xp
                if lootbag == 6:
                    await ctx.send("```diff\n+ {} obtained a lootbag!```".format(user_name))
                    info["lootbag"] = info["lootbag"] + 1
                    fileIO("players/{}/info.json".format(author.id), "save", info)
                info["enemieskilled"] = info["enemieskilled"] + 1
                fileIO("players/{}/info.json".format(author.id), "save", info)
                await _check_levelup(ctx)
            else:
                info["enemyhp"] = enemy_hp_after
                info["health"] = user_hp_after
                fileIO("players/{}/info.json".format(author.id), "save", info)
        else:
            await ctx.send("Please choose one of the skills next time!")
# shows your user's inventory
@client.command()
async def inv(ctx):
    author = ctx.author
    await _create_user(author)
    message = ctx.message
    info = fileIO("players/{}/info.json".format(author.id), "load")
    if info["race"] and info["class"] == "None":
        await ctx.send("Please start your character using `{}start`".format(Prefix))
        return
    em = discord.Embed(description="```diff\n!======== [{}'s Inventory] ========!\n\n!==== [Supplies] ====!\n+ Gold : {}\n+ Wood : {}\n+ Stone : {}\n+ Metal : {}\n\n!===== [Items] =====!\n+ Keys : {}\n+ Loot Bags : {}\n+ Minor HP Potions : {}\n+ {}```".format(info["name"], info["gold"], info["wood"], info["stone"], info["metal"], info["keys"], info["lootbag"], info["hp_potions"], "\n+ ".join(info["inventory"])), color=discord.Color.blue())
    await ctx.send(embed=em)
#shows your user information
@client.command()
async def stats(ctx):
    author = ctx.author
    await _create_user(author)
    info = fileIO("players/{}/info.json".format(author.id), "load")
    if info["race"] and info["class"] == "None":
        await ctx.send("Please start your character using `{}start`".format(Prefix))
        return
    maxexp = 100 * info["lvl"]
    em = discord.Embed(description="```diff\n!======== [{}'s Stats] ========!\n+ Name : {}\n+ Title : {}\n+ Race : {}\n+ Class : {}\n\n+ Level : {} | Exp : ({}/{})\n+ Health : ({}/100)\n+ Stamina : {}\n+ Mana : {}\n\n!===== [Equipment] =====!\n+ Weapon : {}\n+ Wearing : {}\n\n+ Killed : {} Enemies\n+ Died : {} Times```".format(info["name"], info["name"], info["title"], info["race"], info["class"], info["lvl"], info["exp"], maxexp, info["health"], info["stamina"], info["mana"], info["equip"], info["wearing"], info["enemieskilled"], info["deaths"]), color=discord.Color.blue())
    await ctx.send(embed=em)

@client.command()
async def equip(ctx):
    author = ctx.author
    await _create_user(author)
    message = ctx.message
    info = fileIO("players/{}/info.json".format(author.id), "load")
    if info["race"] and info["class"] == "None":
        await ctx.send("Please start your character using `{}start`".format(Prefix))
        return
    choices = []
    inv_list = [i for i in info["inventory"]]
    if len(inv_list) == 0:
        em = discord.Embed(description="```diff\n- You don't have anything else to equip!```", color=discord.Color.red())
        await ctx.send(embed=em)
    else:
        choices.append(inv_list)
        em = discord.Embed(description="```diff\n+ What would you like to equip?\n- Note this is Uppercase and Lowercase sensitive.\n{}```".format("\n".join(inv_list)), color=discord.Color.blue())
        await ctx.send(embed=em)
        def pred(m):
            return m.author == message.author and m.channel == message.channel
        answer1 = await client.wait_for("message", check=pred)
        if answer1.content in inv_list:
            em = discord.Embed(description="```diff\n+ You equip the {}!```".format(answer1.content), color=discord.Color.blue())
            await ctx.send(embed=em)
            info["inventory"].append(info["equip"])
            info["equip"] = "None"
            info["equip"] = answer1.content
            info["inventory"].remove(answer1.content)
            fileIO("players/{}/info.json".format(author.id), "save", info)
        else:
            ctx.send("<@{}> please choose a valid item next time.".format(author.id))

@client.command()
async def lootbag(ctx):
    channel = ctx.channel
    author = ctx.author
    await _create_user(author)
    info = fileIO("players/{}/info.json".format(author.id), "load")
    if info["race"] and info["class"] == "None":
        await ctx.send("Please start your character using `{}start`".format(Prefix))
        return
    if info["lootbag"] == 0:
        em = discord.Embed(description="```diff\n- You don't have any Lootbags!```", color=discord.Color.blue())
        await ctx.send(embed=em)
        return
    else:
        em = discord.Embed(description="```diff\n+ {} Starts opening a Lootbag. . .```".format(info["name"]), color=discord.Color.blue())
        await ctx.send(embed=em)
        await asyncio.sleep(5)
        chance = random.randint(1, 3)
        goldmul = random.randint(10, 30)
        goldgain = goldmul * info["lvl"]
        if chance == 3:
            em = discord.Embed(description="```diff\n+ The Lootbag obtained {} Gold!```".format(goldgain), color=discord.Color.blue())
            await ctx.send(embed=em)
            info["gold"] = info["gold"] + goldgain
            info["lootbag"] = info["lootbag"] - 1
            fileIO("players/{}/info.json".format(author.id), "save", info)
        else:
            em = discord.Embed(description="```diff\n- The Lootbag didn't contain anything!```", color=discord.Color.blue())
            await ctx.send(embed=em)
            info["lootbag"] = info["lootbag"] - 1
            fileIO("players/{}/info.json".format(author.id), "save", info)

@client.command()
async def travel(ctx):
    channel = ctx.channel
    author = ctx.author
    message = ctx.message
    await _create_user(author)
    info = fileIO("players/{}/info.json".format(author.id), "load")
    if info["race"] and info["class"] == "None":
        await ctx.send("Please start your character using `{}start`".format(Prefix))
        return
    options = []
    options2 = []
    travel_location = []

    if info["lvl"] > 0:
        options.append("(0) Golden Temple")
        options2.append("0")

        options.append("(1) Saker Keep")
        options2.append("1")

    if info["lvl"] >= 10:
        options.append("(2) The Forest")
        options2.append("2")
    
    if info["lvl"] >= 20:
        options.append("(3) Aquaris")
        options2.append("3")

    em = discord.Embed(description="<@{}>\n```diff\n+ Where would you like to travel?\n- Type a location number in the chat.\n+ {}```".format(author.id, "\n+ ".join(options)), color=discord.Color.blue())
    await ctx.send(embed=em)

    def pred(m):
        return m.author == message.author and m.channel == message.channel
    answer1 = await client.wait_for("message", check=pred)

    if answer1.content in options2:
        if answer1.content == "0":
            if info["location"] == "Golden Temple":
                em = discord.Embed(description="<@{}>\n```diff\n- You're already at {}!```".format(author.id, info["location"]), color=discord.Color.red())
                await ctx.send(embed=em)
                return
            else:
                location_name = "Golden Temple"
                info["location"] = "Golden Temple"

        elif answer1.content == "1":
            if info["location"] == "Saker Keep":
                em = discord.Embed(description="<@{}>\n```diff\n- You're already at {}!```".format(author.id, info["location"]), color=discord.Color.red())
                await ctx.send(embed=em)
                return
            else:
                location_name = "Saker Keep"
                info["location"] = "Saker Keep"

        elif answer1.content == "2":
            if info["location"] == "The Forest":
                em = discord.Embed(description="<@{}>\n```diff\n- You're already at {}!```".format(author.id, info["location"]), color=discord.Color.red())
                await ctx.send(embed=em)
                return
            else:
                location_name = "The Forest"
                info["location"] = "The Forest"
                
        elif answer1.content == "3":
            if info["location"] == "Aquaris":
                em = discord.Embed(description="<@{}?\n```diff\n- You're already at {}!```".format(author.id, info["location"]), color=discord.Color.red())
                await ctx.send(embed = em)
                return
            else:
                location_name = "Aquaris"
                info["location"] = "Aquaris"

        em = discord.Embed(description="<@{}>\n```diff\n+ Traveling to {}...```".format(author.id, location_name), color=discord.Color.red())
        await ctx.send(embed=em)
        await asyncio.sleep(3)
        info["location"] = location_name
        fileIO("players/{}/info.json".format(author.id), "save", info)
        em = discord.Embed(description="<@{}>\n```diff\n+ You have arrived at {}```".format(author.id, location_name), color=discord.Color.red())
        await ctx.send(embed=em)
    else:
        await ctx.send("Please choose a correct location next time.")
#buy items 
@client.command()
async def buy(ctx):
    author = ctx.author
    await _create_user(author)
    message = ctx.message
    info = fileIO("players/{}/info.json".format(author.id), "load")
    em = discord.Embed(description="```diff\n+ What category would you like to buy from?\n- Items\n- Potions```", color=discord.Color.blue())
    await ctx.send(embed=em)
    options = ["potions", "Potions", "items", "Items", "{}buy".format(Prefix)]
    def pred(m):
        return m.author == message.author and m.channel == message.channel
    answer1 = await client.wait_for("message", check=pred)
    if answer1.content in options:
        if answer1.content == "{}buy".format(Prefix):
            return
        elif answer1.content == "potions" or answer1.content == "Potions":
            em = discord.Embed(description="```diff\n+ How many would you like to buy?```", color=discord.Color.blue())
            await ctx.send(embed=em)
            def pred2(m):
                return m.author == message.author and m.channel == message.channel
            answer2 = await client.wait_for("message", check=pred2)
            try:
                value = int(answer2.content) * 30
                if info["gold"] < value:
                    em = discord.Embed(description="```diff\n- {}, you don't have enough gold for {} potion(s)```".format(info["name"], answer2.content), color=discord.Color.red())
                    await ctx.send(embed=em)
                else:
                    info["gold"] = info["gold"] - value
                    info["hp_potions"] = info["hp_potions"] + int(answer2.content)
                    fileIO("players/{}/info.json".format(author.id), "save", info)
                    em = discord.Embed(description="```diff\n+ {}, you bought {} potion(s) for {} gold!```".format(info["name"], answer2.content, value), color=discord.Color.blue())
                    await ctx.send(embed=em)
            except:
                em = discord.Embed(description="```diff\n- {}, please put a correct number value next time.```".format(info["name"]), color=discord.Color.red())
                await ctx.send(embed=em)
        elif answer1.content == "Items" or answer1.content == "items":
            if info["class"] == "Mage":
                items = ["sprine staff", "Sprine staff", "{}buy".format(Prefix)]
                em = discord.Embed(description="**Items for {} class:**\nItem - Cost\n```diff\n- Sprine Staff | 1,000 gold.```\n```diff\n+ What would you like to buy?```".format(info["class"], color=discord.Color.blue()))
                await ctx.send(embed=em)
                def pred3(m):
                    return m.author == message.author and m.channel == message.channel
                answer3 = await client.wait_for("message", check=pred3)
                if answer3.content == "{}buy".format(Prefix):
                    return
                elif answer3.content == "Sprine staff" or answer3.content == "sprine staff":
                    if info["gold"] < 1000:
                        em = discord.Embed(description="```diff\n- {}, you don't have enough gold for the Sprine Staff.```".format(info["name"]), color=discord.Color.red())
                        await ctx.send(embed=em)
                    else:
                        info["gold"] = info["gold"] - 1000
                        info["inventory"].append("Sprine Staff")
                        fileIO("players/{}/info.json".format(author.id), "save", info)
                        em = discord.Embed(description="```diff\n+ {}, you bought the Sprine Staff!```".format(info["name"]), color=discord.Color.blue())
                        await ctx.send(embed=em)
                else:
                    em = discord.Embed(description="```diff\n- {}, please state a correct item next time.```".format(info["name"]), color=discord.Color.red())
                    await ctx.send(embed=em)
            elif info["class"] == "Paladin":
                items = ["sprine sword", "Sprine sword", "{}buy".format(Prefix)]
                em = discord.Embed(description="**Items for {} class:**\nItem - Cost\n```diff\n- Sprine Sword | 1,000 gold.```\n```diff\n+ What would you like to buy?```".format(info["class"], color=discord.Color.blue()))
                await ctx.send(embed=em)
                def pred3(m):
                    return m.author == message.author and m.channel == message.channel
                answer3 = await client.wait_for("message", check=pred3)
                if answer3.content == "{}buy".format(Prefix):
                    return
                elif answer3.content == "Sprine sword" or answer3.content == "sprine sword":
                    if info["gold"] < 1000:
                        em = discord.Embed(description="```diff\n- {}, you don't have enough gold for the Sprine Sword.```".format(info["name"]), color=discord.Color.red())
                        await ctx.send(embed=em)
                    else:
                        info["gold"] = info["gold"] - 1000
                        info["inventory"].append("Sprine Sword")
                        fileIO("players/{}/info.json".format(author.id), "save", info)
                        em = discord.Embed(description="```diff\n+ {}, you bought the Sprine Sword!```".format(info["name"]), color=discord.Color.blue())
                        await ctx.send(embed=em)
                else:
                    em = discord.Embed(description="```diff\n- {}, please state a correct item next time.```".format(info["name"]), color=discord.Color.red())
                    await ctx.send(embed=em)
            elif info["class"] == "Thief":
                items = ["sprine dagger", "Sprine dagger", "{}buy".format(Prefix)]
                em = discord.Embed(description="**Items for {} class:**\nItem - Cost\n```diff\n- Sprine Dagger | 1,000 gold.```\n```diff\n+ What would you like to buy?```".format(info["class"], color=discord.Color.blue()))
                await ctx.send(embed=em)
                def pred3(m):
                    return m.author == message.author and m.channel == message.channel
                answer3 = await client.wait_for("message", check=pred3)
                if answer3.content == "{}buy".format(Prefix):
                    return
                elif answer3.content == "Sprine dagger" or answer3.content == "sprine dagger":
                    if info["gold"] < 1000:
                        em = discord.Embed(description="```diff\n- {}, you don't have enough gold for the Sprine Dagger.```".format(info["name"]), color=discord.Color.red())
                        await ctx.send(embed=em)
                    else:
                        info["gold"] = info["gold"] - 1000
                        info["inventory"].append("Sprine Dagger")
                        fileIO("players/{}/info.json".format(author.id), "save", info)
                        em = discord.Embed(description="```diff\n+ {}, you bought the Sprine Dagger!```".format(info["name"]), color=discord.Color.blue())
                        await ctx.send(embed=em)
                else:
                    em = discord.Embed(description="```diff\n- {}, please state a correct item next time.```".format(info["name"]), color=discord.Color.red())
                    await ctx.send(embed=em)
            elif info["class"] == "Archer":
                items = ["sprine bow", "Sprine bow", "{}buy".format(Prefix)]
                em = discord.Embed(description="**Items for {} class:**\nItem - Cost\n```diff\n- Sprine bow | 1,000 gold.```\n```diff\n+ What would you like to buy?```".format(info["class"], color=discord.Color.blue()))
                await ctx.send(embed=em)
                def pred3(m):
                    return m.author == message.author and m.channel == message.channel
                answer3 = await client.wait_for("message", check=pred3)
                if answer3.content == "{}buy".format(Prefix):
                    return
                elif answer3.content == "Sprine bow" or answer3.content == "sprine bow":
                    if info["gold"] < 1000:
                        em = discord.Embed(description="```diff\n- {}, you don't have enough gold for the Sprine Bow.```".format(info["name"]), color=discord.Color.red())
                        await ctx.send(embed=em)
                    else:
                        info["gold"] = info["gold"] - 1000
                        info["inventory"].append("Sprine Bow")
                        fileIO("players/{}/info.json".format(author.id), "save", info)
                        em = discord.Embed(description="```diff\n+ {}, you bought the Sprine Bow!```".format(info["name"]), color=discord.Color.blue())
                        await ctx.send(embed=em)
                else:
                    em = discord.Embed(description="```diff\n- {}, please state a correct item next time.```".format(info["name"]), color=discord.Color.red())
                    await ctx.send(embed=em)
        else:
            em = discord.Embed(description="```diff\n- {}, please put a correct value next time.```".format(info["name"]), color=discord.Color.red())
            await ctx.send(embed=em)
    else:
        em = discord.Embed(description="```diff\n- {}, please put a correct value next time.```".format(info["name"]), color=discord.Color.red())
        await ctx.send(embed=em)
#heal by drinking health potions
@client.command()
async def heal(ctx):
    author = ctx.author
    await _create_user(author)
    info = fileIO("players/{}/info.json".format(author.id), "load")
    if info["race"] and info["class"] == "None":
        await ctx.send("Please start your character using `{}start`".format(Prefix))
        return
    if info["hp_potions"] > 0:
        gain = random.randint(90, 100)
        info["health"] = info["health"] + gain
        if info["health"] > 100:
            info["health"] = 100
        info["hp_potions"] = info["hp_potions"] - 1
        fileIO("players/{}/info.json".format(author.id), "save", info)
        em = discord.Embed(description="```diff\n- You use a Minor Health Potion\n+ {} HP```".format(gain), color=discord.Color.blue())
        await ctx.send(embed=em)
    else:
        em = discord.Embed(description="```diff\n- You don't have any health potions!```", color=discord.Color.red())
        await ctx.send(embed=em)
#get daily amount of gold
@client.command()
async def daily(ctx):
    channel = ctx.channel
    author = ctx.author
    await _create_user(author)
    goldget = random.randint(500, 1000)
    info = fileIO("players/{}/info.json".format(author.id), "load")
    if info["race"] and info["class"] == "None":
        await ctx.send("Please start your character using `{}start`".format(Prefix))
        return
    curr_time = time.time()
    delta = float(curr_time) - float(info["daily_block"])

    if delta >= 86400.0 and delta>0:
        if info["class"] == "None" and info["race"] == "None":
            await ctx.send("Please start your player using `{}start`".format(Prefix))
            return
        info["gold"] += goldget
        info["daily_block"] = curr_time
        fileIO("players/{}/info.json".format(author.id), "save", info)
        em = discord.Embed(description="```diff\n+ You recieved your daily gold!\n+ {}```".format(goldget), color=discord.Color.blue())
        await ctx.send(embed=em)
    else:
        seconds = 86400 - delta
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        em = discord.Embed(description="```diff\n- You can't claim your daily reward yet!\n\n- Time left:\n- {} Hours, {} Minutes, and {} Seconds```".format(int(h), int(m), int(s)), color=discord.Color.red())
        await ctx.send(embed=em)
#rest to gain some health back
@client.command()
async def rest(ctx):
    channel = ctx.channel
    author = ctx.author
    await _create_user(author)
    HPget = random.randint(10, 40)
    info = fileIO("players/{}/info.json".format(author.id), "load")
    if info["race"] and info["class"] == "None":
        await ctx.send("Please start your character using `{}start`".format(Prefix))
        return
    curr_time = time.time()
    delta = float(curr_time) - float(info["rest_block"])

    if delta >= 120.0 and delta>0:
        if info["class"] == "None" and info["race"] == "None":
            await ctx.send("Please start your player using `{}start`".format(Prefix))
            return
        info["health"] = info["health"] + HPget
        if info["health"] > 100:
            info["health"] = 100
        info["rest_block"] = curr_time
        fileIO("players/{}/info.json".format(author.id), "save", info)
        em = discord.Embed(description="```diff\n+ You gained {} HP for resting!```".format(HPget), color=discord.Color.blue())
        await ctx.send(embed=em)
    else:
        seconds = 120 - delta
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        em = discord.Embed(description="```diff\n- Your not tired!\n\n- Time left:\n- {} Hours, {} Minutes, and {} Seconds```".format(int(h), int(m), int(s)), color=discord.Color.red())
        await ctx.send(embed=em)

@client.command()
async def mine(ctx):
    channel = ctx.channel
    author = ctx.author
    await _create_user(author)
    mined_metal = random.randint(1, 10)
    mined_rock = random.randint(1, 10)
    info = fileIO("players/{}/info.json".format(author.id), "load")
    if info["race"] and info["class"] == "None":
        await ctx.send("Please start your character using `{}start`".format(Prefix))
        return
    curr_time = time.time()
    delta = float(curr_time) - float(info["mine_block"])

    if delta >= 600.0 and delta>0:
        if info["class"] == "None" and info["race"] == "None":
            await ctx.send("Please start your player using `{}start`".format(Prefix))
            return
        info["metal"] = info["metal"] + mined_metal
        info["stone"] = info["stone"] + mined_rock
        info["mine_block"] = curr_time
        fileIO("players/{}/info.json".format(author.id), "save", info)
        em = discord.Embed(description="```diff\n+ You mined a Rock!\n+ {} Metal\n+ {} Stone```".format(mined_metal, mined_rock), color=discord.Color.blue())
        await ctx.send(embed=em)
    else:
        seconds = 600 - delta
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        em = discord.Embed(description="```diff\n- You cannot mine yet!\n\n- Time left:\n- {} Hours, {} Minutes, and {} Seconds```".format(int(h), int(m), int(s)), color=discord.Color.red())
        await ctx.send(embed=em)

@client.command()
async def update(ctx):
    await _check_levelup(ctx)

@client.command()
async def chop(ctx):
    channel = ctx.channel
    author = ctx.author
    await _create_user(author)
    chopped = random.randint(1, 10)
    info = fileIO("players/{}/info.json".format(author.id), "load")
    if info["race"] and info["class"] == "None":
        await ctx.send("Please start your character using `{}start`".format(Prefix))
        return
    curr_time = time.time()
    delta = float(curr_time) - float(info["chop_block"])

    if delta >= 600.0 and delta>0:
        if info["class"] == "None" and info["race"] == "None":
            await ctx.send("Please start your player using `{}start`".format(Prefix))
            return
        info["wood"] = info["wood"] + chopped
        info["chop_block"] = curr_time
        fileIO("players/{}/info.json".format(author.id), "save", info)
        em = discord.Embed(description="```diff\n+ You chopped a Tree!\n+ {} Wood```".format(chopped), color=discord.Color.blue())
        await ctx.send(embed=em)
    else:
        seconds = 600 - delta
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        em = discord.Embed(description="```diff\n- You cannot chop yet!\n\n- Time left:\n- {} Hours, {} Minutes, and {} Seconds```".format(int(h), int(m), int(s)), color=discord.Color.red())
        await ctx.send(embed=em)

async def _check_levelup(ctx):
    author = ctx.author
    info = fileIO("players/{}/info.json".format(author.id), "load")
    xp = info["exp"]
    num = 100
    name = info["name"]
    lvl = info["lvl"]
    lvlexp = num * lvl
    if xp >= lvlexp:
        await ctx.send("```diff\n+ {} gained a level!```".format(name))
        info["lvl"] = info["lvl"] + 1
        fileIO("players/{}/info.json".format(author.id), "save", info)
        return await _check_levelup(ctx)
    else:
        pass
#function on what class you want to pick
async def _pick_class(ctx):
    author = ctx.author
    message = ctx.message
    info = fileIO("players/{}/info.json".format(author.id), "load")
    await ctx.send("<@{}> Great!\nMay i ask what Class you are?\n`Choose one of the following`\nArcher\nPaladin\nMage\nThief".format(author.id))
    def pred(m):
        return m.author == message.author and m.channel == message.channel
    answer2 = await client.wait_for("message", check=pred)
    values2 = ["archer", "Archer", "paladin", "Paladin", "mage", "Mage", "thief", "Thief", "{}start".format(Prefix)]
    if str(answer2.content) in values2:
        if answer2 == "{}start".format(Prefix):
            return
        elif answer2.content.lower() == "archer" or answer2.content == "Archer":
            info["class"] = "Archer"
            info["skills_learned"].append("Shoot")
            info["equip"] = "Simple Bow"
            fileIO("players/{}/info.json".format(author.id), "save", info)
            await ctx.send("All setup!")
            return
        elif answer2.content.lower() == "paladin" or answer2.content == "Paladin":
            info["class"] = "Paladin"
            info["skills_learned"].append("Swing")
            info["equip"] = "Simple Sword"
            fileIO("players/{}/info.json".format(author.id), "save", info)
            await ctx.send("All setup!")
            return
        elif answer2.content.lower() == "mage" or answer2.content == "Mage":
            info["class"] = "Mage"
            info["skills_learned"].append("Cast")
            info["equip"] = "Simple Staff"
            fileIO("players/{}/info.json".format(author.id), "save", info)
            await ctx.send("All setup!")
            return
        elif answer2.content.lower() == "thief" or answer2.content == "Thief":
            info["class"] = "Thief"
            info["skills_learned"].append("Stab")
            info["equip"] = "Simple Dagger"
            fileIO("players/{}/info.json".format(author.id), "save", info)
            await ctx.send("All setup!")
            return
    else:
        await ctx.send("Next time choose one of the options.")

async def _create_user(author):
    # await _create_user(author)
    if not os.path.exists("players/{}".format(author.id)):
        os.makedirs("players/{}".format(author.id))
        new_account = {
            "name": author.name,
            "race": "None",
            "class": "None",
            "health": 100,
            "enemyhp": 50,
            "enemylvl": 0,
            "lvl": 1,
            "gold": 0,
            "wood": 0,
            "metal": 0,
            "stone": 0,
            "enemieskilled": 0,
            "selected_enemy": "None",
            "deaths": 0,
            "exp": 0,
            "lootbag": 0,
            "wearing": "None",
            "defence": 0,
            "guild": "None",
            "inguild": False,
            "skills_learned": [],
            "inventory" : [],
            "equip": "None",
            "title": "None",
            "wincry": "None",
            "losecry": "None",
            "location": "Golden Temple",
            "roaming": "False",
            "pet": "None",
            "mana": 100,
            "stamina": 100,
            "craftable": [],
            "daily_block": 0,
            "rest_block": 0,
            "traveling_block": 0,
            "hp_potions": 0,
            "keys": 0,
            "mine_block": 0,
            "chop_block": 0,
            "in_dungeon": "False",
            "dungeon_enemy": "None",
            "duneon_enemy_hp": 0,
            "in_party": []
        }
        fileIO("players/{}/info.json".format(author.id), "save", new_account)
    info = fileIO("players/{}/info.json".format(author.id), "load")

@client.command()
async def location(ctx,user: discord.Member = None):
    if user == None:
        user = ctx.author
    info = fileIO("players/{}/info.json".format(user.id), "load")
    map = Image.open("map.png")
    asset = user.avatar_url_as(size = 64)
    
    data = BytesIO(await asset.read())
    pfp = Image.open(data)
    
    match info["location"]:
        case "Golden Temple":
            pfp = pfp.resize((120,120))
            map.paste(pfp, ((195,170)))
            map.save("profile.png")
            draw = ImageDraw.Draw((map))
            text = "You are here"
            draw.text((317,131), text,(0,0,0,))
            map.save("profile.png")
            await ctx.send(file = discord.File("profile.png"))
        case "Saker Keep":
            pfp = pfp.resize((120,120))
            map.paste(pfp, ((585,205)))
            map.save("profile.png")
            draw = ImageDraw.Draw((map))
            text = "You are here"
            draw.text((682,205), text,(0,0,0,))
            map.save("profile.png")
            await ctx.send(file = discord.File("profile.png"))
        case "The Forest":
            pfp = pfp.resize((120,120))
            map.paste(pfp, ((290,526)))
            map.save("profile.png")
            draw = ImageDraw.Draw((map))
            text = "You are here"
            draw.text((370,435), text,(0,0,0,))
            map.save("profile.png")
            await ctx.send(file = discord.File("profile.png"))
        case "Aquaris":
            pfp = pfp.resize((120,120))
            map.paste(pfp, ((618,516)))
            map.save("profile.png")
            draw = ImageDraw.Draw((map))
            text = "You are here"
            draw.text((706,450), text,(0,0,0,))
            map.save("profile.png")
            await ctx.send(file = discord.File("profile.png"))  

@client.command()
async def create_guild(ctx):
    channel = ctx.channel
    author = ctx.author
    message = ctx.message
    await _create_user(author)
    uinfo = fileIO("players/{}/info.json".format(author.id), "load")
    if uinfo["race"] and uinfo["class"] == "None":
        await ctx.send("Please start your character using `{}start`".format(Prefix))
        return
    match uinfo["inguild"]:
        case True:
            await ctx.send("You are already in a guild, you would need to leave your guild in order for you to create a guild.")
            return
        case False:
            em = discord.Embed(description="What is the name that you want to call your guild with?")
            await ctx.send(embed=em)
            def pred(m):
                return m.author == message.author and m.channel == message.channel
            answer1 = await client.wait_for("message", check=pred)
            if not os.path.exists("guilds/{}.json".format(answer1.content)):
                timestamp = datetime.now()
                new_guild = {
                        "banner" : "",
                        "date created" : timestamp.strftime(r"%d/%m/%Y - %I:%M %p"),
                        "founder" : "",
                        "funds" : "0",
                        "guildleader" : author.id,
                        "items" : "",
                        "members" : "1",
                        "name" : answer1.content,
                        "profile" : "",
                        "size" : "1",
                        "visits" : 0
                }
                fileIO("guilds/{}.json".format(answer1.content),"save", new_guild)
                uinfo["guild"] = str(answer1.content)
                uinfo["inguild"] = True
                uinfo = fileIO("players/{}/info.json".format(author.id), "save",uinfo)
                await ctx.send(f"Guild {answer1.content} has been created.")
                return
            else: 
                await ctx.send(f"A guild has already taken the name {answer1.content}.")
                return   

# this was to find the time of when something was created to add to the when a guild was created
# @client.command()
# async def time(ctx):
#     de = pytz.timezone('Europe/London')
#     await ctx.send(f"It is {datetime.datetime.now()}")
# import os.path, time
# print("Last modified: %s" % time.ctime(os.path.getmtime("test.txt")))
# print("Created: %s" % time.ctime(os.path.getctime("test.txt")))
    
    

@client.command()
async def guild(ctx,message = None,user: discord.Member = None):
    if user == None:
        user = ctx.author
    uinfo = fileIO("players/{}/info.json".format(user.id), "load")
    if uinfo["race"] and uinfo["class"] == "None":
        await ctx.send("Please start your character using `{}start`".format(Prefix))
        return
    if message == None:
        guild = uinfo["guild"]
        match uinfo["inguild"]:
            case True:
                info = fileIO("guilds/{}.json".format(guild) ,"load")
                info["visits"] = info["visits"] + 1
                fileIO("guilds/{}.json".format(guild), "save", info)
                embed=discord.Embed(title=info["name"])
                # if info["banner"] == "":
                #     return
                # else:
                #     # link = info["banner"]
                #     embed.thumbnail(url=)
                e = info["guildleader"]
                embed.add_field(name="GuildLeader",value = f"<@{e}>",inline=False)
                embed.add_field(name="Members", value=info["members"], inline=True)
                embed.add_field(name="Funds", value=info["funds"], inline=True)
                if info["items"] == "":
                    embed.add_field(name="Items", value="Nothing", inline=True)
                else:
                    embed.add_field(name="items",value=info["items"],inline=True)
                embed.add_field(name="Visits", value=str(info["visits"]), inline=True)
                embed.add_field(name="Date Created", value=info["date created"], inline=True)
                await ctx.send(embed=embed)
            case False:
                await ctx.send("You are not in a guild")
                return
            
    else:
        info = fileIO("guilds/{}.json".format(message) ,"load")
        info["visits"] = info["visits"] + 1
        fileIO("guilds/{}.json".format(message), "save", info)
            
        embed=discord.Embed(title=info["name"])
        e = info["guildleader"]
        embed.add_field(name="GuildLeader",value = f"<@{e}>",inline=False)
        embed.add_field(name="Members", value=info["members"], inline=True)
        embed.add_field(name="Funds", value=info["funds"], inline=True)
        if info["items"] == "":
            embed.add_field(name="Items", value="Nothing", inline=True)
        else:
            embed.add_field(name="items",value=info["items"],inline=True)
        embed.add_field(name="Visits", value=str(info["visits"]), inline=True)
        embed.add_field(name="Date Created", value=info["date created"], inline=True)
        await ctx.send(embed=embed)

@client.command(aliases=["guildsettings"])
async def gs(ctx):
    channel = ctx.channel
    author = ctx.author
    message = ctx.message
    uinfo = fileIO("players/{}/info.json".format(author.id), "load")
    guild = uinfo["guild"]
    info = fileIO("guilds/{}.json".format(guild) ,"load")
    match uinfo["inguild"]:
        case True:
            if info["guildleader"] == str(author.id) or info["guildleader"] == author.id:
                # await ctx.send("You are the guild leader of your guild")
                options = ["(0) GuildName","(1) GuildBanner","(2) Guildleader","(3) Visits"]
                options2 = ["0","1","2","3"]
                options3 = ["Yes","No"]
                options4 = ["Yes","yes","No","no"]
                em = discord.Embed(description="Guildleader <@{}> of {}\n```diff\n- Type the number on what you want to change.\n+ {}```only (3) Visits works so far".format(author.id,info["name"], "\n+ ".join(options)))
                await ctx.send(embed=em)
                
                def pred(m):
                    return m.author == message.author and m.channel == message.channel
                answer1 = await client.wait_for("message", check=pred)
                
                if answer1.content in options2:
                    if answer1.content == "0":
                        await ctx.send("guildname")
                    elif answer1.content == "1":
                        await ctx.send("guildbanner")
                    elif answer1.content == "2":
                        await ctx.send("guildleader")
                    elif answer1.content == "3":
                        em = discord.Embed(description="<@{}>\n```diff\n- Do you wish to reset your guild visits back to 0.\n+ {}``` Note that this is case sensitive".format(author.id, "\n+ ".join(options3)))
                        await ctx.send(embed=em)
                        def pred(m):
                            return m.author == message.author and m.channel == message.channel
                        answer1 = await client.wait_for("message", check=pred)
                        if answer1.content in options3:
                            if answer1.content == "Yes":
                                info["visits"] = 0
                                fileIO("guilds/{}.json".format(guild), "save", info)
                                await ctx.send("Your guild visits is reset to 0")
                            elif answer1.content == "No":
                                await ctx.send("Option cancelled")
                                return
                            else: 
                                await ctx.send("Option cancelled")
                                return
                        else:
                            await ctx.send("Option cancelled")
                            return
                else:   
                    await ctx.send("Choose a number next to what you want to change next time.")
                    return
                
                
                
            else:
                await ctx.send("You are not a guild leader of your guild")
                return
        case False:
            await ctx.send("You are not in a guild")
            return


'''
sell command
'''
@client.command()
async def sell():
    pass
    
@client.command()
async def nstats(ctx,user: discord.Member = None):
    if user == None:
        user = ctx.author
    info = fileIO("players/{}/info.json".format(user.id), "load")
    stats = Image.open("stats template.png")
    asset = user.avatar_url_as(size = 64)
    fontsize = 38
    font = ImageFont.truetype("arial.ttf", fontsize)
    deathcountsize = ImageFont.truetype("arial.ttf", 35)
    weaponsize = ImageFont.truetype("arial.ttf", 29)
    data = BytesIO(await asset.read())
    pfp = Image.open(data)
    pfp = pfp.resize((190,190))
    stats.paste(pfp, ((75,48)))
    stats.save("stats template copy1.png")
    draw = ImageDraw.Draw((stats))
    name = "Name: " + info["name"]
    cclass = "Class: " + info["class"]
    race = "Race: " + info["race"]
    health = "Health: " + str(info["health"])
    lvl = "Lvl: "+ str(info["lvl"])
    gold = "Gold: "+ str(info["gold"])
    death = "Deathcount:  " + str(info["deaths"])
    weapon = "Equipped: \n" + info["equip"]
    title = "Title: " + info["title"]
    exp = "Exp: " + str(info["exp"])
    draw.text((338,54), name,(0,0,0,),font = font)
    draw.text((332,149), cclass,(0,0,0,),font = font)    
    draw.text((634,50),race,(0,0,0,),font = font)
    draw.text((334,263),health,(0,0,0),font = font)
    draw.text((634,263),lvl,(0,0,0),font = font)
    draw.text((335,368),gold,(0,0,0),font = font)
    draw.text((634,354),weapon,(0,0,0),font = weaponsize)
    draw.text((642,448),death,(0,0,0),font = deathcountsize)
    draw.text((640,149),title,(0,0,0),font = font)
    draw.text((332,460),exp,(0,0,0),font=font)
    stats.save("stats template copy1.png")
    await ctx.send(file = discord.File("stats template copy1.png"))  

# @client.command()
# async def challenge(ctx):
#     author = ctx.author
#     message = ctx.author
#     info = fileIO("players/{}/info.json".format(author.id), "load")
#     if info["class"] == "None" and info["race"] == "None":
#         await ctx.send("Please start your player using `{}start`".format(Prefix))
#         return
#     def pred(m):
#         return m.author == message.author and m.channel == message.channel
#     answer2 = await client.wait_for("message", check=pred)
#     values = ["y", "Y", "yes", "Yes", "n", "N", "no", "No"]
#     if answer2.content in values:
#         if answer2.content == "y" or answer2.content == "Y" or answer2.content == "yes" or answer2.content == "Yes":
#             await ctx.send("Challenge accepted")
#             info["challenge"] = "accepted"
#             fileIO("players/{}/info.json".format(author.id), "save", info)
#             return
#         elif answer2.content == "n" or answer2.content == "N" or answer2.content == "no" or answer2.content == "No":
#             await ctx.send("Challenge declined")
#             info["challenge"] = "declined"
#             fileIO("players/{}/info.json".format(author.id), "save", info)
#             return
#         else:
#             await ctx.send("Challenge cancelled")
#             return
        
#async def get_time():
#    return datetime.datetime.now().strftime("%H:%M:%S")

# keep_alive()
client.run(config_location["Token"])

#Notes from testing phase:

# Making commands case insensitive
# Preventing non players from accessing the command unless an account is made for them
#json security as from skim reading my code it is evident that it is very insecure in a way that wrong information passed in may ruin something
#Reworking the nstats command and location- nstats meaning new stats card as a much better way of viewing your stats as something different from your average text based mmorpg games

# Thank you for watching testing phase one video

# I hope to make more notes from what I have learnt from this and make the changes. 

# Ill be making another testing phase 2 video later 

# see you next time

#take over the world