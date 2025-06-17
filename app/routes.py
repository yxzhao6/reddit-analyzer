import os
import praw
import prawcore # For more specific PRAW exceptions
from flask import render_template, request, jsonify
from app import app # The Flask application instance
from app.llm_utils import get_llm_response
from app.core_utils import parse_subreddit_and_question
import logging

# Configure basic server-side logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- PRAW (Reddit API) Initialization ---
# Attempt to initialize PRAW if credentials are available in environment variables.
# This allows the application to run without PRAW if not configured,
# falling back to LLM responses without Reddit context.

REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT')

# Global flag indicating if PRAW client is available and initialized.
praw_available = bool(REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET and REDDIT_USER_AGENT)
reddit = None  # PRAW Reddit instance

if praw_available:
    try:
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT,
            check_for_async=False  # Suitable for synchronous Flask app
        )
        # Perform a lightweight test call to verify API credentials and connectivity.
        logging.info("PRAW client configured. Attempting a test call to Reddit API...")
        reddit.random_subreddit(nsfw=False) # Fetches a random SFW subreddit.
        logging.info("PRAW initialized and Reddit API connection seems OK.")
    except prawcore.exceptions.OAuthException as e:
        logging.error(f"PRAW OAuthException during initialization: {e}. "
                      "Please check REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, and REDDIT_USER_AGENT.")
        praw_available = False # Mark PRAW as unavailable if auth fails
        reddit = None
    except Exception as e: # Catch other potential errors during PRAW initialization
        logging.error(f"An unexpected error occurred during PRAW initialization: {e}")
        praw_available = False
        reddit = None
else:
    logging.warning("PRAW credentials (REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT) "
                    "not found or incomplete in environment variables. Reddit integration will be skipped.")

# --- Flask Routes ---

@app.route('/')
def index():
    """
    Serves the main HTML page of the chat application.
    """
    return render_template('index.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    """
    Handles incoming chat messages from the user.

    It expects a JSON payload with a 'message' key.
    The message is parsed for a subreddit tag (e.g., @r/learnpython).
    If a tag is found and PRAW is available, it attempts to fetch subreddit info.
    Then, it calls a (currently mock) LLM to generate a response.
    Returns a JSON response with either a 'reply' or an 'error' key.
    """
    try:
        # Basic request validation
        data = request.get_json()
        if not data or 'message' not in data:
            logging.warning("/send_message: Received invalid request (no JSON data or 'message' key).")
            return jsonify({'reply': None, 'error': "Invalid request: No message provided."}), 400

        user_message = data.get('message', '').strip()
        if not user_message:
            logging.info("/send_message: Received empty message.")
            return jsonify({'reply': None, 'error': "Please enter a question."})

        # Parse the user's message to separate subreddit and question
        subreddit_name_from_query, question_for_llm = parse_subreddit_and_question(user_message)
        logging.info(f"/send_message: Parsed query: subreddit='{subreddit_name_from_query}', question='{question_for_llm}'")

        # Validate if a question exists when a subreddit is specified
        if subreddit_name_from_query and not question_for_llm:
            logging.info(f"/send_message: Subreddit '{subreddit_name_from_query}' mentioned, but question is empty.")
            return jsonify({'reply': None, 'error': f"You mentioned r/{subreddit_name_from_query}, but what is your question?"})

        subreddit_info_dict = None
        if subreddit_name_from_query:
            # Attempt to fetch subreddit info only if a subreddit was specified
            if not praw_available:
                logging.warning(f"PRAW not available. Cannot fetch r/{subreddit_name_from_query} for question: '{question_for_llm}'.")
            elif not reddit: # Should not happen if praw_available is True, but as a safeguard
                 logging.error("PRAW was marked as available, but the Reddit instance is None. This indicates an issue during PRAW setup.")
                 return jsonify({'reply': None, 'error': "Sorry, Reddit API access is not configured correctly on the server."})
            else:
                # PRAW is available and initialized, try to get subreddit data
                try:
                    logging.info(f"Fetching info for subreddit: r/{subreddit_name_from_query}...")
                    subreddit_obj = reddit.subreddit(subreddit_name_from_query)
                    # Access an attribute to confirm subreddit exists and is accessible (triggers PRAW exception if not)
                    subreddit_obj.created_utc
                    subreddit_info_dict = {
                        'display_name': subreddit_obj.display_name,
                        'public_description': subreddit_obj.public_description,
                        'subscribers': subreddit_obj.subscribers,
                        'name': subreddit_name_from_query # Pass original parsed name for context
                    }
                    logging.info(f"Successfully fetched info for r/{subreddit_name_from_query}.")
                except prawcore.exceptions.Redirect: # Subreddit does not exist or was redirected (e.g. mistyped)
                    logging.warning(f"Subreddit r/{subreddit_name_from_query} not found (PRAW Redirect).")
                    return jsonify({'reply': None, 'error': f"Sorry, the subreddit r/{subreddit_name_from_query} could not be found."})
                except prawcore.exceptions.NotFound: # Subreddit is banned, private, or quarantined
                    logging.warning(f"Subreddit r/{subreddit_name_from_query} not accessible (PRAW NotFound - e.g., private, banned).")
                    return jsonify({'reply': None, 'error': f"Sorry, r/{subreddit_name_from_query} is private, banned, or quarantined."})
                except prawcore.exceptions.PrawcoreException as e: # Other PRAW-related errors (API limits, network, etc.)
                    logging.error(f"PRAW Core error while fetching r/{subreddit_name_from_query}: {e}")
                    return jsonify({'reply': None, 'error': f"Sorry, an error occurred with the Reddit API while trying to fetch r/{subreddit_name_from_query}."})
                except Exception as e: # Catch any other unexpected errors during PRAW interaction
                    logging.error(f"Unexpected error while fetching data for r/{subreddit_name_from_query}: {e}")
                    return jsonify({'reply': None, 'error': f"An unexpected error occurred while fetching data for r/{subreddit_name_from_query}."})

        # Call the (mock) LLM to get a response
        try:
            llm_reply_text = get_llm_response(question_for_llm, subreddit_info_dict, praw_available_for_llm=praw_available)
            logging.info(f"Generated LLM reply for question '{question_for_llm}'.")
            return jsonify({'reply': llm_reply_text, 'error': None})
        except Exception as e:
            logging.error(f"Error during LLM interaction (mock or real): {e}")
            return jsonify({'reply': None, 'error': "Sorry, there was an issue getting a response from the assistant."})

    except Exception as e:
        # Catch-all for any other unexpected errors in the route
        logging.exception("An unexpected error occurred in the /send_message route:") # Logs full traceback
        return jsonify({'reply': None, 'error': "An unexpected error occurred on the server. Please try again later."}), 500
