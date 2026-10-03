"""Explicit memory IDs must not be lost to filename-only replacement scope."""
import unittest
from unittest.mock import Mock
from memos.mem_feedback.feedback import MemFeedback

class TargetedFeedbackRouteTests(unittest.TestCase):
    def test_targeted_correction_uses_semantic_path(self):
        feedback = object.__new__(MemFeedback)
        feedback._keyword_replace_judgement = Mock(return_value={
            'if_keyword_replace': 'true', 'original': 'Tuesday',
            'target': 'Wednesday', 'doc_scope': 'Cedar',
        })
        feedback.process_keyword_replace = Mock(return_value={'wrong_route': True})
        feedback._feedback_judgement = Mock(return_value=[])
        feedback.process_feedback_core('root', 'fixture', [{'role': 'user', 'content': 'Tuesday'}],
                                       'Wednesday replaces Tuesday', retrieved_memory_ids=['known-id'])
        feedback.process_keyword_replace.assert_not_called()
        feedback._feedback_judgement.assert_called_once()

if __name__ == '__main__':
    unittest.main()
