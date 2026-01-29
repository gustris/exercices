import unittest
from unittest.mock import patch
from calculette_IAmulti import calculer

class TestCalculatrice(unittest.TestCase):

    def test_valid_calculation(self):
        # Test une opération valide
        with patch('builtins.input', side_effect=['1', '4.4', 'addition', '3.3', 'oui', '4.4', 'division', '0', 'non']):
            calculer()
            self.assertEqual(display_result.call_args_list[0][0][0], 'Le résultat est: 14.92')

    def test_invalid_calculation(self):
        # Test une opération incorrecte
        with patch('builtins.input', side_effect=['1', '4.4', 'division', '0', 'oui']):
            with self.assertRaises(ValueError):
                calculer()

if __name__ == '__main__':
    unittest.main()