import unittest
import calculette_IA
from unittest.mock import patch


class TestCalculatrice(unittest.TestCase):

    @patch('builtins.input', side_effect=['4.4', 'addition', '3.3', 'oui', '4.4', 'division', '0', 'non'])
    def test_addition_and_division(self, mock_input):
        # Test l'opération d'addition et de division
        calculette_IA.calculate()
        self.assertEqual(mock_input.call_count, 6)
        self.assertEqual(mock_input.call_args_list[0][0], 'Saisissez le premier opérande : ')
        self.assertEqual(mock_input.call_args_list[1][0], 'Saisissez le deuxième opérande : ')
        self.assertEqual(mock_input.call_args_list[2][0], 'Saisissez l\'opération (addition, soustraction, multiplication, division) : ')
        self.assertEqual(mock_input.call_args_list[3][0], 'Saisissez le premier opérande : ')
        self.assertEqual(mock_input.call_args_list[4][0], 'Saisissez le deuxième opérande : ')

        # Vérification du résultat
        self.assertEqual(mock_input.call_args_list[5][0], 'Voulez-vous continuer ? (oui/non) : ')
        self.assertEqual(display_result.call_args_list[0][0][0], 'Le résultat est: 14.92')
        self.assertEqual(display_result.call_args_list[1][0][0], 'Le résultat est: inf')

if __name__ == '__main__':
    unittest.main()