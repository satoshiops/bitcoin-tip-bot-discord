# Main execution file
# This file contains all function definitions for the tip bot
import helpers
import currency_mongo
import discord
import random

token_file = open("./private_data/token.txt", "r")
server_id_file = open("./private_data/my_server_id.txt", "r")

server_id = int(server_id_file.read())

token = token_file.read()
permissions = 67584

tipbot_name = "bad-lab-tipbot"

# add_to_server_url = f"https://discordapp.com/oauth2/authorize?client_id={client_id}&scope=bot&permissions={permissions}"

# Initialize Discord client and MongoDB connection
client = discord.Client()
'''
Absolutely not necessary, but it's a lot of fun - the array
and boolean below will send a gif whenever someone is tipped.
'''
tip_gifs = [
	"https://media.giphy.com/media/l3q2wJsC23ikJg9xe/giphy.gif",
	"https://media.giphy.com/media/BYoRqTmcgzHcL9TCy1/giphy.gif",
	"https://media.giphy.com/media/I1WiaoKFdWcpaAp1Z7/giphy.gif",
	"https://media.giphy.com/media/h0MTqLyvgG0Ss/giphy.gif",
	"https://media.giphy.com/media/3kD49hW8Cpz92rpJxX/giphy.gif",
	"https://media.giphy.com/media/eewYSr7s7utOM/giphy.gif",
	"https://media.giphy.com/media/69v2l3Mx3VHZY2MTmO/giphy.gif",
	"https://media.giphy.com/media/ZO8z7Pb7R08b4EZuYH/giphy.gif",
	"https://media.giphy.com/media/8qgKKgu42TYZP93Z4u/giphy.gif",
	"https://media.giphy.com/media/7RDFd7vrISPu0/giphy.gif",
	"https://media.giphy.com/media/l41lR76EVnUedm40g/giphy.gif",
	"https://media.giphy.com/media/MFsqcBSoOKPbjtmvWz/giphy.gif"
]

show_tip_gif = True

'''
 If the user has at least this many satoshis, we message them to let
them know. This is so our users know that they are starting to hold a
large amount of sats in their wallet
'''
MAX_SATS_HELD = 750000

@client.event 	# decorator/wrapper
async def on_ready():
    pass

