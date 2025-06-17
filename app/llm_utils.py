def get_llm_response(question, subreddit_info=None, praw_available_for_llm=True):
    """
    Generates a mock response simulating an LLM's answer.

    This function currently returns predefined string patterns based on whether
    subreddit information (fetched via PRAW) was available and provided, and
    whether PRAW itself was considered active (e.g., credentials loaded).

    In a real application, this function would interact with an actual LLM API.

    Args:
        question (str): The user's question (potentially stripped of subreddit tags).
        subreddit_info (dict, optional): A dictionary containing details about the
            queried subreddit (e.g., 'display_name', 'public_description',
            'subscribers'). Defaults to None if no info was fetched or applicable.
        praw_available_for_llm (bool): Flag indicating if PRAW was considered
            available/functional at the time of the call. This helps tailor
            the mock response.

    Returns:
        str: A string representing the LLM's (mocked) answer.
    """
    if subreddit_info:
        # Case 1: Subreddit context was successfully fetched.
        subreddit_name = subreddit_info.get('display_name', subreddit_info.get('name', 'unknown'))
        description = subreddit_info.get('public_description', 'No description available.')
        subscribers = subreddit_info.get('subscribers', 'N/A')

        return (f"LLM mock response: Based on live info from r/{subreddit_name} "
                f"(Subscribers: {subscribers}, Description: '{description}'), "
                f"the answer to '{question}' is [mocked answer using this specific subreddit context].")

    elif praw_available_for_llm:
        # Case 2: PRAW was available, but no specific subreddit info was provided for this question.
        # This typically means the user didn't use an @r/subreddit tag, or the tag was invalid
        # and handled before this function was called.
        return (f"LLM mock response: I can access Reddit, but you didn't specify a subreddit or "
                f"there was an issue I couldn't pinpoint for the one you mentioned. "
                f"For your question '{question}', the general answer is [mocked generic answer, PRAW was active].")

    else:
        # Case 3: PRAW was NOT available (e.g., credentials missing, initialization failed).
        # The response reflects that no live Reddit data could be accessed.
        return (f"LLM mock response: I currently don't have access to live Reddit data. "
                f"Regarding your question '{question}', the general answer without subreddit context is [mocked generic answer, PRAW was INACTIVE].")
