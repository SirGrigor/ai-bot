from telegram.ext import Application, CommandHandler, CallbackContext
from telegram import Update
from ai_bot.database.database import db_session
from ai_bot.users.user_model import get_user, create_user, update_user_preferences
from ai_bot.books.book_model import create_book, get_user_books, get_book, get_book_chapters
from ai_bot.errors.logger import setup_logger
import pytz

logger = setup_logger(__name__)

async def register_command(update: Update, context: CallbackContext) -> None:
    """Register a new user with timezone"""
    user = update.effective_user
    telegram_id = str(user.id)
    
    # Check if user already exists
    db_user = get_user(db_session, telegram_id)
    
    # Get timezone from command arguments
    timezone = 'UTC'  # Default timezone
    if context.args and len(context.args) > 0:
        requested_timezone = context.args[0]
        try:
            pytz.timezone(requested_timezone)
            timezone = requested_timezone
        except pytz.exceptions.UnknownTimeZoneError:
            await update.message.reply_text(
                f"Invalid timezone: {requested_timezone}. Using UTC instead.\n"
                f"Please see https://en.wikipedia.org/wiki/List_of_tz_database_time_zones for valid timezones."
            )
    
    if db_user:
        # Update existing user
        db_user = update_user_preferences(db_session, telegram_id, timezone=timezone)
        await update.message.reply_text(
            f"Your account has been updated with timezone: {timezone}"
        )
    else:
        # Create new user
        db_user = create_user(
            db_session,
            telegram_id=telegram_id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            timezone=timezone
        )
        await update.message.reply_text(
            f"Welcome! Your account has been created with timezone: {timezone}\n\n"
            f"You can now use the bot to manage your books and learning schedules.\n"
            f"Try uploading a book with /upload or adding one manually with /add [title] [author]"
        )

async def preferences_command(update: Update, context: CallbackContext) -> None:
    """Set user preferences"""
    user = update.effective_user
    telegram_id = str(user.id)
    
    # Check if user exists
    db_user = get_user(db_session, telegram_id)
    if not db_user:
        await update.message.reply_text(
            "You need to register first. Use /register [timezone] to create an account."
        )
        return
    
    # For now, just show current preferences
    await update.message.reply_text(
        f"Your current preferences:\n"
        f"- Timezone: {db_user.timezone}\n"
        f"- Notification time: {db_user.notification_time}\n"
        f"- Notifications enabled: {'Yes' if db_user.notification_enabled else 'No'}\n\n"
        f"To change your timezone, use /register [timezone]\n"
        f"More preference settings will be available soon."
    )

async def add_book_command(update: Update, context: CallbackContext) -> None:
    """Add a book manually"""
    user = update.effective_user
    telegram_id = str(user.id)
    
    # Check if user exists
    db_user = get_user(db_session, telegram_id)
    if not db_user:
        await update.message.reply_text(
            "You need to register first. Use /register [timezone] to create an account."
        )
        return
    
    # Check if command has enough arguments
    if not context.args or len(context.args) < 1:
        await update.message.reply_text(
            "Please provide a book title. Usage: /add [title] [author]"
        )
        return
    
    # Extract title and author
    if len(context.args) == 1:
        title = context.args[0]
        author = None
    else:
        title = context.args[0]
        author = ' '.join(context.args[1:])
    
    # Create book
    book = create_book(db_session, db_user.id, title, author)
    
    await update.message.reply_text(
        f"Book added: {title}" + (f" by {author}" if author else "") + "\n"
        f"Book ID: {book.id}\n\n"
        f"Since this book was added manually, you'll need to upload content or add notes later."
    )

async def my_books_command(update: Update, context: CallbackContext) -> None:
    """List user's books"""
    user = update.effective_user
    telegram_id = str(user.id)
    
    # Check if user exists
    db_user = get_user(db_session, telegram_id)
    if not db_user:
        await update.message.reply_text(
            "You need to register first. Use /register [timezone] to create an account."
        )
        return
    
    # Get user's books
    books = get_user_books(db_session, db_user.id)
    
    if not books:
        await update.message.reply_text(
            "You don't have any books yet. Use /add [title] [author] to add a book manually, "
            "or upload a book file."
        )
        return
    
    # Format book list
    book_list = "Your books:\n\n"
    for book in books:
        book_list += f"ID: {book.id} - {book.title}" + (f" by {book.author}" if book.author else "") + "\n"
        book_list += f"Status: {book.processing_status.capitalize()}\n"
        book_list += f"Chapters: {book.processed_chapters}/{book.total_chapters}\n\n"
    
    await update.message.reply_text(book_list)

def register_command_handlers(application: Application):
    """Register all command handlers"""
    application.add_handler(CommandHandler("register", register_command))
    application.add_handler(CommandHandler("preferences", preferences_command))
    application.add_handler(CommandHandler("add", add_book_command))
    application.add_handler(CommandHandler("mybooks", my_books_command))
    
    # TODO: Add more command handlers
    
    logger.info("Command handlers registered")
