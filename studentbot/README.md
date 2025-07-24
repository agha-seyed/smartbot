# International Student Bot

This is a Telegram bot designed to help international students, with a focus on Iranian students in Perugia, Italy.

## Features

- Multi-language support (Farsi, English, Italian)
- User registration and profile management
- ISEE calculator
- Educational migration consultation form
- Semantic search for common questions
- Weather information for Perugia
- File sending (PDFs and videos)
- Gamification system
- Interactive calendar for deadlines
- Geolocation for important places
- Live chat with an admin
- Question submission form

## Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd studentbot
   ```

2. **Create a virtual environment and install dependencies:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   - Copy `.env.example` to `.env`.
   - Fill in the required values in the `.env` file.

4. **Run the bot:**
   ```bash
   python main.py
   ```

## Deployment

This bot is designed to be deployed on Render.

1. Create a new Web Service on Render.
2. Connect your GitHub repository.
3. Set the environment to Python 3.10.
4. Add your environment variables from the `.env` file.
5. Set the build command to `pip install -r requirements.txt`.
6. Set the start command to `python main.py`.
7. Set up the webhook as described in the project prompt.
