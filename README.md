# StudentBot

StudentBot is a comprehensive Telegram bot designed to assist students with various academic and administrative tasks. It provides features like scholarship search, ISEE calculation, a step-by-step guide for arriving in Italy, and much more.

## Architecture

The bot is built with Python and the `python-telegram-bot` library. It follows a modular architecture to ensure scalability and maintainability.

- **`main.py`**: The entry point of the application. It initializes the bot and registers all the handlers.
- **`studentbot/handlers/`**: This directory contains the logic for handling different user commands and interactions. Each feature has its own handler file.
- **`studentbot/utils/`**: This directory contains utility modules for tasks like database interaction (`db.py`), Redis caching (`redis_utils.py`), text formatting (`text_formatter.py`), and AI-related functions (`ai_utils.py`).
- **`studentbot/config/`**: This directory contains configuration files, such as the menu structure (`menus.json`) and the step-by-step guide (`knowledge.json`).
- **`tests/`**: This directory contains all the tests for the project.

## Setup and Installation

### Prerequisites
- Python 3.11+
- Docker and Docker Compose (for running the bot in a containerized environment)

### Local Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/studentbot.git
    cd studentbot
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements-core.txt -r requirements-dev.txt
    ```

3.  **Create a `.env` file:**
    Copy the `.env.example` file to `.env` and fill in the required environment variables, such as your `TELEGRAM_BOT_TOKEN`, `HUGGINGFACE_API_KEY`, and `DATABASE_URL`.

4.  **Run the bot:**
    ```bash
    python -m studentbot.main
    ```

### Docker Installation

1.  **Create a `.env` file:**
    Follow the instructions in the "Local Installation" section to create and configure your `.env` file.

2.  **Build and run the bot:**
    ```bash
    bash build.sh
    bash run.sh
    ```

## Running Tests

To run the test suite, use the following command:

```bash
pytest
```

## Deployment on Render

This project is designed to be easily deployed on a platform like Render.

1.  **Create a new Web Service on Render.**
2.  **Connect your Git repository.**
3.  **Set the Build Command to:**
    ```bash
    pip install -r requirements-core.txt
    ```
4.  **Set the Start Command to:**
    ```bash
    python -m studentbot.main
    ```
5.  **Add your environment variables** from the `.env` file to the Render dashboard.
6.  **Set up a webhook** for your bot by sending a POST request to the Telegram API:
    ```bash
    curl -X POST https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/setWebhook?url=<BASE_URL>/webhook&secret_token=<WEBHOOK_SECRET>
    ```
    Replace `<TELEGRAM_BOT_TOKEN>`, `<BASE_URL>`, and `<WEBHOOK_SECRET>` with your actual values.

## Roadmap

- **Phase 1 (Infrastructure)**: Complete the core infrastructure, including the database, Redis, Docker, and basic handlers.
- **Phase 2 (UX and Menus)**: Redesign the menu system, improve the user experience, and add more dynamic features.
- **Phase 3 (AI and Advanced Features)**: Enhance the AI capabilities, integrate with a Grok webhook, and add voice responses.
- **Phase 4 (Scaling and Expansion)**: Implement comprehensive testing, CI/CD, a CMS for content management, and a mobile app.
