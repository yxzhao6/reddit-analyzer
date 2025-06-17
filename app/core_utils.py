import re

# Regex to extract just the name from a subreddit tag like "@r/learnpython" -> "learnpython"
SUBREDDIT_NAME_EXTRACTOR_PATTERN = r'@r/(\w+)'

# Regex to identify a subreddit tag at the beginning of a message and capture the rest as the question.
# It captures two groups:
# 1. The full subreddit tag (e.g., "@r/learnpython")
# 2. The remainder of the message after the tag and any intermediate whitespace (e.g., "what is flask?")
MESSAGE_SPLIT_PATTERN = r'(@r/\w+\b)\s*(.*)'

def parse_subreddit_and_question(user_message):
    """
    Parses a user message to extract a subreddit mention (e.g., @r/learnpython)
    and the subsequent question. The subreddit mention must be at the beginning
    of the message.

    Args:
        user_message (str): The raw message from the user, which might include
                            leading/trailing whitespace.

    Returns:
        tuple: (subreddit_name, question_text)
               - If a valid subreddit tag is found at the start:
                 (e.g., "learnpython", "what is flask?")
                 If the question part is empty, question_text will be an empty string.
               - If no valid @r/subreddit tag is found at the start:
                 (None, original_message_after_stripping_whitespace)
    """
    user_message = user_message.strip() # Remove leading/trailing whitespace

    # Attempt to match the pattern for "@r/subreddit_tag question_text"
    match = re.match(MESSAGE_SPLIT_PATTERN, user_message)

    if match:
        subreddit_tag_full = match.group(1)  # Full tag, e.g., "@r/learnpython"
        question_text = match.group(2).strip() # The rest of the message, stripped

        # Extract just the subreddit name (e.g., "learnpython") from the full tag
        subreddit_name_match = re.match(SUBREDDIT_NAME_EXTRACTOR_PATTERN, subreddit_tag_full)
        if subreddit_name_match:
            subreddit_name = subreddit_name_match.group(1)
            return subreddit_name, question_text
        else:
            # This case should ideally not be reached if MESSAGE_SPLIT_PATTERN matched correctly,
            # as @r/\w+\b implies a valid tag format.
            # However, as a defensive fallback, return no subreddit and the original message.
            return None, user_message
    else:
        # No @r/subreddit tag was found at the beginning of the message.
        # Return None for subreddit_name and the original (stripped) message as the question.
        return None, user_message
