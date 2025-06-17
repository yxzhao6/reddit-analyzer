# Reddit Q&A Chatbot

## Project Overview

This project is a Flask-based web application that allows users to ask questions about specific Reddit subreddits. It aims to use the Reddit API (via PRAW) to fetch information about a subreddit and then (eventually) use a Large Language Model (LLM) to answer questions based on that information. The current version uses a mocked LLM.

## Features

*   Simple web-based chat interface.
*   Parses subreddit mentions (e.g., `@r/learnpython What is a decorator?`).
*   Fetches basic subreddit details (name, description, subscriber count) using the Reddit API (PRAW) if credentials are provided.
*   Provides responses using a mocked Large Language Model (LLM).
*   User-friendly error messages for API issues or invalid input.
*   Comprehensive backend unit tests.

## How it Works

The application follows this basic flow:

1.  **User Input**: The user types a message into the web chat interface. This message might include a subreddit tag like `@r/subredditname`.
2.  **Frontend to Backend**: The JavaScript frontend sends the message to the Flask backend (`/send_message` endpoint).
3.  **Subreddit Parsing**: The backend's `app.core_utils.parse_subreddit_and_question` function attempts to extract the subreddit name and the actual question from the user's message.
4.  **PRAW Integration (Reddit API)**:
    *   If a subreddit name is identified and Reddit API credentials (`REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USER_AGENT`) are correctly set up as environment variables, the application uses PRAW to connect to the Reddit API.
    *   It then attempts to fetch information about the specified subreddit (e.g., public description, subscriber count).
    *   Various errors are handled, such as invalid credentials, subreddit not found, or other API issues. If PRAW is not configured or an error occurs, this step is skipped or an error message is prepared.
5.  **LLM Interaction (Mocked)**:
    *   The user's question and any fetched subreddit information (or lack thereof) are passed to the `app.llm_utils.get_llm_response` function.
    *   Currently, this function is a **mock**. It does not connect to a real LLM but returns a predefined string indicating what kind of information it received (e.g., if subreddit data was available, if PRAW was active).
6.  **Response to Frontend**: The Flask backend sends a JSON response to the frontend. This response contains either the (mocked) LLM's reply or an error message.
7.  **Display to User**: The JavaScript frontend displays the bot's reply or error message in the chat interface.

## Setup and Running

1.  **Clone the repository:**
    ```bash
    git clone <your_repository_url> # Replace with the actual URL
    cd reddit-qna-chatbot
    ```

