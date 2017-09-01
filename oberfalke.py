#!/usr/bin/env python3

# Falkenbot -- a software incarnation of our beloved falcons.

import discord
import asyncio
import datetime

# Read API token from token file.
with open("token.txt", "r") as tokenfile:
    api_token = tokenfile.readline().rstrip()

# Client class with event listeners
class Oberfalke_client(discord.Client):
    def __init__(self, *args, **kwargs):
        super(Oberfalke_client, self).__init__(*args, **kwargs)

        # lists how often the bot has been mentioned by individual users
        self.user_mention_count = {}

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

    async def respond_to_mention(self, mentioner, channel):
        # Increment the user's mention counter
        if not mentioner.id in self.user_mention_count:
            self.user_mention_count[mentioner.id] = 1
        else:
            self.user_mention_count[mentioner.id] = self.user_mention_count[mentioner.id] + 1

        # Respond according to mention count
        author_mention_count = self.user_mention_count[mentioner.id]
        author_mention_string = "<@" + mentioner.id + ">"

        if author_mention_count == 1:
            await self.type_message(
                channel,
                content="Wage es nicht, mich anzusprechen, %s!" % (author_mention_string)
            )
        elif author_mention_count == 2:
            await self.type_message(
                channel,
                content="Ich warne dich, %s, mit mir ist nicht zu scherzen." % (author_mention_string)
            )
        elif author_mention_count == 3:
            await self.type_message(
                channel,
                content="Ich sage es kein weiteres Mal, %s. Das nächste Mal hat das Konsequenzen." % (author_mention_string)
            )
        else:
            await self.type_message(
                channel,
                content="Das reicht. Hätte <@269910584877645825> das schon implementiert, hättest du jetzt Ärger, %s." % (author_mention_string)
            )

    # Event listeners:
    async def on_ready(self):
        print("Verbunden mit %d Servern:" % (len(client.servers)))
        for server in client.servers:
            print("%s -- %s" % (server.id, server.name))

    async def on_message(self, message):
        # Search for mention and respond if found
        bot_mentionstring = '<@' + self.user.id + '>'

        if message.content.find(bot_mentionstring) > -1:
            await self.respond_to_mention(message.author, message.channel)

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
