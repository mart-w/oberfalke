#!/usr/bin/env python3

# Falkenbot -- a software incarnation of our beloved falcons.

import discord
import asyncio
import datetime
import re
import random
import datetime
from tinydb import TinyDB, Query

# Read API token from token file.
with open("token.txt", "r") as tokenfile:
    api_token = tokenfile.readline().rstrip()


# Client class with event listeners
class Oberfalke_client(discord.Client):
    def __init__(self, *args, **kwargs):
        super(Oberfalke_client, self).__init__(*args, **kwargs)

        # lists how often the bot has been mentioned by individual users
        self.user_mention_count = {}

        # Regular expression objects.
        self.re_quote = re.compile(r"(?P<author>.*?)\s*>\s*(?P<content>.+)")

        self.re_falkenheil = re.compile(r"HEIL[ \w,:]+DEN[ \w,]+FALKEN", flags=re.IGNORECASE)
        self.re_falkenheil_response = re.compile(r"HEIL IHNEN", flags=re.IGNORECASE)
        self.re_falkenspruch = re.compile(r"falke", flags=re.IGNORECASE)
        self.re_treason = re.compile(r"HEIL ((?:(?:DEM)|(?:DER)|(?:DEN)) [ \w,]*)", flags=re.IGNORECASE)

        # TinyDB user database.
        self.db_users = TinyDB("users.json")
        self.DB_User = Query()

        # Lists on which channels the bot is currently running respnd_to_falkenheil()
        self.falkenheil_channels = []


    # Returns the reputaion value of the given user or 0 if the user does not exist yet.
    async def get_reputation(self, user):
        result = self.db_users.search(self.DB_User.id == user.id)

        if result:
            return result[0]["reputation"]
        else:
            return 0

    # Sets the reputation of a user to the given value.
    async def set_reputation(self, user, reputation):
        if self.db_users.search(self.DB_User.id == user.id):
            self.db_users.update({"reputation": reputation}, self.DB_User.id == user.id)
        else:
            self.db_users.insert({"id": user.id, "reputation": reputation})

    # Changes the user's reputation by the given value or sets their reputaion to it if the user does not exist.
    async def update_reputation(self, user, change):
        reputation = await self.get_reputation(user)

        reputation += change

        await self.set_reputation(user, reputation)

    # Check if a :pro: emoji exist. If so, return according Emoji object, otherwise thumbs-up
    async def get_pro_emoji(self, server):
        for emoji in server.emojis:
            if emoji.name == "pro":
                return emoji

        return "👍"

    # Similar to send_message(), but simulates actual typing by adding delays
    async def type_message(self, destination, content=None, tts=False, embed=None):
        # Calculate typing_delay based on the length of content
        if not content:
            typing_delay = 1 # No text content; assume 1 for embedded content
        else:
            typing_delay = len(str(content)) / 30
            if typing_delay > 10:
                typing_delay = 10

        await self.send_typing(destination)
        await asyncio.sleep(typing_delay)
        return await self.send_message(destination, content=content, tts=tts, embed=embed)

    # Compares a User object to a name string and returns if the given object is meant by this string.
    async def is_same_user(self, user_obj, user_str):
        # Convert all strings to lowercase so that the search is case-insensitive
        user_obj_id = user_obj.id.lower() # User ID
        user_obj_full_name = user_obj.name.lower() + '#' + user_obj.discriminator # Full user name including discriminator, e.g. User#1234
        user_obj_display_name = user_obj.display_name.lower() # The user's display name
        user_str = user_str.lower()

        # Name string is the beginning of or is the user ID,
        # is contained in or is the username
        # or is contained in or is the display name.
        if user_obj_id.find(user_str) == 0 \
        or user_obj_full_name.find(user_str) > -1 \
        or user_obj_display_name.find(user_str) > -1:
            return True
        else:
            return False

    # Finds and returns a quote in a given channel and returns the found Message object.
    async def search_message_by_quote(self, quote):
        match = self.re_quote.fullmatch(quote.content)
        match_author = match.group("author")
        match_content = match.group("content")

        if match_author:
            # Search the last 300 messages
            async for message in self.logs_from(quote.channel, limit=300, before=quote):
                if await self.is_same_user(message.author, match_author):
                    if message.content.find(match_content) > -1:
                        return message

            return None # Message not found
        else:
            # Get the last 100 messages in the channel
            async for message in self.logs_from(quote.channel, limit=100, before=quote):
                if message.content.find(match_content) > -1:
                    return message

            return None # Message not found

    # Quote a message based on a chat quote
    async def quote_message(self, quote):
        quoted_message = await self.search_message_by_quote(quote)
        if quoted_message:
            timedatelabel = quoted_message.timestamp.strftime("Am %d.%m.%Y um %H:%M Uhr")

            if quoted_message.edited_timestamp: # Message was edited.
                timedatelabel += quoted_message.edited_timestamp.strftime(", bearbeitet am %d.%m.%Y um %H:%M Uhr")

            timedatelabel += '.'

            quote_embed = discord.Embed(
                title=quoted_message.content,
                color=0x1abc9c
            )
            quote_embed.set_author(
                name=quoted_message.author.display_name,
                icon_url=quoted_message.author.avatar_url
            )
            quote_embed.set_footer(
                text="%s Zitiert von %s." % (timedatelabel, quote.author.display_name),
                icon_url=quote.author.avatar_url
            )

            await self.send_message(quote.channel, embed=quote_embed)
        else:
            quoter_mention_string = '<@' + quote.author.id + '>'
            await self.type_message("Tut mir leid, %s, diese Nachricht konnte ich nicht finden." % (quoter_mention_string))


    async def respond_to_mention(self, mentioner, channel):
        author_reputation = await self.get_reputation(mentioner)
        author_mention_string = "<@" + mentioner.id + ">"

        if author_reputation < -5:
            await self.update_reputation(mentioner, -2)
            await self.type_message(channel, random.choice([
            "Schnauze auf den billigen Plätzen!",
            "Mich sprichst *du* nicht beim Namen an, %s!" % (author_mention_string),
            "Ich rede nicht mit deinesgleichen.",
            "Hat jemand was gesagt?",
            "Habt ihr etwas gehört?",
            "Ich glaube, ich bekomme Tinnitus. War da was?",
            "*pfeift*"
            ]))
        elif author_reputation > 10:
            await self.update_reputation(mentioner, 1)
            await self.type_message(channel, random.choice([
            "%s! Von dir höre ich doch immer gern." % (author_mention_string),
            "Es ist immer schön, den Respekt seiner Untertanen zu ernten.",
            "Lang lebe %s!" % (author_mention_string),
            "Du hast immer die besten Worte parat, %s." % (author_mention_string)
            ]))
        else:
            await self.update_reputation(mentioner, -1)
            await self.type_message(channel, random.choice([
            "Ist was?!",
            "Muss das jetzt sein?",
            "Jaja, ist gut.",
            "Kenne ich dich?",
            "Ich weiß nicht, was ich von dir denken soll.",
            "*gähnt* Mhm?"
            ]))


    async def respond_to_falkenheil(self, message):
        print(self.falkenheil_channels)
        # Make sure the coroutine is not running twice at the same time in one channel
        if not message.channel.id in self.falkenheil_channels:
            self.falkenheil_channels.append(message.channel.id)

            supporters = []
            # Respond to the message so long as it isn't the bot's own.
            if not message.author.id == self.user.id:
                supporters.append(message.author.id)
                await self.update_reputation(message.author, 2)
                await self.add_reaction(message, "🦅")
                await self.type_message(message.channel, content="HEIL IHNEN!")

            # Wait for responses from other users and thumbs-up them.
            response = await self.wait_for_message(
                timeout=15,
                check=lambda s:
                    s.channel.id == message.channel.id
                    and s.author.id != self.user.id
                    and self.re_falkenheil_response.search(s.content)
            )

            while response:
                if not response.author.id in supporters:
                    supporters.append(response.author.id)
                    await self.update_reputation(response.author, 1)
                await self.add_reaction(response, await self.get_pro_emoji(message.server))

                response = await self.wait_for_message(
                    timeout=15,
                    check=lambda s:
                        s.channel.id == message.channel.id
                        and s.author.id != self.user.id
                        and self.re_falkenheil_response.search(s.content)
                )

            self.falkenheil_channels.remove(message.channel.id)

    async def respond_to_treason(self, message, evidence):
        await self.update_reputation(message.author, -5)

        author_mentionstring = "<@" + message.author.id + ">"

        # Generate exclamation repeating the traitor's unholy words
        exclamation = evidence.group(0)
        exclamation = exclamation[:1].upper() + exclamation[1:] # Capitalise first letter

        await self.type_message(
            message.channel,
            content="%s %s?! Was soll das denn? HEIL DEN FALKEN!" % (author_mentionstring, exclamation)
        )


    # Event listeners:

    async def on_ready(self):
        print("Verbunden mit %d Servern:" % (len(client.servers)))
        for server in client.servers:
            print("%s -- %s" % (server.id, server.name))

    async def on_message(self, message):
        # Search for quotation
        if self.re_quote.fullmatch(message.content):
            await self.quote_message(message)

        # Fun features.
        else:
            # Search for mention and respond if found
            bot_mentionstring = '<@' + self.user.id + '>'

            if message.content.find(bot_mentionstring) > -1:
                await self.respond_to_mention(message.author, message.channel)

            # Search for hailing or mentioning of the falcons and respond accordingly
            if self.re_falkenheil.search(message.content):
                await self.respond_to_falkenheil(message)
            elif self.re_falkenspruch.search(message.content):
                if not message.author.id == self.user.id:
                    await self.type_message(message.channel, content="HEIL DEN FALKEN!")
            else:
                # Has anyone but the holy falcons been hailed?
                treason = self.re_treason.search(message.content)
                if treason: # hang them!
                    await self.respond_to_treason(message, treason)

# Initialise client object.
client = Oberfalke_client()

# Start bot session.
client.run(api_token)

# MIT License
#
# Copyright (c) 2017 Martin W.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
