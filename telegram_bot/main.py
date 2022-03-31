from telegram_bot_lib import *

def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    token = json.load(open("token.json"))["telegramToken"]
    updater = Updater(token)

    bot = TelegramBot()
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', bot.start)],
        states={
            bot.CHOOSING: [
                MessageHandler(
                    # Filters.regex('^(Age|Favourite colour|Number of siblings)$'), regular_choice
                    Filters.regex('^Your Plants$'), bot.your_plants),                
                MessageHandler(
                    Filters.regex('^Log Watering$'), bot.log_watering),
                MessageHandler(
                    Filters.regex('^Statistics$'), bot.start),
                MessageHandler(
                    Filters.regex('^Account settings$'), bot.start),
            ],
            bot.TYPING_CHOICE: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Done$')), bot.regular_choice
                )
            ],
            bot.TYPING_REPLY: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Done$')),
                    bot.received_information,
                )
            ],
            bot.CHOOSING_PLANTS: [
                MessageHandler(
                    # Filters.regex('^(Age|Favourite colour|Number of siblings)$'), regular_choice
                    Filters.regex('^List plants$'), bot.list_plants),                
                MessageHandler(
                    Filters.regex('^Add plants$'), bot.add_plants),
                MessageHandler(
                    Filters.regex('^Edit a plant$'), bot.edit_a_plant),
                MessageHandler(
                    Filters.regex('^Delete a plant$'), bot.delete_a_plant),
                MessageHandler(
                    Filters.regex('^Back$'), bot.start),
            ],
        },
        fallbacks=[MessageHandler(Filters.regex('^Done$'), bot.done)],
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
    # url_1 = "http://127.0.0.2:8080/plants/add_plant?chat_id=12345678"
    # url_2 = "http://127.0.0.2:8080/plants/getlastid?chat_id=123456789"
    # url_3 = "http://127.0.0.2:8080/plants/delete_plant?chat_id=52417371450&plant_id=1"

    # j = {
    #         "id": "6",
    #         "plant species": "pothos",
    #         "plant nickname": "pothos1112",
    #         "room": "kitchen",
    #         "watered": []
    #     }

    # # r = requests.post(url_1, json = j)
    # r = requests.delete(url_3)
    # print(r.text)
