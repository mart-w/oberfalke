#!/usr/bin/env python3

# Falkenbot -- die softwaregewordene Inkarnation unserer gelieben Falken.

import discord
import asyncio
import datetime

# Lese API-Token ein.
with open("token.txt", "r") as tokendatei:
    api_token = tokendatei.readline().rstrip()

# Client-Klasse mit Event-Listenern
class Oberfalkenclient(discord.Client):
    # Vergleiche send_message(). Simuliert Tippen durch den Bot.
    async def type_message(self, destination, content=None, tts=False, embed=None):
        # Berechne simulierte Tippzeit in Sekunden aus Länge der Nachricht.
        if not content:
            tippzeit = 1 # Keine Nachricht; nehme 1 für eingebettete Inhalte an.
        else:
            tippzeit = len(str(content)) / 30
            if tippzeit > 10:
                tippzeit = 10

        await self.send_typing(destination)
        await asyncio.sleep(tippzeit)
        return await self.send_message(destination, content=content, tts=tts, embed=embed)

    # Event-Listener:
    async def on_ready(self):
        print("Verbunden mit %d Servern:" % (len(client.servers)))
        for server in client.servers:
            print("%s -- %s" % (server.id, server.name))

# Initialisiere Client-Objekt.
client = Oberfalkenclient()

# Starte Bot-Session.
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