# Handle any messages sent on the server
@client.event
async def on_message(message):
    mongo_currency = currency_mongo.Currency()
    # print(f"{message} : #{message.channel} : {message.author} : {message.content}")
    helpers.log(message)
    member_id = message.author.id
    member_name = message.author.name
    server_id = ''
    server_name = ''
    is_direct_message = True

    if message.guild and message.guild.id:
        is_direct_message = False
        server_id = message.guild.id
        server_name = message.guild.name

    if "!btctip" not in message.content:
        return

    helpers.log(
        f"\n-> message: {message.content} |||| server_id: {server_id} | server_name: {server_name} | member_id: {member_id} | member_name: {member_name}\n")

    mongo_currency.check(server_id, server_name, member_id, member_name)

    if "!btctip balance" in message.content.lower() and message.author.name != tipbot_name:
		# Balance is personal info - send to the user via DM instead of to the channel
        bal = mongo_currency.get_balance(member_id)
        # await message.channel.send("Hey we just DM'd you!")
        await message.author.send(f"Your tip wallet has {bal} sats")
        return
    elif "!btctip help" in message.content.lower() and message.author.name != tipbot_name:
        await message.author.send("I'm a Bitcoin bot you can use to tip bad-lab members Bitcoin via the Lightning Network.\n\nHere's a list of what I can do:\n\nTo tip someone: `!btctip <@username> <amt-in-sats>` - will tip a recipient Bitcoin via the LN.\nFor example: `!btctip @satoshiops#2798 50`.\nThis will tip 50 sats from your wallet to satoshiop's wallet.\n\nTo see your balance: `!btctip balance`. This will send you a DM with your balance in your tipping wallet, in sats.\n\nTo withdraw your balance: `!btctip withdraw <invoice>`. Make sure you paste in a Lightning Network invoice! Most of the time they start with `lnbc`.\n\nTo deposit sats into your tipping wallet: `!btctip deposit <amount in sats>`.\nFor example, running `!btctip deposit 2000` will generate an invoice on the lightning network that you can pay to. These sats will then go into your tipping wallet. Please note it may take up to 1 minute for your balance to update via our database.\n\nGot any questions? Ask one of the mods and we'll be happy to help!")
        return

    elif "!btctip withdraw" in message.content.lower() and message.author.name != tipbot_name:
        try:
            withdrawer_id = member_id
            withdrawer_name = member_name

            words = message.content.lower().split(' ')
            for i in range(len(words)):
                if words[i] == "!btctip" and words[i+1] == "withdraw":
                    pay_req = words[i+2]
                    break
                    # not returning if invalid after invoke command cuz it raises exception and program goes on

            #result = mongo_currency.get_amount_from_payreq(pay_req)
            result_message = mongo_currency.withdraw_pay_invoice(
                server_id, server_name, withdrawer_id, withdrawer_name, pay_req)

            await message.author.send(result_message)

        except Exception as e:
            helpers.log(e, 'error')
            await message.author.send("Sorry, there was an error on our end. Please try again. If the issue persists, please DM one of the mods!")
            return

    elif "!btctip deposit" in message.content.lower() and message.author.name != tipbot_name:
        try:

            depositor_id = member_id
            depositor_name = member_name

            words = message.content.lower().split(' ')
            for i in range(len(words)):
                if words[i] == "!btctip" and words[i+1] == "deposit":
                    amount = words[i+2]
                    break
                    # not returning if invalid after invoke command cuz it raises exception and program goes on

            invoice = mongo_currency.deposit_get_payreq(
                server_id, server_name, depositor_id, depositor_name, amount)

			# Create QR code of invoice as well
            invoiceQr = helpers.invoice_to_qrcode(invoice)
            await message.author.send(f"Please send your sats to this invoice:\n\n{invoice}\n\nFeel free to scan the QR code below as well instead of copy/pasting")
            await message.author.send(file=discord.File(fp=invoiceQr, filename="image.png"))

        except Exception as e:
            helpers.log(e, 'error')
            await message.author.send("Sorry, there was an error on our end. Please try again. If the issue persists, please DM one of the mods!")
            return

    elif "!btctip" in message.content.lower() and message.author.name != tipbot_name:
        try:
            words = message.content.lower().split(' ')

            for i in range(len(words)):
                if words[i] == "!btctip":
                    recipient = words[i+1]
                    amount = words[i+2]
                    if amount == '':  # sometimes mentioning user adds another empty char which could fuck things up so I'm removing any empty chars registered as words
                        amount = words[i+3]
                    break
                    # not returning if invalid after invoke command cuz it raises exception and program goes on

            sender_id = member_id
            sender_name = member_name

            if '!' in recipient:  # desktop client
                recipient_id = int(recipient.split('!')[1][: -1])
            else:  # mobile client
                recipient_id = int(recipient.split('@')[1][: -1])

            recipient_name = await client.fetch_user(recipient_id)
            recipient_name = str(recipient_name).split('#')[0]

            mongo_currency.check(server_id, server_name,
                                 recipient_id, recipient_name)

            helpers.log(
                f"sender_name = {sender_name} | sender_id = {sender_id} | recipient_name = {recipient_name} | recipient_id = {recipient_id}")

            if int(amount) <= 0:
                await message.author.send("You can't send negative sats!")
                return

            if sender_id == recipient_id:
                await message.author.send("You can't tip yourself!")
                return

            result = mongo_currency.send_money(sender_id, recipient_id, amount)

            if result == "not enough balance":
                await message.author.send("Hey there! We tried to send your payment but you don't have enough sats!")
                return

            if result:
                await message.channel.send(f"Check it out! <@{sender_id}> just sent {amount} sats to <@{recipient_id}>!")
                
                if show_tip_gif:
                    await message.channel.send(random.choice(tip_gifs))

                receiver_bal = mongo_currency.get_balance(recipient_id)
                if(receiver_bal >= MAX_SATS_HELD):
                    ""
                    print("Send DM to recipient here!")
            else:
                await message.channel.send(f"problem: {result}")

        except Exception as e:
            helpers.log(e, 'error')
            await message.channel.send("ay check again")

client.run(token)