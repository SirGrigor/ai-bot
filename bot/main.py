import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import os
from dotenv import load_dotenv
from ai_bot.database.database import init_db
from ai_bot.bot.command_handler import register_command_handlers
from ai_bot.bot.message_router import register_message_handlers
from ai_bot.errors.logger import setup_logger
from ai_bot.errors.error_handler import error_handler

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logger(__name__)

async def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        f"Hi {user.mention_html()}! I'm your Book Retention Bot. I'll help you process, analyze, and create spaced repetition learning schedules for books.\n\n"
        f"Use /register [timezone] to set up your account with your timezone preference.\n"
        f"For example: /register UTC or /register America/New_York\n\n"
        f"Type /help to see all available commands."
    )

async def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    help_text = """
*Book Retention Bot Commands*

*User Management*
/start - Get started with the bot
/register [timezone] - Create user account with timezone preference
/preferences - Set notification times, content depth preferences

*Book Management*
/browse [category] - View curated books by category
/search [query] - Find specific books by title/author
/add [title] [author] - Manually add a book
/upload - Upload book file (PDF, EPUB, etc.)
/mybooks - View books in progress/completed

*Book Analysis*
/summary [book_id] - Receive AI-generated book overview
/concepts [book_id] - Get key takeaways as bullet points
/estimate [book_id] - Show reading and learning time estimates

*Learning Schedule*
/schedule [book_id] - Set up learning schedule
/pause [book_id] - Temporarily pause schedule
/resume [book_id] - Resume paused schedule

*Spaced Repetition*
/recap [book_id] - Core concept reminders (Day 1)
/connect [book_id] - Concept connections (Day 3)
/apply [book_id] - Application prompts (Day 7)
/master [book_id] - Comprehensive review (Day 30)

*Interactive Learning*
/quiz [book_id] - Get multiple-choice questions
/explain [concept] - Free text response to concept
/progress [book_id] - View question completion stats
/teach [concept] - Get prompts to explain concept
/improve [concept] - Get suggestions to improve explanation

*Analytics*
/stats [book_id] - View personal retention metrics
/compare [book_id1] [book_id2] - Compare learning across books
/export [book_id] [format] - Export notes and insights

*Other Commands*
/status - Current progress across all books
/skip [concept] - Move to next concept
/restart [book_id] - Begin book from scratch
/feedback [text] - Submit user feedback
"""
    await update.message.reply_markdown(help_text)

def main() -> None:
    """Start the bot."""
    # Initialize database
    init_db()
    
    # Create the Application
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        logger.error("No TELEGRAM_TOKEN found in environment variables")
        return
        
    application = Application.builder().token(token).build()

    # Register basic handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # Register all command handlers
    register_command_handlers(application)
    
    # Register message handlers
    register_message_handlers(application)
    
    # Register error handler
    application.add_error_handler(error_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == '__main__':
    main()
