#!/home/lama/miniconda3/envs/tg_bot/bin/python
import logging

import httpx
import hydra
from omegaconf import DictConfig

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from todoist_api_python.api_async import TodoistAPIAsync

from winged_scapula_span_bot.helper.todoist import upload_image

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Create task from message."""
    api = TodoistAPIAsync(context.bot_data.get("todoist_token"))
    try:
        text = update.message.text or ""
        text += update.message.caption or ""
        task_name = text.split('\n')[0][:100]

        text_md = update.message.text_markdown_v2_urled or ""
        text_md += update.message.caption_markdown_v2_urled or ""

        task = await api.add_task(
            content=f"tg: {task_name}",
            description=f"{text_md}\n"
                        f"chat: {update.message.chat}\n,"
                        f"message: {update.message.message_id}\n,"
                        f"forward from chat: {update.message.forward_from_chat},"
                        f"forward from message: {update.message.forward_from_message_id},"
                        f"date: {update.message.date}"
        )

        if update.message.photo:
            photo_size = update.message.photo[-1]
            file = await photo_size.get_file()
            file_bytes = await file.download_as_bytearray()
            response = await upload_image(
                f"{photo_size.file_id}.jpg",
                file_bytes,
                context.bot_data.get('todoist_token')
            )

            if response.status_code == httpx.codes.OK:
                content = photo_size.file_id
                attachment_data = {
                    "file_url": response.json()["file_url"],
                    "file_type": "image/jpeg",
                    "file_name": f"{photo_size.file_id}.jpg",
                }
                await api.add_comment(
                    content=content,
                    task_id=task.id,
                    attachment=attachment_data
                )
            else:
                raise ValueError(f"🫡 {task.url}; but image haven\"t attached: {response}")

        logger.info(f"Added task: {task.url}")
        await update.message.reply_text(f"🫡 {task.url}")
    except Exception as error:
        logger.error(error, exc_info=True)
        await update.message.reply_text(repr(error))


@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(cfg: DictConfig) -> None:
    """Start the bot."""
    # Create the Application and pass it your bot"s token.
    application = Application.builder().token(cfg["tg"]["token"]).build()
    todoist_token = cfg["todoist"]["token"]
    application.bot_data["todoist_token"] = todoist_token

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    msg_handler = MessageHandler(~filters.COMMAND, echo)
    application.add_handler(msg_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