2.  **Create and activate a Python virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Environment Variables (Crucial for Reddit API Functionality):**
    To allow the application to fetch live data from Reddit, you need to set up API credentials.
    *   Go to [Reddit's app preferences](https://www.reddit.com/prefs/apps).
    *   Click "are you a developer? create an app..."
    *   Fill out the form:
        *   **name**: A unique name for your app (e.g., `MyRedditQnABotV1`)
        *   **type**: Select `script`.
        *   **description**: (Optional)
        *   **about url**: (Optional)
        *   **redirect uri**: `http://localhost:8080` (This is often required but not strictly used for script-type apps).
    *   Click "create app". You will see your app listed. The client ID is shown beneath the app name (it's a string of characters). The client secret is labeled "secret".

    Set the following environment variables in your terminal before running the app:
    ```bash
    export REDDIT_CLIENT_ID="YOUR_CLIENT_ID"
    export REDDIT_CLIENT_SECRET="YOUR_CLIENT_SECRET"
    export REDDIT_USER_AGENT="MyRedditQnABot/0.1 by YourRedditUsername" # Customize with your app name and Reddit username
    ```
    **Note:** If these variables are not set or are incorrect, the application will still run, but it will not be able to fetch live data from Reddit. The bot will indicate that it doesn't have Reddit access in its responses.

5.  **Run the Flask application:**
    ```bash
    python run.py
    ```
    The application will typically be available at `http://127.0.0.1:5000/`.

## Running Tests

To run the automated unit tests, ensure your virtual environment is activated and navigate to the project root directory. Then run:
```bash
python -m unittest discover -s tests
```
This command will discover and execute all test cases located in the `tests` directory.

## LLM Integration Status & Limitations

*   **Mocked LLM**: The core limitation is that the Large Language Model (LLM) is currently **mocked**. The `app/llm_utils.py` file contains a placeholder function that returns hardcoded string patterns. It does **not** perform any actual natural language processing or question answering.
*   **Reddit API Dependency**: Real-time Reddit data fetching is entirely dependent on the correct setup of PRAW credentials as environment variables. Without these, the bot operates with no live subreddit context.
*   **Basic Error Handling**: While error handling for common scenarios (API errors, bad input) is implemented, it could be made more granular for a production system.
*   **Simple UI**: The user interface is very basic HTML, CSS, and JavaScript, focused on functionality rather than aesthetics.

## Project Structure

*   `run.py`: Main script to start the Flask development server.
*   `requirements.txt`: Lists Python package dependencies.
*   `app/`: The main application package.
    *   `__init__.py`: Initializes the Flask application (`app`).
    *   `core_utils.py`: Contains utility functions, like subreddit and question parsing.
    *   `llm_utils.py`: Contains the (currently mock) LLM interaction logic.
    *   `routes.py`: Defines the Flask application's routes (e.g., serving `index.html`, handling `/send_message`).
    *   `static/`: Contains static assets.
        *   `style.css`: Basic CSS for the chat interface.
        *   `script.js`: Frontend JavaScript for chat functionality and communication with the backend.
    *   `templates/`: HTML templates rendered by Flask.
        *   `index.html`: The main page for the chat application.
*   `tests/`: Contains unit tests for the application.
    *   `__init__.py`: Makes the `tests` directory a Python package.
    *   `test_config.py`: Placeholder for future shared test configurations.
    *   `test_core_utils.py`: Unit tests for parsing logic in `core_utils.py`.
    *   `test_llm_utils.py`: Unit tests for the mock LLM response generator in `llm_utils.py`.
    *   `test_app.py`: Unit tests for the Flask app, routes, and integration of components (using mocks).
*   `venv/`: (Typically) The Python virtual environment directory (if created as per instructions, usually excluded from Git).

## Future Improvements

*   **Real LLM Integration**: Replace the mock LLM with a connection to an actual LLM API (e.g., OpenAI GPT, Google Gemini, an open-source model via Hugging Face). This would involve:
    *   Choosing an LLM provider and setting up API keys.
    *   Modifying `app/llm_utils.py` to make API calls.
    *   Potentially creating more sophisticated prompt engineering that incorporates the fetched Reddit context.
*   **Enhanced Subreddit Analysis**: Instead of just basic info, PRAW could be used to fetch top posts, comments, or specific information from a subreddit's wiki to provide richer context to the LLM.
*   **Improved UI/UX**: Enhance the frontend with a more polished chat interface, loading indicators, and potentially user accounts or history.
*   **Asynchronous Operations**: For real API calls (Reddit, LLM), consider using asynchronous tasks (e.g., with Celery and Redis) to prevent blocking the Flask server, especially for potentially long-running LLM responses.
*   **Deployment**: Document and script the process for deploying the application to a cloud platform (e.g., Heroku, AWS, Google Cloud).
*   **More Robust Error Handling**: Implement more nuanced error handling and feedback for various failure modes.
*   **Security Enhancements**: If handling user data or more sensitive operations in the future, implement appropriate security measures (e.g., input sanitization beyond current, rate limiting).
*   **Configuration Management**: Use a more formal configuration management approach (e.g., Flask config files) instead of relying solely on environment variables for all settings.

## Contributing
(This section can be filled out if the project becomes open to contributions, detailing coding standards, pull request processes, etc.)

## License
(To be determined. Common choices include MIT, Apache 2.0, etc. For now, assume it's proprietary or specify if otherwise.)
