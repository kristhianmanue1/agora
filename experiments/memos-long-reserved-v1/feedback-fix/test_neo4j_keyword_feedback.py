"""Regression tests for scoped keyword feedback on Neo4j Community."""
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock
from memos.graph_dbs.neo4j_community import Neo4jCommunityGraphDB

class KeywordFeedbackTests(unittest.TestCase):
    def store(self):
        db = object.__new__(Neo4jCommunityGraphDB)
        db.config = SimpleNamespace(user_name=None)
        db.db_name = 'neo4j'
        db.driver = MagicMock()
        db.driver.session.return_value.__enter__.return_value.run.return_value = [{'id': 'one'}]
        return db

    def test_scoped_parameterized_lookup(self):
        db = self.store()
        result = db.search_by_keywords_like('%Tuesday%', user_name='fixture')
        self.assertEqual(result, [{'id': 'one'}])
        args, params = db.driver.session.return_value.__enter__.return_value.run.call_args
        self.assertIn('n.user_name = $user_name', args[0])
        self.assertNotIn('Tuesday', args[0])
        self.assertEqual(params['pattern'], '(?s).*Tuesday.*')
        self.assertEqual(params['user_name'], 'fixture')
        self.assertIn('activated', args[0])

    def test_no_unscoped_search(self):
        db = self.store()
        with self.assertRaises(ValueError):
            db.search_by_keywords_like('%Tuesday%')
        db.driver.session.assert_not_called()

    def test_regex_characters_are_literal_and_filters_retained(self):
        db = self.store()
        db._build_filter_conditions_cypher = MagicMock(return_value=(['n.agent = $f0'], {'f0': 'agent-a'}))
        db.search_by_keywords_like('%a.b%', user_name='fixture', filter={'info.agent_id': 'agent-a'})
        args, params = db.driver.session.return_value.__enter__.return_value.run.call_args
        self.assertEqual(params['pattern'], '(?s).*a\\.b.*')
        self.assertIn('n.agent = $f0', args[0])
        self.assertEqual(params['f0'], 'agent-a')

if __name__ == '__main__':
    unittest.main()
