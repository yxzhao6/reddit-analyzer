import unittest
import json
from unittest.mock import patch, MagicMock
from app import app as flask_app # Import the Flask app instance from app package
from app.routes import praw_available as routes_praw_available # To check initial state
import os

# Store original PRAW availability state from routes.py
ORIGINAL_PRAW_AVAILABLE_STATE = routes_praw_available

class TestApp(unittest.TestCase):

    def setUp(self):
        """Set up test client and other resources."""
        flask_app.testing = True
        self.client = flask_app.test_client()
        # Ensure a clean slate for PRAW availability for each test
        # We might need to patch 'app.routes.praw_available' and 'app.routes.reddit'
        # for some tests.
        self.patch_praw_available = patch('app.routes.praw_available')
        self.mock_praw_available = self.patch_praw_available.start()

        self.patch_reddit_instance = patch('app.routes.reddit')
        self.mock_reddit_instance = self.patch_reddit_instance.start()


    def tearDown(self):
        """Clean up after tests."""
        self.patch_praw_available.stop()
        self.patch_reddit_instance.stop()


    def test_flask_app_creation(self):
        """Test if the Flask app instance is created."""
        self.assertTrue(flask_app is not None)

    @patch('app.llm_utils.get_llm_response')
    def test_send_message_valid_with_subreddit(self, mock_get_llm_response):
        """Test /send_message with a valid subreddit and question."""
        self.mock_praw_available = True
        self.mock_reddit_instance = MagicMock()

        # Configure the mock PRAW subreddit object
        mock_subreddit = MagicMock()
        mock_subreddit.display_name = "learnpython"
        mock_subreddit.public_description = "Learn Python here!"
        mock_subreddit.subscribers = 12345
        mock_subreddit.created_utc = 1234567890 # Needs to be present to pass existence check
        self.mock_reddit_instance.subreddit.return_value = mock_subreddit

        mock_get_llm_response.return_value = "Mocked LLM response for learnpython"

        payload = {"message": "@r/learnpython what is list comprehension?"}
        response = self.client.post('/send_message', data=json.dumps(payload), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['reply'], "Mocked LLM response for learnpython")
        self.assertIsNone(data['error'])
        mock_get_llm_response.assert_called_once_with(
            "what is list comprehension?",
            {'display_name': 'learnpython', 'public_description': 'Learn Python here!', 'subscribers': 12345, 'name': 'learnpython'},
            praw_available_for_llm=True
        )

    @patch('app.llm_utils.get_llm_response')
    def test_send_message_no_subreddit_tag(self, mock_get_llm_response):
        """Test /send_message when no @r/ tag is present."""
        self.mock_praw_available = True # PRAW could be available
        mock_get_llm_response.return_value = "Mocked LLM response for general query"

        payload = {"message": "what is python?"}
        response = self.client.post('/send_message', data=json.dumps(payload), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['reply'], "Mocked LLM response for general query")
        self.assertIsNone(data['error'])
        mock_get_llm_response.assert_called_once_with("what is python?", None, praw_available_for_llm=True)

    def test_send_message_empty_message(self):
        """Test /send_message with an empty message string."""
        payload = {"message": " "} # Whitespace only
        response = self.client.post('/send_message', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200) # Current routes return 200 with error in JSON
        data = json.loads(response.data)
        self.assertIsNone(data['reply'])
        self.assertEqual(data['error'], "Please enter a question.")

    def test_send_message_invalid_payload_format(self):
        """Test /send_message with invalid JSON payload."""
        payload = {"text": "this is not the right key"} # Incorrect key
        response = self.client.post('/send_message', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIsNone(data['reply'])
        self.assertEqual(data['error'], "Invalid request: No message provided.")

    def test_send_message_subreddit_but_empty_question(self):
        """Test /send_message with a subreddit tag but no question."""
        payload = {"message": "@r/askreddit "}
        response = self.client.post('/send_message', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200) # Current routes return 200 with error in JSON
        data = json.loads(response.data)
        self.assertIsNone(data['reply'])
        self.assertEqual(data['error'], "You mentioned r/askreddit, but what is your question?")

    @patch('app.llm_utils.get_llm_response')
    def test_send_message_praw_unavailable(self, mock_get_llm_response):
        """Test /send_message when PRAW is globally unavailable."""
        self.mock_praw_available.return_value = False # Patch praw_available to be False
        self.mock_reddit_instance = None # Ensure reddit instance is None

        mock_get_llm_response.return_value = "LLM response when PRAW is down"

        payload = {"message": "@r/someplace what is it?"}
        response = self.client.post('/send_message', data=json.dumps(payload), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['reply'], "LLM response when PRAW is down")
        self.assertIsNone(data['error'])
        # PRAW was unavailable, so subreddit_info_dict should be None
        mock_get_llm_response.assert_called_once_with("what is it?", None, praw_available_for_llm=False)

    @patch('app.routes.reddit', new_callable=MagicMock) # Mock the reddit instance directly in routes
    @patch('app.llm_utils.get_llm_response')
    def test_send_message_praw_subreddit_not_found(self, mock_get_llm_response, mock_reddit_obj_in_routes):
        """Test /send_message when a subreddit is not found by PRAW."""
        self.mock_praw_available = True # PRAW itself is available

        # Simulate PRAW raising Redirect when subreddit is accessed
        from prawcore.exceptions import Redirect
        mock_reddit_obj_in_routes.subreddit.side_effect = Redirect(response=MagicMock())

        payload = {"message": "@r/nonexistentsub what?"}
        response = self.client.post('/send_message', data=json.dumps(payload), content_type='application/json')

        self.assertEqual(response.status_code, 200) # Error is in JSON
        data = json.loads(response.data)
        self.assertIsNone(data['reply'])
        self.assertEqual(data['error'], "Sorry, the subreddit r/nonexistentsub could not be found.")
        mock_get_llm_response.assert_not_called()

    @patch('app.routes.reddit', new_callable=MagicMock)
    @patch('app.llm_utils.get_llm_response')
    def test_send_message_praw_api_error_on_fetch(self, mock_get_llm_response, mock_reddit_obj_in_routes):
        """Test /send_message with a PRAW API error during fetch."""
        self.mock_praw_available = True
        from prawcore.exceptions import PrawcoreException
        mock_reddit_obj_in_routes.subreddit.side_effect = PrawcoreException(response=MagicMock())

        payload = {"message": "@r/brokenapi what?"}
        response = self.client.post('/send_message', data=json.dumps(payload), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsNone(data['reply'])
        self.assertEqual(data['error'], "Sorry, an error occurred with the Reddit API while trying to fetch r/brokenapi.")
        mock_get_llm_response.assert_not_called()

    # Test for when PRAW is marked as available but the reddit object is None (init failed)
    @patch('app.routes.praw_available', True) # Force praw_available to True
    @patch('app.routes.reddit', None)        # Force reddit instance to None
    @patch('app.llm_utils.get_llm_response')
    def test_send_message_praw_available_but_reddit_none(self, mock_get_llm_response):
        payload = {"message": "@r/anything query"}
        response = self.client.post('/send_message', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsNotNone(data['error'])
        self.assertEqual(data['error'], "Sorry, Reddit API access is not configured correctly on the server.")
        mock_get_llm_response.assert_not_called()


if __name__ == '__main__':
    unittest.main()
