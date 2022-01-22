# ruby_counter.py

import re

import discord
from discord.ext import commands

from database import errors, users
from resources import emojis, exceptions, settings


class RubyCounterCog(commands.Cog):
    """Cog that contains all commands related to the ruby counter"""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """Runs when a message is sent in a channel."""
        if message.author.id != settings.EPIC_RPG_ID: return

        if message.embeds:
            embed: discord.Embed = message.embeds[0]
            message_description = message_field = message_author = ''
            if embed.description: message_description = str(embed.description)
            if embed.fields: message_field = str(embed.fields[0].value)
            if embed.author:
                message_author = str(embed.author.name)
                icon_url = embed.author.icon_url

            # Rubies from trades E and F
            if 'our trade is done then' in message_description.lower() and '<:ruby' in message_field.lower():
                user_name = user = None
                try:
                    search_string = "\*\*(.+?)\*\*"
                    user_name = re.search(search_string, message_field).group(1)
                    if user_name == 'EPIC NPC': user_name = re.search(search_string, message_field).group(2)
                    user_name = user_name.encode('unicode-escape',errors='ignore').decode('ASCII').replace('\\','')
                except Exception as error:
                    await message.add_reaction(emojis.WARNING)
                    await errors.log_error(error)
                    return

                for member in message.guild.members:
                    member_name = member.name.encode('unicode-escape',errors='ignore').decode('ASCII').replace('\\','')
                    if member_name == user_name:
                        user = member
                        break
                if user is None:
                    await message.add_reaction(emojis.WARNING)
                    await errors.log_error(f'User not found in trade message: {message}')
                    return
                try:
                    user_settings: users.User = await users.get_user(user.id)
                except exceptions.FirstTimeUserError:
                    return
                if not user_settings.bot_enabled or not user_settings.ruby_counter_enabled: return
                epic_npc_pos = message_field.find('**EPIC NPC**')
                ruby_pos = message_field.find('<:ruby')
                trade_type = 'F' if ruby_pos > epic_npc_pos else 'E'
                search_string = "603304907650629653> x(.+?) \\n"  if trade_type == 'E' else "603304907650629653> x(.+?)$"
                try:
                    ruby_count = re.search(search_string, message_field).group(1)
                    ruby_count = int(ruby_count)
                except Exception as error:
                    await message.add_reaction(emojis.WARNING)
                    await errors.log_error(error)
                    return
                if trade_type == 'E': ruby_count *= -1
                ruby_count += user_settings.rubies
                if ruby_count < 0: ruby_count == 0
                await user_settings.update(rubies=ruby_count)
                if user_settings.rubies == ruby_count: await message.add_reaction(emojis.NAVI)

            # Rubies from lootboxes
            if "'s lootbox" in message_author.lower() and '<:ruby' in message_field.lower():
                user_id = user_name = user = None
                try:
                    user_id = int(re.search("avatars\/(.+?)\/", icon_url).group(1))
                except:
                    try:
                        user_name = re.search("^(.+?)'s lootbox", message_author).group(1)
                        user_name = user_name.encode('unicode-escape',errors='ignore').decode('ASCII').replace('\\','')
                    except Exception as error:
                        await message.add_reaction(emojis.WARNING)
                        await errors.log_error(error)
                        return
                if user_id is not None:
                    user = await message.guild.fetch_member(user_id)
                else:
                    for member in message.guild.members:
                        member_name = member.name.encode('unicode-escape',errors='ignore').decode('ASCII').replace('\\','')
                        if member_name == user_name:
                            user = member
                            break
                if user is None:
                    await message.add_reaction(emojis.WARNING)
                    await errors.log_error(f'User not found in lootbox message: {message}')
                    return
                try:
                    user_settings: users.User = await users.get_user(user.id)
                except exceptions.FirstTimeUserError:
                    return
                if not user_settings.bot_enabled or not user_settings.ruby_counter_enabled: return
                try:
                    ruby_pos = message_field.find('<:ruby')
                    number_start_pos = message_field.rfind('+', 0, ruby_pos)
                    ruby_count = re.search('\+(.+?) <:ruby', message_field[number_start_pos:]).group(1)
                    ruby_count = int(ruby_count)
                except Exception as error:
                    await message.add_reaction(emojis.WARNING)
                    await errors.log_error(error)
                    return
                ruby_count += user_settings.rubies
                if ruby_count < 0: ruby_count == 0
                await user_settings.update(rubies=ruby_count)
                if user_settings.rubies == ruby_count: await message.add_reaction(emojis.NAVI)

            # Rubies from inventory
            if "'s inventory" in message_author.lower():
                user_id = user_name = user = None
                try:
                    user_id = int(re.search("avatars\/(.+?)\/", icon_url).group(1))
                except:
                    try:
                        user_name = re.search("^(.+?)'s inventory", message_author).group(1)
                        user_name = user_name.encode('unicode-escape',errors='ignore').decode('ASCII').replace('\\','')
                    except Exception as error:
                        await message.add_reaction(emojis.WARNING)
                        await errors.log_error(error)
                        return
                if user_id is not None:
                    user = await message.guild.fetch_member(user_id)
                else:
                    for member in message.guild.members:
                        member_name = member.name.encode('unicode-escape',errors='ignore').decode('ASCII').replace('\\','')
                        if member_name == user_name:
                            user = member
                            break
                if user is None:
                    await message.add_reaction(emojis.WARNING)
                    await errors.log_error(f'User not found in inventory message: {message}')
                    return
                try:
                    user_settings: users.User = await users.get_user(user.id)
                except exceptions.FirstTimeUserError:
                    return
                if not user_settings.bot_enabled or not user_settings.ruby_counter_enabled: return
                if  '<:ruby' not in message_field.lower():
                    ruby_count = 0
                else:
                    try:
                        ruby_count = re.search("ruby\*\*: (.+?)\\n", message_field).group(1)
                        ruby_count = int(ruby_count)
                    except:
                        try:
                            ruby_count = re.search("ruby\*\*: (.+?)$", message_field).group(1)
                            ruby_count = int(ruby_count)
                        except Exception as error:
                            await message.add_reaction(emojis.WARNING)
                            await errors.log_error(error)
                            return
                await user_settings.update(rubies=ruby_count)
                if user_settings.rubies == ruby_count: await message.add_reaction(emojis.NAVI)

        if not message.embeds:
            message_content = message.content
            # Ruby training helper
            if '** is training in the mine!' in message_content.lower():
                user_name = user = None
                try:
                    user_name = re.search("^\*\*(.+?)\*\* ", message_content).group(1)
                    user_name = user_name.encode('unicode-escape',errors='ignore').decode('ASCII').replace('\\','')
                except Exception as error:
                    await message.add_reaction(emojis.WARNING)
                    await errors.log_error(error)
                    return
                for member in message.guild.members:
                    member_name = member.name.encode('unicode-escape',errors='ignore').decode('ASCII').replace('\\','')
                    if member_name == user_name:
                        user = member
                        break
                if user is None:
                    await message.add_reaction(emojis.WARNING)
                    await errors.log_error(f'User not found in ruby training helper message: {message}')
                    return
                try:
                    user_settings: users.User = await users.get_user(user.id)
                except exceptions.FirstTimeUserError:
                    return
                if not user_settings.bot_enabled or not user_settings.ruby_counter_enabled: return
                try:
                    ruby_count = re.search('more than (.+?) <:ruby', message_content).group(1)
                    ruby_count = int(ruby_count)
                except Exception as error:
                    await message.add_reaction(emojis.WARNING)
                    await errors.log_error(error)
                    return
                answer = 'YES' if user_settings.rubies > ruby_count else 'NO'
                await message.reply(f'`{answer}` (you have {user_settings.rubies} {emojis.RUBY}', mention_author=False)

            # Rubies from work commands
            if '** got ' in message_content.lower() and '<:ruby' in message_content.lower():
                user_name = user = None
                try:
                    user_name = re.search("\*\*(.+?)\*\* got", message_content, re.IGNORECASE).group(1)
                    user_name = user_name.encode('unicode-escape',errors='ignore').decode('ASCII').replace('\\','')
                except Exception as error:
                    await message.add_reaction(emojis.WARNING)
                    await errors.log_error(error)
                    return
                for member in message.guild.members:
                    member_name = member.name.encode('unicode-escape',errors='ignore').decode('ASCII').replace('\\','')
                    if member_name == user_name:
                        user = member
                        break
                if user is None:
                    await message.add_reaction(emojis.WARNING)
                    await errors.log_error(f'User not found in work message: {message}')
                    return
                try:
                    user_settings: users.User = await users.get_user(user.id)
                except exceptions.FirstTimeUserError:
                    return
                if not user_settings.bot_enabled or not user_settings.ruby_counter_enabled: return
                try:
                    ruby_count = re.search('\*\* got (.+?) <:ruby', message_content, re.IGNORECASE).group(1)
                    ruby_count = int(ruby_count)
                except Exception as error:
                    await message.add_reaction(emojis.WARNING)
                    await errors.log_error(error)
                    return
                ruby_count += user_settings.rubies
                if ruby_count < 0: ruby_count == 0
                await user_settings.update(rubies=ruby_count)

            # Rubies from crafting ruby sword
            if '`ruby sword` successfully crafted' in message_content.lower():
                message_history = await message.channel.history(limit=50).flatten()
                user_command_message = None
                for msg in message_history:
                    if msg.content is not None:
                        if msg.content.lower() == 'rpg craft ruby sword':
                            user_command_message = msg
                            break
                if user_command_message is None:
                    await message.add_reaction(emojis.WARNING)
                    await errors.log_error('Couldn\'t find a command for the ruby sword crafting message.')
                    return
                user = user_command_message.author
                try:
                    user_settings: users.User = await users.get_user(user.id)
                except exceptions.FirstTimeUserError:
                    return
                if not user_settings.bot_enabled or not user_settings.ruby_counter_enabled: return
                ruby_count = user_settings.rubies - 4
                if ruby_count < 0: ruby_count == 0
                await user_settings.update(rubies=ruby_count)
                if user_settings.rubies == ruby_count: await message.add_reaction(emojis.NAVI)

            # Rubies from crafting ruby armor
            if '`ruby armor` successfully crafted' in message_content.lower():
                message_history = await message.channel.history(limit=50).flatten()
                user_command_message = None
                for msg in message_history:
                    if msg.content is not None:
                        if msg.content.lower() == 'rpg craft ruby armor':
                            user_command_message = msg
                            break
                if user_command_message is None:
                    await message.add_reaction(emojis.WARNING)
                    await errors.log_error('Couldn\'t find a command for the ruby armor crafting message.')
                    return
                user = user_command_message.author
                try:
                    user_settings: users.User = await users.get_user(user.id)
                except exceptions.FirstTimeUserError:
                    return
                if not user_settings.bot_enabled or not user_settings.ruby_counter_enabled: return
                ruby_count = user_settings.rubies - 7
                if ruby_count < 0: ruby_count == 0
                await user_settings.update(rubies=ruby_count)
                if user_settings.rubies == ruby_count: await message.add_reaction(emojis.NAVI)

            # Rubies from crafting coin sword
            if '`coin sword` successfully crafted' in message_content.lower():
                message_history = await message.channel.history(limit=50).flatten()
                user_command_message = None
                for msg in message_history:
                    if msg.content is not None:
                        if msg.content.lower() == 'rpg craft coin sword':
                            user_command_message = msg
                            break
                if user_command_message is None:
                    await message.add_reaction(emojis.WARNING)
                    await errors.log_error('Couldn\'t find a command for the coin sword crafting message.')
                    return
                user = user_command_message.author
                try:
                    user_settings: users.User = await users.get_user(user.id)
                except exceptions.FirstTimeUserError:
                    return
                if not user_settings.bot_enabled or not user_settings.ruby_counter_enabled: return
                ruby_count = user_settings.rubies - 4
                if ruby_count < 0: ruby_count == 0
                await user_settings.update(rubies=ruby_count)
                if user_settings.rubies == ruby_count: await message.add_reaction(emojis.NAVI)

            # Rubies from crafting ultra-edgy armor
            if '`ultra-edgy armor` successfully forged' in message_content.lower():
                message_history = await message.channel.history(limit=50).flatten()
                user_command_message = None
                for msg in message_history:
                    if msg.content is not None:
                        if msg.content.lower() == 'rpg forge ultra-edgy armor':
                            user_command_message = msg
                            break
                if user_command_message is None:
                    await message.add_reaction(emojis.WARNING)
                    await errors.log_error('Couldn\'t find a command for the ultra-edgy armor crafting message.')
                    return
                user = user_command_message.author
                try:
                    user_settings: users.User = await users.get_user(user.id)
                except exceptions.FirstTimeUserError:
                    return
                if not user_settings.bot_enabled or not user_settings.ruby_counter_enabled: return
                ruby_count = user_settings.rubies - 400
                if ruby_count < 0: ruby_count == 0
                await user_settings.update(rubies=ruby_count)
                if user_settings.rubies == ruby_count: await message.add_reaction(emojis.NAVI)


# Initialization
def setup(bot):
    bot.add_cog(RubyCounterCog(bot))