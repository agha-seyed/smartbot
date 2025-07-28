# International Student Bot

This is a Telegram bot designed to help international students, with a focus on Iranian students in Perugia, Italy.

## Features

- **Multi-language Support:** The bot supports Farsi, English, and Italian.
- **User Profile:** Users can create and manage their profile with information such as name, age, field of study, and country.
- **Smart Search:** A smart search engine to answer common questions using a knowledge base and semantic search.
- **ISEE Calculator:** An ISEE calculator to help students estimate their financial situation for scholarships.
- **Consultation Form:** A form to request consultation on migration, scholarships, and other topics.
- **File Upload:** A system to upload files to Google Drive.
- **Text-to-Speech and Speech-to-Text:** Convert text to speech and vice versa using Google's and OpenAI's APIs.
- **Gamification:** A gamification system with points, a leaderboard, migration progress tracking, and deadlines.
- **Static Information:** Provides static information about scholarships, migration, housing, student life, universities, language courses, and university news.
- **Weather:** Get the current weather in Perugia.
- **Admin Panel:** A comprehensive admin panel to manage users, questions, and other aspects of the bot.

## Commands

- `/start`: Start the bot and select a language.
- `/profile`: Create or view your profile.
- `/delete_profile`: Delete your profile.
- `/search`: Search for information.
- `/isee`: Calculate your ISEE.
- `/consult`: Request a consultation.
- `/upload`: Upload a file.
- `/tts <text>`: Convert text to speech.
- `/progress`: View your migration progress.
- `/deadlines`: View upcoming deadlines.
- `/points`: View your points.
- `/leaderboard`: View the leaderboard.

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
3. Set the environment to Python 3.11.9.
4. Add your environment variables from the `.env` file.
5. Set the build command to `pip install -r requirements.txt`.
6. Set the start command to `python main.py`.
7. Set up the webhook as described in the project prompt.
