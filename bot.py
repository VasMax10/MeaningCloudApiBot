import meaning_cloud_api

from typing import Dict

from telegram import __version__ as TG_VER


try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.constants import ParseMode

from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

OPERATION, CHOOSE_LANGUAGE, CHOOSE_MODEL, WRITE_TEXT = range(4)

def facts_to_str(user_data: Dict[str, str]) -> str:
    """Helper function for formatting the gathered user info."""
    facts = [f"{key} : {value}" for key, value in user_data.items()]
    return "\n".join(facts).join(["\n", "\n"])

from tabulate import tabulate

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    """Start the conversation and ask user for input."""
    operation_step_keyboard = [[
                            "Language Identification"], [
                            "Topic Extraction"], [ 
                            "Text Classification"], [
                            "Summarization"]
                            # , [
                            # "Sentiment Analysis"], [
                            # "Text Clustering"], [ 
                            # "Corporate Reputation"], [
                            # "Document Structure Analysis"], [
                            # "Lemmatization, Pos and Parsing"]
                           ]
    
    markup = ReplyKeyboardMarkup(operation_step_keyboard, one_time_keyboard=True)
    await update.message.reply_text(
        "Hi! I am gonna help you to analyze your text. To start with, choose type of analysis you wanna apply:",
        reply_markup=markup,
    )
    
    return OPERATION

async def choose_lang(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    if "operation" in context.user_data:
        text = update.message.text
        context.user_data["model"] = text
    else:
        text = update.message.text
        context.user_data["operation"] = text
    
    print(context.user_data)

    lang_step_keyboard = [["auto", "ENG", "UKR"]]
    
    markup = ReplyKeyboardMarkup(lang_step_keyboard, one_time_keyboard=True)
    await update.message.reply_text(
        "Now let's choose a language for the text",
        reply_markup=markup,
    )
    return CHOOSE_LANGUAGE

async def choose_model(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    context.user_data["operation"] = update.message.text
    
    text = update.message.reply_text

    print(context.user_data)
    
    model_step_keyboard = [["SocialMedia", "IPTC"]]
    markup = ReplyKeyboardMarkup(model_step_keyboard, one_time_keyboard=True)

    await update.message.reply_text(
        "Now let's choose a language for the text",
        reply_markup=markup,
    )
    return CHOOSE_MODEL

async def enter_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
    if "operation" in context.user_data:
        text = update.message.text
        context.user_data["lang"] = text
    else:
        text = update.message.text
        context.user_data["operation"] = text
    
    print(context.user_data)
    
    await update.message.reply_text("Now, enter your text for analyzing:")

    return WRITE_TEXT

async def call_api(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
    
    text = update.message.text
    context.user_data['text'] = text
    
    user_data = context.user_data
    
    await update.message.reply_text(
        "Fine! Analysis will be done as soon as possible. Please wait! Your entered data: \n"
        f"{facts_to_str(user_data)}"
    )

    if user_data['operation'] == 'Summarization':
        result = meaning_cloud_api.summarization(user_data['text'], 5)
        await update.message.reply_text(result)
        return ConversationHandler.END
    elif user_data['operation'] == 'Text Classification':
        result = meaning_cloud_api.text_classification(user_data['model'], user_data['lang'], user_data['text'])
    elif user_data['operation'] == 'Topic Extraction':
        result = meaning_cloud_api.topic_extraction(user_data['lang'], user_data['text'])
    elif user_data['operation'] == 'Language Identification':    
        result = meaning_cloud_api.language_identification(user_data['text'])
    
    

    

    text = tabulate(result, headers='firstrow', tablefmt='orgtbl')

    await update.message.reply_text(f"<pre>{text}</pre>", parse_mode=ParseMode.HTML)

    return ConversationHandler.END


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Display the gathered info and end the conversation."""
    user_data = context.user_data
    if "choice" in user_data:
        del user_data["choice"]

    await update.message.reply_text(
        f"I learned these facts about you: {facts_to_str(user_data)}Until next time!",
        reply_markup=ReplyKeyboardRemove(),
    )

    user_data.clear()
    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    application = Application.builder().token("6209707155:AAFEKVl39j9QFVH4nxpLCjyzZ0AKSjrfjcw").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            OPERATION: [
                MessageHandler(
                    filters.Regex("^(Topic Extraction|Sentiment Analysis|Corporate Reputation|Document Structure Analysis)$"), choose_lang
                ),
                MessageHandler(
                    filters.Regex("^(Text Classification)$"), choose_model
                ),
                MessageHandler(
                    filters.Regex("^(Language Identification|Text Clustering|Lemmatization, Pos and Parsing|Summarization)$"), enter_text
                )
            ],
            CHOOSE_LANGUAGE: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")), enter_text
                )
            ],
            CHOOSE_MODEL: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")), choose_lang
                )
            ],
            WRITE_TEXT: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")),
                    call_api,
                )
            ],
        },
        fallbacks=[MessageHandler((filters.Regex("^Done$") | filters.COMMAND), done)],
    )

    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == "__main__":
    main()