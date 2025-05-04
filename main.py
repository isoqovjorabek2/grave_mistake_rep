import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# Set up logging for the bot
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Bot token for accessing Telegram Bot API
BOT_TOKEN = '8001531016:AAFduxJ276zPQ-o9i09Hbq9DZ9DEDrFW-zQ'

# Handler for processing the received photo
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get the highest resolution photo
    photo = update.message.photo[-1]
    file = await photo.get_file()

    # Set up the input directory and file path
    input_dir = "downloads"
    os.makedirs(input_dir, exist_ok=True)
    input_path = f"{input_dir}/{file.file_id}.jpg"
    out_path ='output/result.png'

    # Check if the file already exists and delete it if it does
    if os.path.isfile(input_path):
        os.remove(input_path)

    # Download the photo to the server
    await file.download_to_drive(input_path)

    # Notify the user that the image is being processed
    await update.message.reply_text("Image received. Sending back the image...")

    try:
        # Simply send back the received image without any processing
        with open(out_path, 'rb') as image_file:
            await update.message.reply_photo(photo=image_file)

    except Exception as e:
        # Log any error during processing and notify the user
        logging.exception("Error during image processing")
        await update.message.reply_text("Oops. Something went wrong while processing the image.")

# Main function to start the Telegram bot
def main():
    # Create the bot application
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Add a handler for receiving photos
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Start polling to check for new messages
    app.run_polling()

if __name__ == '__main__':
    main()
