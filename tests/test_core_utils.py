import unittest
from app.core_utils import parse_subreddit_and_question

class TestCoreUtils(unittest.TestCase):

    def test_parse_valid_subreddit_and_question(self):
        message = "@r/learnpython what is flask?"
        subreddit, question = parse_subreddit_and_question(message)
        self.assertEqual(subreddit, "learnpython")
        self.assertEqual(question, "what is flask?")

    def test_parse_valid_subreddit_no_space(self):
        message = "@r/django_rest_frameworkhow to serialize?"
        subreddit, question = parse_subreddit_and_question(message)
        self.assertEqual(subreddit, "django_rest_framework")
        self.assertEqual(question, "how to serialize?")

    def test_parse_valid_subreddit_and_question_with_leading_spaces(self):
        message = "  @r/learnpython what is flask?"
        subreddit, question = parse_subreddit_and_question(message)
        self.assertEqual(subreddit, "learnpython")
        self.assertEqual(question, "what is flask?")

    def test_parse_no_subreddit_tag(self):
        message = "what is python?"
        subreddit, question = parse_subreddit_and_question(message)
        self.assertIsNone(subreddit)
        self.assertEqual(question, "what is python?")

    def test_parse_subreddit_tag_not_at_start(self):
        message = "My question about @r/askreddit is important."
        subreddit, question = parse_subreddit_and_question(message)
        self.assertIsNone(subreddit)
        self.assertEqual(question, "My question about @r/askreddit is important.")

    def test_parse_empty_question_after_subreddit(self):
        message = "@r/help "
        subreddit, question = parse_subreddit_and_question(message)
        self.assertEqual(subreddit, "help")
        self.assertEqual(question, "")

    def test_parse_empty_question_after_subreddit_no_space(self):
        message = "@r/help"
        subreddit, question = parse_subreddit_and_question(message)
        self.assertEqual(subreddit, "help")
        self.assertEqual(question, "")

    def test_parse_empty_message(self):
        message = ""
        subreddit, question = parse_subreddit_and_question(message)
        self.assertIsNone(subreddit)
        self.assertEqual(question, "")

    def test_parse_only_subreddit_tag(self):
        message = "@r/onlytag"
        subreddit, question = parse_subreddit_and_question(message)
        self.assertEqual(subreddit, "onlytag")
        self.assertEqual(question, "")

    def test_parse_tag_with_special_chars_in_question(self):
        message = "@r/techsupport my computer is making a @wEiRd noise!"
        subreddit, question = parse_subreddit_and_question(message)
        self.assertEqual(subreddit, "techsupport")
        self.assertEqual(question, "my computer is making a @wEiRd noise!")

    def test_parse_just_tag_and_spaces(self):
        message = "@r/ask   "
        subreddit, question = parse_subreddit_and_question(message)
        self.assertEqual(subreddit, "ask")
        self.assertEqual(question, "")

if __name__ == '__main__':
    unittest.main()
