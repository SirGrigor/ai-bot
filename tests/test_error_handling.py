import pytest
import logging
from unittest.mock import patch, MagicMock, AsyncMock
from telegram import Update
from telegram.ext import CallbackContext
from errors.error_handler import error_handler
from errors.logger import setup_logger

def test_setup_logger():
    """Test logger setup"""
    with patch('logging.getLogger') as mock_get_logger, \
         patch('logging.FileHandler') as mock_file_handler, \
         patch('logging.StreamHandler') as mock_stream_handler:
        
        # Mock logger
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        mock_logger.handlers = []
        
        # Mock handlers
        mock_file_handler_instance = MagicMock()
        mock_file_handler.return_value = mock_file_handler_instance
        mock_stream_handler_instance = MagicMock()
        mock_stream_handler.return_value = mock_stream_handler_instance
        
        # Call setup_logger
        logger = setup_logger("test_logger")
        
        # Check if logger was created
        mock_get_logger.assert_called_once_with("test_logger")
        
        # Check if handlers were added
        assert mock_logger.addHandler.call_count == 2
        mock_logger.addHandler.assert_any_call(mock_file_handler_instance)
        mock_logger.addHandler.assert_any_call(mock_stream_handler_instance)
        
        # Check if formatter was set
        assert mock_file_handler_instance.setFormatter.call_count == 1
        assert mock_stream_handler_instance.setFormatter.call_count == 1

@pytest.mark.asyncio
async def test_error_handler_unauthorized():
    """Test error handler with Unauthorized error"""
    # Mock update and context
    update = MagicMock(spec=Update)
    update.effective_message = MagicMock()
    update.effective_message.reply_text = AsyncMock()
    
    context = MagicMock(spec=CallbackContext)
    context.error = Exception("Unauthorized: Bot was blocked by the user")
    
    # Mock logger
    with patch('ai_bot.errors.error_handler.logger') as mock_logger:
        await error_handler(update, context)
        
        # Check if error was logged
        assert mock_logger.error.call_count >= 3
        mock_logger.error.assert_any_call(f"Exception while handling an update: {context.error}")
        mock_logger.error.assert_any_call("Error Type: API Error")
        
        # Check if message was sent to user
        update.effective_message.reply_text.assert_called_once()
        assert "trouble communicating with Telegram" in update.effective_message.reply_text.call_args[0][0]

@pytest.mark.asyncio
async def test_error_handler_timeout():
    """Test error handler with timeout error"""
    # Mock update and context
    update = MagicMock(spec=Update)
    update.effective_message = MagicMock()
    update.effective_message.reply_text = AsyncMock()
    
    context = MagicMock(spec=CallbackContext)
    context.error = Exception("Timed out waiting for response")
    
    # Mock logger
    with patch('ai_bot.errors.error_handler.logger') as mock_logger:
        await error_handler(update, context)
        
        # Check if error was logged
        assert mock_logger.error.call_count >= 3
        mock_logger.error.assert_any_call(f"Exception while handling an update: {context.error}")
        mock_logger.error.assert_any_call("Error Type: Network Error")
        
        # Check if message was sent to user
        update.effective_message.reply_text.assert_called_once()
        assert "timed out" in update.effective_message.reply_text.call_args[0][0].lower()

@pytest.mark.asyncio
async def test_error_handler_other_error():
    """Test error handler with other error"""
    # Mock update and context
    update = MagicMock(spec=Update)
    update.effective_message = MagicMock()
    update.effective_message.reply_text = AsyncMock()
    
    context = MagicMock(spec=CallbackContext)
    context.error = Exception("Some unexpected error")
    
    # Mock logger
    with patch('ai_bot.errors.error_handler.logger') as mock_logger:
        await error_handler(update, context)
        
        # Check if error was logged
        assert mock_logger.error.call_count >= 3
        mock_logger.error.assert_any_call(f"Exception while handling an update: {context.error}")
        mock_logger.error.assert_any_call("Error Type: System Error")
        
        # Check if message was sent to user
        update.effective_message.reply_text.assert_called_once()
        assert "unexpected error" in update.effective_message.reply_text.call_args[0][0].lower()
