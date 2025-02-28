from telegram.ext import Application, MessageHandler, filters, CallbackContext, ConversationHandler
from telegram import Update
from ai_bot.database.database import db_session
from ai_bot.users.user_model import get_user, update_user_activity
from ai_bot.books.book_model import process_book_file
from ai_bot.errors.logger import setup_logger

logger = setup_logger(__name__)

async def handle_document(update: Update, context: CallbackContext) -> None:
    """Handle document uploads (books)"""
    user = update.effective_user
    telegram_id = str(user.id)
    
    # Check if user exists
    db_user = get_user(db_session, telegram_id)
    if not db_user:
        await update.message.reply_text(
            "You need to register first. Use /register [timezone] to create an account."
        )
        return
    
    # Update user activity
    update_user_activity(db_session, telegram_id)
    
    document = update.message.document
    file_name = document.file_name
    
    # Check if it's a supported file type
    supported_extensions = ['.pdf', '.epub', '.mobi', '.txt']
    is_supported = any(file_name.lower().endswith(ext) for ext in supported_extensions)
    
    if not is_supported:
        await update.message.reply_text(
            "Sorry, this file type is not supported. Please upload a PDF, EPUB, MOBI, or TXT file."
        )
        return
    
    await update.message.reply_text(
        f"I've received your book: {file_name}\n"
        f"I'll start processing it now. This may take a few minutes depending on the size.\n"
        f"I'll notify you when it's ready."
    )
    
    # Download the file
    file = await context.bot.get_file(document.file_id)
    file_bytes = await file.download_as_bytearray()
    
    # Process the book file
    book = process_book_file(db_session, db_user.id, telegram_id, file_bytes, file_name)
    
    if book:
        await update.message.reply_text(
            f"Your book has been processed successfully!\n"
            f"Title: {book.title}\n"
            f"Chapters: {book.processed_chapters}\n"
            f"Book ID: {book.id}\n\n"
            f"You can now use commands like /summary {book.id} or /schedule {book.id} to work with this book."
        )
    else:
        await update.message.reply_text(
            f"There was an error processing your book. Please try again or try a different file."
        )

async def handle_text(update: Update, context: CallbackContext) -> None:
    """Handle text messages"""
    user = update.effective_user
    telegram_id = str(user.id)
    
    # Check if user exists
    db_user = get_user(db_session, telegram_id)
    if not db_user:
        await update.message.reply_text(
            "You need to register first. Use /register [timezone] to create an account."
        )
        return
    
    # Update user activity
    update_user_activity(db_session, telegram_id)
    
    # For now, just echo back a simple response
    await update.message.reply_text(
        "I'm designed to work with commands and book files. Try /help to see what I can do!"
    )

def register_message_handlers(application: Application):
    """Register all message handlers"""
    application.add_handler(MessageHandler(filters.DOCUMENT, handle_document))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    logger.info("Message handlers registered")
