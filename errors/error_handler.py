from telegram import Update
from telegram.ext import CallbackContext
from ai_bot.errors.logger import setup_logger

logger = setup_logger(__name__)

async def error_handler(update: Update, context: CallbackContext) -> None:
    """Log the error and send a message to the user."""
    # Log the error
    logger.error(f"Exception while handling an update: {context.error}")
    
    # Extract error message
    error_message = str(context.error)
    
    # Categorize error
    if "Unauthorized" in error_message:
        error_type = "API Error"
        user_message = "I'm having trouble communicating with Telegram. Please try again later."
    elif "Timed out" in error_message:
        error_type = "Network Error"
        user_message = "The operation timed out. Please try again later."
    elif "Connection" in error_message:
        error_type = "Network Error"
        user_message = "I'm having connection issues. Please try again later."
    else:
        error_type = "System Error"
        user_message = "An unexpected error occurred. Our team has been notified."
    
    # Log detailed error information
    logger.error(f"Error Type: {error_type}")
    logger.error(f"Update: {update}")
    
    # Send message to user if possible
    if update and update.effective_message:
        await update.effective_message.reply_text(user_message)
