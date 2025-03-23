# tests/test_jira.py
import unittest
from unittest.mock import patch, MagicMock
from src.automation.jira import Jira

class TestJira(unittest.TestCase):

    @patch('src.automation.jira.JIRA')
    def setUp(self, MockJIRA):
        self.mock_jira = MockJIRA.return_value
        self.jira = Jira()

    def test_test_connection_success(self):
        self.mock_jira.myself.return_value = {'emailAddress': 'test@example.com'}
        result = self.jira.test_connection()
        self.assertTrue(result)

    def test_test_connection_failure(self):
        self.mock_jira.myself.side_effect = Exception("Connection error")
        result = self.jira.test_connection()
        self.assertFalse(result)

    def test_get_current_sprint(self):
        self.mock_jira.sprints.return_value = [MagicMock(name='Sprint 1')]
        result = self.jira.get_current_sprint(1)
        self.assertEqual(result, 'Sprint 1')

    def test_get_current_sprint_no_active_sprints(self):
        self.mock_jira.sprints.return_value = []
        result = self.jira.get_current_sprint(1)
        self.assertEqual(result, 'No hay sprints activos :V')

    def test_get_sprint_stories(self):
        self.mock_jira.search_issues.return_value = ['Story 1', 'Story 2']
        result = self.jira.get_sprint_stories(1)
        self.assertEqual(result, ['Story 1', 'Story 2'])

    def test_list_issue_types(self):
        self.mock_jira.issue_types.return_value = [MagicMock(id='1', name='Bug'), MagicMock(id='2', name='Task')]
        with patch('builtins.print') as mocked_print:
            self.jira.list_issue_types()
            mocked_print.assert_any_call('ID: 1, Name: Bug')
            mocked_print.assert_any_call('ID: 2, Name: Task')

if __name__ == '__main__':
    unittest.main()