import unittest

class TestLetterPresence(unittest.TestCase):
    def test_letter_presence(self):
        sentence1 = "gdfjshkqdjcbxw hskjsnxsjcbv"
        sentence2 = "le chat mange la souris"
        sentence3 = "bonjour mond"
        self.assertFalse(test_letter_presence(sentence1), "Letter 'e' not present in sentence1")
        self.assertTrue(test_letter_presence(sentence2), "Letter 'e' present in sentence2")
        self.assertFalse(test_letter_presence(sentence3), "Letter 'e' not present in sentence3")

def test_letter_presence(sentence):
    letter = 'e'
    t = any(letter in word for word in sentence.split())
    return t

if __name__ == '__main__':
    unittest.main()