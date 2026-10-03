import unittest
from selector import select

class SelectorChecks(unittest.TestCase):
    def test_budget_utf8_and_duplicates(self):
        raw = 'baseline input result café\n\ninput sentence\n\nresult accuracy'.encode()
        for budget in (1, 12, 30, 100):
            result = select(raw, 'compare input accuracy', budget)
            ranges = result['ranges']
            self.assertEqual(len(ranges), len(set(map(tuple, ranges))))
            self.assertEqual(sum(b-a for a,b in ranges), result['delivered_bytes'])
            self.assertLessEqual(result['delivered_bytes'], budget)
            for a,b in ranges: raw[a:b].decode()
    def test_no_match_and_bad_budget(self):
        self.assertEqual(select(b'unrelated prose', 'anything', 100)['ranges'], [])
        for budget in (0, -1, True, '5'):
            with self.assertRaises(ValueError): select(b'input', 'input', budget)
    def test_all_roles_with_room(self):
        raw = b'baseline alpha\n\ninput beta\n\naccuracy gamma'
        self.assertEqual(len(select(raw, 'alpha beta gamma', 100)['ranges']), 3)

if __name__ == '__main__': unittest.main()
