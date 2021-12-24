
# # bot.py
# Reference: https://realpython.com/how-to-make-a-discord-bot-python/

import os, re, sys

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()
guild = None
mentorRequestsChannel = None

USERS = {}
KEYWORDS = ["Python", "C/C++/C#", "Java", "JavaSpring", "Kotlin", "Objective C", "Swift", "React", 
    "HTML/CSS", "Javascript", "NodeJS", "ExpressJS", "AngularJS", "VueJS", "PHP", "Laravel", 
    "Ruby", "Ruby on Rails", "Django", "Android App", "IOS App", "Web Development", 
    "Hardware/Circuitry", "Arduino", "Raspberry Pi", "ML/AI", "Graphics", 
    "UX/Design", "Game Design", "SQL/Databases", "Cloud Services/DNS", 
    "Git", "VR/AR", "Other/None"]


class ResponseStrings:

    @staticmethod
    def mentorRequest(uid, name, keywords, summary, description, attempts):
        return (
            f"{name} (<@{uid}>) needs help with **{'**, **'.join(keywords)}**:\n\n"
            f"Project summary: \n> {summary}\n\nIssue: \n> {description}\n\n"
            f"Steps taken: \n> {attempts}\n\n*Please react to this post and send "
            f"a private message to <@{uid}> if you would like to assist.*"
        )
    
    @staticmethod
    def privateResponseInitiate(name):
        return (
            f"Hi {name}, you have requested assistance from a mentor. "
            f"Please answer the following questions with details about your issue. "
            f"If at any point you want to cancel the request, respond with the "
            f"phrase 'quit'. Would you like to continue? (yes/no)"
        )

    @staticmethod
    def privateResponseQuit():
        return "Your request has been cancelled. Reply to this message to initiate a new request."

    @staticmethod
    def privateResponseTruncate(length):
        return f"The message was too long, so it was truncated to {length} characters."

    @staticmethod
    def privateResponseConfirm():
        return "I'm sorry, I didn't understand that. Please respond 'yes' to continue."

    @staticmethod
    def privateRequestName():
        return "Please enter your full name:"

    @staticmethod
    def privateRequestDescription():
        return "Give a 1-2 sentence description of your project: (Max 500 characters)"

    @staticmethod
    def privateRequestKeywords(keywords):
        return f"Select between one and three keywords that best represent your issue: (e.g., '1, 8, 11')\n{keywords}"

    @staticmethod
    def privateResponseKeywordsNumber():
        return "Please select between one and three keywords."

    @staticmethod
    def privateResponseKeywordsInvalid(number):
        return f"The number {number} does not correspond with a valid keyword. Please try again."

    @staticmethod
    def privateResponseKeywords(keywords):
        return f"You selected the keywords: {keywords}."

    @staticmethod
    def privateRequestSummary():
        return (
            "Please describe the issue you're encountering. You will have the opportunity "
            "to explain your issue in more depth once we connect you to a mentor. "
            "If you just want guidance on getting started or on a particular topic, "
            "that is okay too. (Max 1000 characters)"
        )

    @staticmethod
    def privateRequestAttempts():
        return (
            "Have you taken any steps to try and solve the issue? It's okay if "
            "you haven't made any progress so far. (Max 1000 characters)"
        )

    @staticmethod
    def privateResponseSuccess():
        return "Thank you for your response. Your request is being processed."

    @staticmethod
    def privateResponseRemind():
        return (
            "Your mentor request is currently being processed. If you wish to make "
            "another request, you must first cancel this one by typing 'quit'."
        )

    @staticmethod
    def privateResponseAccepted(mentor):
        return f"Your mentor request has been accepted by <@{mentor}>.\n"


@client.event
async def on_ready():
    # Locate the server for SB Hacks VII:
    global guild
    guild = discord.utils.get(client.guilds, name=GUILD)
    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name} (id: {guild.id})',
        file=sys.stderr
    )

    # get the mentor requests channel:
    global mentorRequestsChannel
    mentorRequestsChannel = discord.utils.get(guild.text_channels, name="mentor-requests")

