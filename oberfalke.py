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
            self.user_mention_count[mentioner.id] += 1

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

    async def respond_to_falkenheil(self, message):
        # Respond to the message so long as it isn't the bot's own.
        if not message.author.id == self.user.id:
            await self.add_reaction(message, "🦅")
            await self.type_message(message.channel, content="HEIL IHNEN!")

        # Wait for responses from other users and thumbs-up and thank them.
        responders = []
        response = await self.wait_for_message(
            timeout=15,
            check=lambda s:s.content.casefold().find("heil ihnen") > -1
        )

        while response:
            if not response.author.id == self.user.id:
                if not response.author.id in responders:
                    responders.append(response.author.id)
                await self.add_reaction(response, "👍")

            response = await self.wait_for_message(
                timeout=15,
                check=lambda s:s.content.casefold().find("heil ihnen") > -1
            )

        if not responders == []:
            thankyoustring = "Der Dank der Falken gebührt "

            for index, responder in enumerate(responders):
                thankyoustring += "<@" + responder + ">"

                if index <= len(responders) - 3:
                    thankyoustring += ", "
                if index == len(responders) - 2:
                    thankyoustring += " und "

            thankyoustring += " für die Ergebenheit!"

            await self.type_message(message.channel, content=thankyoustring)


    # Event listeners:

    async def on_ready(self):
        print("Verbunden mit %d Servern:" % (len(client.servers)))
        for server in client.servers:
            print("%s -- %s" % (server.id, server.name))

    async def on_message(self, message):
        # Casefolded version of the message for case-insensitive searching
        casefoldmsg = message.content.casefold()

        # Search for mention and respond if found
        bot_mentionstring = '<@' + self.user.id + '>'

        # The raw message string is being used to not alter the IDs
        if message.content.find(bot_mentionstring) > -1:
            await self.respond_to_mention(message.author, message.channel)

        # Search for the words "Heil", "den", and "Falken" in that order and
        # respond if found.
        pos = casefoldmsg.find("heil")
        if pos > -1:
            pos = casefoldmsg.find(" den ", pos)
            if pos > -1:
                pos = casefoldmsg.find("falken", pos)
                if pos > -1:
                    await self.respond_to_falkenheil(message)
                else: # The user hailed the wrong party
                    await self.type_message(
                        message.channel,
                        content="Bitte was, <@%s>?! **HEIL DEN FALKEN!**" % (message.author.id)
                    )
            else: # The user just said "Heil" in any context
                if not casefoldmsg.find("heil ihnen") > -1: # "Heil ihnen" should end the joke, not start yet a new one
                    await self.type_message(
                        message.channel,
                        content="HEIL DEN FALKEN!"
                    )

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
