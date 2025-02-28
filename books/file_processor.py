import os
import tempfile
from pathlib import Path
import PyPDF2
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from ai_bot.errors.logger import setup_logger

logger = setup_logger(__name__)

# Create data directory if it doesn't exist
data_dir = Path(__file__).parent.parent.parent / 'data' / 'books'
data_dir.mkdir(exist_ok=True, parents=True)

def save_uploaded_file(file_bytes, user_id, file_name):
    """Save an uploaded file to disk"""
    # Create user directory if it doesn't exist
    user_dir = data_dir / str(user_id)
    user_dir.mkdir(exist_ok=True)
    
    # Save file
    file_path = user_dir / file_name
    with open(file_path, 'wb') as f:
        f.write(file_bytes)
    
    return str(file_path)

def extract_text_from_pdf(file_path):
    """Extract text from a PDF file"""
    text = ""
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            num_pages = len(reader.pages)
            
            for page_num in range(num_pages):
                page = reader.pages[page_num]
                text += page.extract_text() + "\n\n"
                
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        return None

def extract_text_from_epub(file_path):
    """Extract text from an EPUB file"""
    text = ""
    try:
        book = epub.read_epub(file_path)
        
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                content = item.get_content().decode('utf-8')
                soup = BeautifulSoup(content, 'html.parser')
                text += soup.get_text() + "\n\n"
                
        return text
    except Exception as e:
        logger.error(f"Error extracting text from EPUB: {e}")
        return None

def extract_text_from_txt(file_path):
    """Extract text from a TXT file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except UnicodeDecodeError:
        # Try with different encodings
        encodings = ['latin-1', 'iso-8859-1', 'windows-1252']
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    return file.read()
            except UnicodeDecodeError:
                continue
        
        logger.error(f"Could not decode text file with any encoding")
        return None
    except Exception as e:
        logger.error(f"Error extracting text from TXT: {e}")
        return None

def extract_text(file_path):
    """Extract text from a file based on its extension"""
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension == '.pdf':
        return extract_text_from_pdf(file_path)
    elif file_extension == '.epub':
        return extract_text_from_epub(file_path)
    elif file_extension == '.txt':
        return extract_text_from_txt(file_path)
    else:
        logger.error(f"Unsupported file extension: {file_extension}")
        return None