@client.event
async def on_message(message):
    # ignore if the message is coming from us:
    if message.author == client.user:
        return

    # only respond if the message is a DM:
    if message.channel.type == discord.ChannelType.private:
        print(f"Received message from {message.author.id} ({message.author.name}).", file=sys.stderr)

        # if the user is new, then respond and add them to the dict:
        if (message.author.id not in USERS):
            USERS[message.author.id] = {"status": 1}
            print(f"Sending response #1 to {message.author.id} ({message.author.name}).", file=sys.stderr)
            await message.channel.send(ResponseStrings.privateResponseInitiate(message.author.name))
            return
        
        # if the user wants to quit, delete them from the dict:
        elif (message.content.lower() in ["quit", "exit", "cancel"]):
            del USERS[message.author.id]
            print(f"Sending response QUIT to {message.author.id} ({message.author.name}).", file=sys.stderr)
            await message.channel.send(ResponseStrings.privateResponseQuit())
            return

        # the user responds 'yes' to continue
        elif (USERS[message.author.id]["status"] == 1):

            if (message.content.strip().lower() in ["y", "yes"]):
                USERS[message.author.id]["channel"] = message.channel
                USERS[message.author.id]["handle"] = message.author.name
                USERS[message.author.id]["discriminator"] = message.author.discriminator
                USERS[message.author.id]["status"] = 2
                print(f"Sending response #2 to {message.author.id} ({message.author.name}).", file=sys.stderr)
                await message.channel.send(ResponseStrings.privateRequestName())
                return

            elif (message.content.strip().lower() in ["n", "no"]):
                del USERS[message.author.id]
                print(f"Sending response QUIT to {message.author.id} ({message.author.name}).", file=sys.stderr)
                await message.channel.send(ResponseStrings.privateResponseQuit())
                return
            
            else:
                print(f"Sending response #1.1 to {message.author.id} ({message.author.name}).", file=sys.stderr)
                await message.channel.send(ResponseStrings.privateResponseConfirm())
                return

        # the user enters their name:
        elif (USERS[message.author.id]["status"] == 2):
            
            # name cannot be empty:
            if (len(message.content.strip()) == 0):
                print(f"Sending response #2.1 to {message.author.id} ({message.author.name}).", file=sys.stderr)
                await message.channel.send(ResponseStrings.privateRequestName())
                return

            else:
                USERS[message.author.id]["name"] = message.content.strip()[:50]
                USERS[message.author.id]["status"] = 3
                print(f"Sending response #3 to {message.author.id} ({message.author.name}).", file=sys.stderr)
                await message.channel.send(ResponseStrings.privateRequestDescription())
                return
        
        # the user enters their project summary:
        elif (USERS[message.author.id]["status"] == 3):

            # summary cannot be empty:
            if (len(message.content.strip()) == 0):
                print(f"Sending response #3.1 to {message.author.id} ({message.author.name}).", file=sys.stderr)
                await message.channel.send(ResponseStrings.privateRequestDescription())
                return
            
            else:
                if len(message.content.strip()) > 500:
                    await message.channel.send(ResponseStrings.privateResponseTruncate(500))
                USERS[message.author.id]["summary"] = message.content.strip()[:550]
                USERS[message.author.id]["status"] = 4
                print(f"Sending response #4 to {message.author.id} ({message.author.name}).", file=sys.stderr)
                keywordsList = '\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0 '.join([f"{i})\xa0{KEYWORDS[i]}" for i in range(len(KEYWORDS))])
                await message.channel.send(ResponseStrings.privateRequestKeywords(keywordsList))
                return

        # the user enters their keywords:
        elif (USERS[message.author.id]["status"] == 4):

            numbers = list(set([int(number) for number in re.findall(r'\d+', message.content.strip())]))
            
            if (len(numbers) < 1 or len(numbers) > 3):
                print(f"Sending response #4.1 to {message.author.id} ({message.author.name}).", file=sys.stderr)
                await message.channel.send(ResponseStrings.privateResponseKeywordsNumber())
                return
            
            for number in numbers:
                if (number < 0 or number >= len(KEYWORDS)):
                    print(f"Sending response #4.2 to {message.author.id} ({message.author.name}).", file=sys.stderr)
                    await message.channel.send(ResponseStrings.privateResponseKeywordsInvalid(number))
                    return
            
            USERS[message.author.id]["keywords"] = [KEYWORDS[number] for number in numbers]
            USERS[message.author.id]["status"] = 5
            print(f"Sending response #5 to {message.author.id} ({message.author.name}).", file=sys.stderr)
            await message.channel.send(ResponseStrings.privateResponseKeywords(', '.join(USERS[message.author.id]['keywords'])))
            await message.channel.send(ResponseStrings.privateRequestSummary())
            return
            
        # the user enters their description:
        elif (USERS[message.author.id]["status"] == 5):

            # description cannot be empty:
            if (len(message.content.strip()) == 0):
                print(f"Sending response #5.1 to {message.author.id} ({message.author.name}).", file=sys.stderr)
                await message.channel.send(ResponseStrings.privateRequestSummary())
                return
            
            else:
                if len(message.content.strip()) > 1000:
                    await message.channel.send(ResponseStrings.privateResponseTruncate(1000))
                USERS[message.author.id]["description"] = message.content.strip()[:1050]
                USERS[message.author.id]["status"] = 6
                print(f"Sending response #6 to {message.author.id} ({message.author.name}).", file=sys.stderr)
                await message.channel.send(ResponseStrings.privateRequestAttempts())
                return

        # the user enters their attempts:
        elif (USERS[message.author.id]["status"] == 6):

            # attempts cannot be empty:
            if (len(message.content.strip()) == 0):
                print(f"Sending response #6.1 to {message.author.id} ({message.author.name}).", file=sys.stderr)
                await message.channel.send(ResponseStrings.privateRequestAttempts())
                return
            
            else:
                if len(message.content.strip()) > 1000:
                    await message.channel.send(ResponseStrings.privateResponseTruncate(1000))
                USERS[message.author.id]["attempts"] = message.content.strip()[:1050]
                USERS[message.author.id]["status"] = 7
                print(f"Sending response #7 to {message.author.id} ({message.author.name}).", file=sys.stderr)
                await message.channel.send(ResponseStrings.privateResponseSuccess())
                print(f"Submitted request for user {message.author.id} ({message.author.name}).", file=sys.stderr)
                # Send actual mentor request:
                request = await mentorRequestsChannel.send(ResponseStrings.mentorRequest(
                    message.author.id, 
                    USERS[message.author.id]['name'], 
                    USERS[message.author.id]['keywords'], 
                    USERS[message.author.id]['summary'], 
                    USERS[message.author.id]['description'], 
                    USERS[message.author.id]['attempts']
                ))
                USERS[message.author.id]["request"] = request.id
                return

        # their request is being processed:
        elif (USERS[message.author.id]["status"] == 7):
            await message.channel.send(ResponseStrings.privateResponseRemind())
            return
            
        else:
            print(f"Error: Invalid state", file=sys.stderr)
            return

@client.event
async def on_reaction_add(reaction, user):
    for uid in list(USERS.keys()):
        if USERS[uid]["status"] == 7 and USERS[uid]["request"] == reaction.message.id:
            # send a notification to the user that they have a mentor:
            users = await reaction.users().flatten()
            reactor = users[0].id
            await USERS[uid]["channel"].send(ResponseStrings.privateResponseAccepted(reactor))
            del USERS[uid]

client.run(TOKEN)
