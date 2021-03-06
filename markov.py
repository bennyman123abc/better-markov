#
# markov.py -
# markov chain bot that uses yamamura logfiles as input
#

# import the needed modules
from discord.ext.commands import Bot
import re, markovify, discord, json
import multiprocessing as mp

# load config file, exit if not found
cfg = None
try:
    with open("config.json", "r") as cfgFile:
        cfg = json.load(cfgFile)
except FileNotFoundError:
    print(
        'copy "config.example.json", rename it to "config.json and edit it before running this bot'
    )

# the thing that fixes mentions
class squeaky:

    # quick workaround for passing
    # context
    def __init__(self, message):

        # set the context
        self.message = message

    # whem this class is called
    def __call__(self, match):

        # really quick and dirty workaround
        try:

            # attempt to get length
            len(match)

        except:

            # group them
            match = match.group(0)

        # getting uid
        try:

            # get the uid
            uid = int(match[2:(len(match) - 1)])

        except:

            try:

                # some are like this
                uid = int(match[3:(len(match) - 1)])

            except:

                # otherwise, return
                return match

        try:

            # look it up
            return self.message.server.get_member(uid).name

        except:

            # it might be a role
            for role in self.message.server.roles:

                # check if it is here
                if role.id == uid:

                    # return the role name
                    return role.name

            # otherwise, return uid
            return str(uid)

# the function we use to spool writes to the logfile
def spooler(queue):

    # load the log file
    with open("chat.log", "a") as f:

        # loop to constantly write lines to the file
        while True:

            # get a message to write from the queue
            message = queue.get()

            # write the message
            f.write(message)


# create the bot object
bot = Bot(description="that one markov chain bot", command_prefix="m~")

chain = None

@bot.event
async def on_ready():

    # print some output
    print(
        f"logged in as: { bot.user.name } id:{ bot.user.id } | connected to { str(len(bot.servers)) } server(s)"
    )
    print(
        f"invite: https://discordapp.com/oauth2/authorize?bot_id={ bot.user.id }&scope=bot&permissions=8"
    )
    await bot.change_presence(game=discord.Game(name="scanning your text..."))

    # make the chain

    # extracted text from file variable
    extracted_text = ""

    # load the log file
    with open("chat.log", "r") as f:

        # extract all text from it
        extracted_text = f.read()

    # save the extracted text to a markov chain
    global chain
    chain = markovify.NewlineText(extracted_text)

@bot.event
async def on_message(message):
    if message.content.startswith("m~"):
        print("Got command!")
        print(message.content)
        args = message.content.split()
        print(args)
        cmd = args[0].replace("m~", '')
        print(cmd)
        args = args.remove(args[0])

        if cmd == "markov":
            await markov(message, args)

    elif not message.content.startswith("m~") and not message.author.bot:
        with open("chat.log", "a") as f:
            # write the message
            f.write(message.content + "\n")
            f.close()




# the only command

# @bot.command()
async def markov(message, args):
    print("1")
    # global copy
    global chain
    print("2")
    # make the sentence variable
    sentence = None

    while sentence == None:
        print("3")
        # make a sentence
        sentence = chain.make_sentence(tries=250)

    # check if we have arguments
    # if args != None:

    #     # make a sentence
    #     while sentence == None:

    #         # make a sentence
    #         sentence = chain.make_sentence(tries=250)

    # else:

    #     # make a variable for the
    #     # to-be-sent message
    #     sentence = ""

    #     # individual sentence var
    #     isentence = None

    #     # make a variable for the
    #     # number of sentences we
    #     # have constructed
    #     x = 1

    #     # check if the arg is a valid
    #     # int
    #     try:

    #         # check
    #         iters = int(args[0])

    #         # tell them if it is definitely too big
    #         if iters >= 50:

    #             # send a message
    #             # await ctx.send(f"{ ctx.author.mention }, that number of sentences is definitely way too high!")
    #             await bot.send_message(message.channel.id, f"<@{ message.author.id }>, that number of sentences is definitely way too high!")

    #             # exit
    #             return

    #     except ValueError:

    #         # respond saying it isn't valid
    #         # await ctx.send(f"{ args[0] } is not a number...")
    #         await bot.send_message(message.channel.id, f"{ args[0] } is not a number...")

    #         # exit
    #         return

    #     # now construct the message
    #     for x in range(iters):

    #         # make sure we have a message
    #         while isentence == None:

    #             # make the message
    #             isentence = chain.make_sentence(tries=250)

    #         # if it works, append the message to the
    #         # full message
    #         sentence += ("%s\n" % isentence)

    #         # reset the isentence variable
    #         isentence = None

    # make the message squeaky clean
    print("4")
    sentence = re.sub(r"\<\@(.*?)\>", squeaky(message), sentence, flags=re.IGNORECASE)

    # remove the @everyones and @heres
    sentence = re.sub(r"\@everyone", "everyone", sentence, flags=re.IGNORECASE)
    sentence = re.sub(r"\@here", "here", sentence, flags=re.IGNORECASE)

    try:

        # send it
        # await ctx.send(sentence)
        print(f"Sentence: { sentence }")
        await bot.send_message(message.channel, sentence)

    except discord.errors.HTTPException:

        # send an error message
        # await ctx.send(f"{ ctx.author.mention }, sorry, but the message generated was too long...")
        await bot.send_message("Sorry, but the message generated was too long!")


# run the bot
bot.run(cfg["token"])
