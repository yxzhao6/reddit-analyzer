import unittest
from app.llm_utils import get_llm_response

class TestLlmUtils(unittest.TestCase):

    def test_llm_response_with_subreddit_info(self):
        question = "What are decorators?"
        subreddit_info = {
            'display_name': 'learnpython',
            'public_description': 'A place to learn Python.',
            'subscribers': 100000
        }
        response = get_llm_response(question, subreddit_info, praw_available_for_llm=True)
        self.assertIn("LLM mock response: Based on live info from r/learnpython", response)
        self.assertIn("Subscribers: 100000", response)
        self.assertIn("Description: 'A place to learn Python.'", response)
        self.assertIn(question, response)
        self.assertIn("[mocked answer using this specific subreddit context]", response)

    def test_llm_response_with_subreddit_info_name_fallback(self):
        question = "What are decorators?"
        subreddit_info = {
            'name': 'learnpython_fallback', # display_name is missing
            'public_description': 'A place to learn Python.',
            'subscribers': 100000
        }
        response = get_llm_response(question, subreddit_info, praw_available_for_llm=True)
        self.assertIn("LLM mock response: Based on live info from r/learnpython_fallback", response)
        self.assertIn(question, response)

    def test_llm_response_praw_available_no_subreddit_info(self):
        question = "What is Python used for?"
        response = get_llm_response(question, subreddit_info=None, praw_available_for_llm=True)
        self.assertIn("LLM mock response: I can access Reddit, but you didn't specify a subreddit", response)
        self.assertIn(question, response)
        self.assertIn("[mocked generic answer, PRAW was active]", response)

    def test_llm_response_praw_unavailable(self):
        question = "What is the GIL?"
        response = get_llm_response(question, subreddit_info=None, praw_available_for_llm=False)
        self.assertIn("LLM mock response: I currently don't have access to live Reddit data.", response)
        self.assertIn(question, response)
        self.assertIn("[mocked generic answer, PRAW was INACTIVE]", response)

    def test_llm_response_praw_unavailable_with_passed_subreddit_info_should_still_indicate_praw_inactive(self):
        # This case tests if praw_available_for_llm=False overrides the presence of subreddit_info,
        # which aligns with the function's current logic.
        question = "Tell me about Django."
        subreddit_info = {
            'display_name': 'django',
            'public_description': 'The web framework for perfectionists with deadlines.',
            'subscribers': 50000
        }
        response = get_llm_response(question, subreddit_info, praw_available_for_llm=False)
        self.assertIn("LLM mock response: I currently don't have access to live Reddit data.", response)
        self.assertNotIn("r/django", response) # Should not use subreddit_info if PRAW is marked inactive
        self.assertIn(question, response)

if __name__ == '__main__':
    unittest.main()
