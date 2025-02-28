# Book Retention System

A comprehensive Telegram bot for processing, analyzing, and creating spaced repetition learning schedules for books.

## Features

- Process uploaded books (PDF, EPUB, MOBI, TXT)
- Extract and analyze book content using Claude AI
- Create spaced repetition learning schedules
- Interactive quizzes and learning tools
- Track learning progress and retention

## Setup

### Prerequisites

- Python 3.9 or higher
- Poetry (dependency management)
- Telegram Bot Token
- Anthropic API Key (for Claude)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/book-retention-system.git
   cd book-retention-system
   ```

2. Install dependencies using Poetry:
   ```
   poetry install
   ```

3. Create a `.env` file in the root directory with your API keys:
   ```
   TELEGRAM_TOKEN=your_telegram_bot_token
   ANTHROPIC_API_KEY=your_anthropic_api_key
   ```

4. Run the bot:
   ```
   poetry run start
   ```

### Docker Setup

Alternatively, you can use Docker:

1. Build the Docker image:
   ```
   docker build -t book-retention-bot .
   ```

2. Run the container:
   ```
   docker run -d --name book-bot -v $(pwd)/data:/app/data -v $(pwd)/logs:/app/logs --env-file .env book-retention-bot
   ```

## Bot Commands

### User Management
- `/start` - Get started with the bot
- `/register [timezone]` - Create user account with timezone preference
- `/preferences` - Set notification times, content depth preferences

### Book Management
- `/browse [category]` - View curated books by category
- `/search [query]` - Find specific books by title/author
- `/add [title] [author]` - Manually add a book
- `/upload` - Upload book file (PDF, EPUB, etc.)
- `/mybooks` - View books in progress/completed

### Book Analysis
- `/summary [book_id]` - Receive AI-generated book overview
- `/concepts [book_id]` - Get key takeaways as bullet points
- `/estimate [book_id]` - Show reading and learning time estimates

### Learning Schedule
- `/schedule [book_id]` - Set up learning schedule
- `/pause [book_id]` - Temporarily pause schedule
- `/resume [book_id]` - Resume paused schedule

### Spaced Repetition
- `/recap [book_id]` - Core concept reminders (Day 1)
- `/connect [book_id]` - Concept connections (Day 3)
- `/apply [book_id]` - Application prompts (Day 7)
- `/master [book_id]` - Comprehensive review (Day 30)

### Interactive Learning
- `/quiz [book_id]` - Get multiple-choice questions
- `/explain [concept]` - Free text response to concept
- `/progress [book_id]` - View question completion stats
- `/teach [concept]` - Get prompts to explain concept
- `/improve [concept]` - Get suggestions to improve explanation

### Analytics
- `/stats [book_id]` - View personal retention metrics
- `/compare [book_id1] [book_id2]` - Compare learning across books
- `/export [book_id] [format]` - Export notes and insights

### Other Commands
- `/help` - List all available commands
- `/status` - Current progress across all books
- `/skip [concept]` - Move to next concept
- `/restart [book_id]` - Begin book from scratch
- `/feedback [text]` - Submit user feedback

## Development

### Project Structure

```
/ai-bot/
  /bot/          - Telegram bot core
  /users/        - User management
  /books/        - Book processing
  /processing/   - Content chunking
  /analysis/     - AI analysis
  /api/          - API integrations
  /learning/     - Spaced repetition
  /interactive/  - Interactive learning
  /analytics/    - Metrics and insights
  /database/     - Database models
  /errors/       - Error handling
/tests/          - Test suite
/templates/      - Prompt templates
/logs/           - Application logs
/data/           - Database and books
```

### Running Tests

```
poetry run pytest
```

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

[MIT License](LICENSE)
