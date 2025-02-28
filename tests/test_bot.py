import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from telegram import Update, User, Message, Chat, Document
from telegram.ext import Application, CommandHandler
from bot.main import start, help_command
from bot.command_handler import register_command, preferences_command
from bot.message_router import handle_document, handle_text

@pytest.fixture
def mock_update():
    user = MagicMock(spec=User)
    user.id = 12345
    user.username = "test_user"
    user.first_name = "Test"
    user.last_name = "User"
    user.mention_html.return_value = "<a href='tg://user?id=12345'>Test User</a>"
    
    chat = MagicMock(spec=Chat)
    chat.id = 12345
    
    message = MagicMock(spec=Message)
    message.message_id = 1
    message.chat = chat
    message.reply_text = AsyncMock()
    message.reply_html = AsyncMock()
    message.reply_markdown = AsyncMock()
    
    update = MagicMock(spec=Update)
    update.effective_user = user
    update.message = message
    update.effective_message = message
    
    return update

@pytest.fixture
def mock_context():
    context = MagicMock()
    context.args = []
    context.bot = MagicMock()
    context.bot.get_file = AsyncMock()
    return context

@pytest.mark.asyncio
async def test_start_command(mock_update, mock_context):
    """Test the /start command"""
    await start(mock_update, mock_context)
    mock_update.message.reply_html.assert_called_once()
    assert "Hi" in mock_update.message.reply_html.call_args[0][0]
    assert "Book Retention Bot" in mock_update.message.reply_html.call_args[0][0]

@pytest.mark.asyncio
async def test_help_command(mock_update, mock_context):
    """Test the /help command"""
    await help_command(mock_update, mock_context)
    mock_update.message.reply_markdown.assert_called_once()
    assert "Book Retention Bot Commands" in mock_update.message.reply_markdown.call_args[0][0]

@pytest.mark.asyncio
@patch('ai_bot.bot.command_handler.get_user')
@patch('ai_bot.bot.command_handler.create_user')
async def test_register_command_new_user(mock_create_user, mock_get_user, mock_update, mock_context):
    """Test the /register command for a new user"""
    mock_get_user.return_value = None
    mock_context.args = ["America/New_York"]
    
    await register_command(mock_update, mock_context)
    
    mock_get_user.assert_called_once()
    mock_create_user.assert_called_once()
    mock_update.message.reply_text.assert_called_once()
    assert "Welcome" in mock_update.message.reply_text.call_args[0][0]
    assert "America/New_York" in mock_update.message.reply_text.call_args[0][0]

@pytest.mark.asyncio
@patch('ai_bot.bot.command_handler.get_user')
@patch('ai_bot.bot.command_handler.update_user_preferences')
async def test_register_command_existing_user(mock_update_preferences, mock_get_user, mock_update, mock_context):
    """Test the /register command for an existing user"""
    mock_user = MagicMock()
    mock_get_user.return_value = mock_user
    mock_context.args = ["Europe/London"]
    
    await register_command(mock_update, mock_context)
    
    mock_get_user.assert_called_once()
    mock_update_preferences.assert_called_once()
    mock_update.message.reply_text.assert_called_once()
    assert "updated" in mock_update.message.reply_text.call_args[0][0]
    assert "Europe/London" in mock_update.message.reply_text.call_args[0][0]

@pytest.mark.asyncio
@patch('ai_bot.bot.message_router.get_user')
@patch('ai_bot.bot.message_router.update_user_activity')
async def test_handle_document_unsupported_file(mock_update_activity, mock_get_user, mock_update, mock_context):
    """Test handling an unsupported document type"""
    mock_user = MagicMock()
    mock_get_user.return_value = mock_user
    
    document = MagicMock(spec=Document)
    document.file_name = "test.doc"
    mock_update.message.document = document
    
    await handle_document(mock_update, mock_context)
    
    mock_get_user.assert_called_once()
    mock_update_activity.assert_called_once()
    mock_update.message.reply_text.assert_called_once()
    assert "not supported" in mock_update.message.reply_text.call_args[0][0]

@pytest.mark.asyncio
@patch('ai_bot.bot.message_router.get_user')
@patch('ai_bot.bot.message_router.update_user_activity')
@patch('ai_bot.bot.message_router.process_book_file')
async def test_handle_document_supported_file(mock_process_book, mock_update_activity, mock_get_user, mock_update, mock_context):
    """Test handling a supported document type"""
    mock_user = MagicMock()
    mock_user.id = 1
    mock_get_user.return_value = mock_user
    
    document = MagicMock(spec=Document)
    document.file_name = "test.pdf"
    document.file_id = "test_file_id"
    mock_update.message.document = document
    
    file_mock = AsyncMock()
    file_mock.download_as_bytearray = AsyncMock(return_value=b"test_content")
    mock_context.bot.get_file.return_value = file_mock
    
    mock_book = MagicMock()
    mock_book.id = 1
    mock_book.title = "Test Book"
    mock_book.processed_chapters = 10
    mock_process_book.return_value = mock_book
    
    await handle_document(mock_update, mock_context)
    
    mock_get_user.assert_called_once()
    mock_update_activity.assert_called_once()
    mock_context.bot.get_file.assert_called_once_with(document.file_id)
    file_mock.download_as_bytearray.assert_called_once()
    mock_process_book.assert_called_once()
    assert mock_update.message.reply_text.call_count == 2
    assert "processed successfully" in mock_update.message.reply_text.call_args[0][0]
