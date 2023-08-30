# from types import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.ext import ExtBot

from aiogram import Bot, Dispatcher, types


import queue

import random
import time

import threading
import asyncio

loop = asyncio.get_event_loop()

TOKEN = '6614265216:AAHyKsrRP06uHLAqspGMu_x1nmEOkDapCNM'
BOT_USERNAME = '@Monk_Roulette_bot'

bot_instance = Bot(token=TOKEN)
dispatcher = Dispatcher(bot_instance)

current_batch_bets = []
context_queue = queue.Queue()
betting_users = set()  # Set to store users who have placed bets in the current cycle
users_with_bets = {}


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type == 'private':
        await update.message.reply_text("Please use the bot in a group chat.")
    else:
        await update.message.reply_text('Hello! Thanks for chatting with me! I am Roulette bot!')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type == 'private':
        await update.message.reply_text("Please use the bot in a group chat.")
    else:
        await update.message.reply_text('Please type something so I can respond')

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type == 'private':
        await update.message.reply_text("Please use the bot in a group chat.")
    else:
        await update.message.reply_text('This is a custom command')

async def bet_command(update:Update, context:ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user.username
    if user in users_with_bets:
        await update.message.reply_text("You have already placed a bet in this batch. Please wait for the next batch.")
        return
    
    
    await update.message.reply_text('Please enter the number of coins foolwed by betting colour after space')
    users_with_bets[user] = True

#Responses

def handle_response(text: str) -> str:
    global current_batch_bets
    processed: str = text.lower()

    current_batch_bets.append(processed)




    if 'hello' in processed:
        return 'Hey There!'
    
    if 'how are you' in processed:
        return 'I am good!'

    if 'i love python' in processed:
        return 'Remember to unsubscribe!'
    
    return 'I do not understand what you wrote... '


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type == 'group' or update.message.chat.type == 'supergroup':
        try:
            user = update.message.from_user.username

            if any(bet['user']==user for bet in current_batch_bets):
                print(user,'user')
                await update.message.reply_text("You've already placed a bet in this cycle. Please wait for the next cycle to place another bet.")
                return
            
            tokens, choice = update.message.text.split(' ')
            tokens = int(tokens)
            
            print(tokens, choice)

            if choice not in ['red', 'black', 'green']:
                raise ValueError
            betting_users.add(user)
            current_batch_bets.append({'user': update.message.from_user.username, 'tokens': tokens, 'choice': choice})

            # print(current_batch_bets[0])
            await update.message.reply_text(f"Your bet of {tokens} tokens on {choice} has been registered!")
            context.bot_data['chat_id'] = update.message.chat_id
            context_queue.put(context)
        except ValueError:
            await update.message.reply_text("Invalid input format. Please enter in the format: <tokens> <choice>.")

# def polling(context: CallbackContext):
#     """Polling function that runs every 5 minutes to determine bet outcomes"""
#     while True:
#         time.sleep(60)  # Sleep for 5 minutes
#         pattern = random.choice(['red', 'black', 'green'])
#         for bet in current_batch_bets:
#             if bet['choice'] == pattern:
#                 context.bot.send_message(chat_id=bet['user'], text=f"You win! The pattern was {pattern}.")
#             else:
#                 context.bot.send_message(chat_id=bet['user'], text=f"You lose! The pattern was {pattern}.")
#         current_batch_bets.clear()


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')
def process_bets_thread():
    # bot_instance = ExtBot(token=TOKEN)
    while True:
        context = context_queue.get()
        # print(context,'heelo')
        process_bets(context, bot_instance)
        time.sleep(60)

def process_bets(context: ContextTypes.DEFAULT_TYPE, bot:ExtBot):
        global current_batch_bets
        # group_chat_id = context.update.message.chat_id
        # print('12hello')
        outcome_color = random.choice(["Red", "Black", "Green"])

        print(outcome_color)
        results = []

        for bet in current_batch_bets:
            tokens = bet['tokens']
            bet_type = bet['choice']
            user = bet['user']
            print('heelo',tokens,bet_type)
            win = False

            if (bet_type == "red" and outcome_color == "Red") or \
            (bet_type == "black" and outcome_color == "Black") or \
            (bet_type == "green" and outcome_color == "Green"):
                win = True
            print('win', win)

            if win:
                if bet_type == "green":
                    payout = 14.0
                else:
                    payout = 2.0  # Even money payout for colors
                reward = tokens * payout
                result_text = f"Win! {user} won {reward:.2f} tokens."
            else:
                reward = -tokens
                result_text = f"Lose. {user} lost {tokens:.2f} tokens."

            results.append(result_text)
            print('results text', result_text)

        # Send messages with results to the group
        results_text = "\n".join(results)
        
        chat_id = context.bot_data['chat_id']
        print('chatid', chat_id)
        # try:
        #     bot.send_message(chat_id=chat_id, text=results_text)
        # except Exception as e:
        #     print("Error sending message:", e)
        if(results_text):
            asyncio.run(send_results_async(chat_id, results_text))
        print('everything')
        # Clear current batch bets for the next round
        current_batch_bets = []
        betting_users.clear()
        users_with_bets.clear()

async def send_results_async(chat_id, results_text):
    await bot_instance.send_message(chat_id=chat_id, text=results_text)
      

def main():
    print('Starting bot...')
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))
    app.add_handler(CommandHandler('bet', bet_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Process Bets
    # app.add_scheduled_job(process_bets, interval=30)

    

    # Errors
    app.add_error_handler(error)

    # asyncio.create_task(process_bets(context=app))
    # context_queue = queue.Queue()

    # Polls the bot
    process_bets_thread_obj = threading.Thread(target=process_bets_thread)
    process_bets_thread_obj.start()
    print('Polling...')
    app.run_polling(poll_interval=3)
    print('after pollig')
# Define a timestamp to keep track of when to process bets
    # last_processed_time = time.time()

    # while True:
    #     # Check if it's time to process bets (e.g., every 1 minute)
    #     process_bets(None,None)
    #     time.sleep(60)
          # Adjust the sleep time as needed
    # schedule.every(1).minutes.do(process_bets)
    # print('afte schedule')
    # while True:
    #     print('werth')
    #     schedule.run_pending()
    #     time.sleep(1)  # Adjust the sleep time as needed


    # while True:
    #     print('Running process_bets...')
    #     process_bets(None)  # Pass a dummy context or None
    #     time.sleep(60)  # Run every 60 seconds    


if __name__ == '__main__':
    main()