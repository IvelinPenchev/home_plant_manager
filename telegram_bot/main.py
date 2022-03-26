from telegram_bot_lib import *

def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    token = json.load(open("token.json"))["telegramToken"]
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [
                MessageHandler(
                    # Filters.regex('^(Age|Favourite colour|Number of siblings)$'), regular_choice
                    Filters.regex('^Edit Plants$'), edit_plants),                
                MessageHandler(
                    Filters.regex('^Log Watering$'), log_watering),
                MessageHandler(
                    Filters.regex('^Statistics$'), start),
                MessageHandler(
                    Filters.regex('^Account settings$'), start),
            ],
            TYPING_CHOICE: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Done$')), regular_choice
                )
            ],
            TYPING_REPLY: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Done$')),
                    received_information,
                )
            ],
            CHOOSING_PLANTS: [
                MessageHandler(
                    # Filters.regex('^(Age|Favourite colour|Number of siblings)$'), regular_choice
                    Filters.regex('^List plants$'), edit_plants),                
                MessageHandler(
                    Filters.regex('^Add plants$'), add_plants),
                MessageHandler(
                    Filters.regex('^Edit a plant$'), edit_a_plant),
                MessageHandler(
                    Filters.regex('^Back$'), start),
            ],
        },
        fallbacks=[MessageHandler(Filters.regex('^Done$'), done)],
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