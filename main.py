import discord
import requests
import json
import random
from io import BytesIO
import urllib.request as urllib2
import urllib.error
import urllib.parse

#Client setup
intents = discord.Intents.all()
client = discord.Client(intents = intents)

#Bot logon
@client.event
async def on_ready():
    print("Logged in as a bot {0.user}".format(client))

@client.event
async def on_message(message):
    #Avoid recursion by ignoring self-written messages
    if message.author == client.user:
        return

    msg = message.content

    #Find a player and retrieve/display some of their info. Command formats:
    #1) $search <Character Name>
    #2) $search <Character Name> $ <Server>

    if msg.startswith("$search"):

        userInput = msg.split("$search ", 1)[1] #Remove the command tag at the beginning

        #Build the URL to search for a character
        if userInput.find("$") > -1: #Format 2: Name + Server
            playerName = userInput.split(" $ ", 1)[0]
            playerServer = userInput.split(" $ ", 1)[1]
            url = "https://xivapi.com/character/search?name=" + playerName.replace(' ', '+') + "&server=" + playerServer
        else: #Format 2: Name only
            playerName = userInput
            playerServer = "No Server"
            url = "https://xivapi.com/character/search?name=" + playerName.replace(' ', '+')

        print("Received " + playerName + ", " + playerServer)

        #Send the search request, and retrieve the first/only character's basic data
        request = urllib2.Request(url)
        request.add_header('User-Agent', '&lt;User-Agent&gt;')
        playerData = json.loads(urllib2.urlopen(request).read())
        playerID = playerData["Results"][0]["ID"]

        #Take the ID received and perform a query to receive the rest of the character's info
        request = urllib2.Request("https://xivapi.com/character/" + str(playerID))
        request.add_header('User-Agent', '&lt;User-Agent&gt;')
        playerData = json.loads(urllib2.urlopen(request).read())

        #Check if in an FC
        if playerData['Character']['FreeCompanyName']:
            playerFC = playerData['Character']['FreeCompanyName']
        else:
            playerFC = "None"
        
        #Retrieve info that's always present
        playerImg = playerData['Character']['Portrait']
        playerServer = playerData['Character']['Server']

        #Send the character image to the channel
        image = BytesIO(requests.get(playerImg).content)
        await message.channel.send(file=discord.File(image, "fashion.png"))

        #Send the other info to the channel
        await message.channel.send(playerName + " -- Server: " + playerServer + " -- FC: " + playerFC)

token = ""
client.run(token)