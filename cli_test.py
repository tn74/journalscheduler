import unittest
import tempfile
import os
import csv
from cli import parse_students, parse_journals, write_results
from scheduler import Student, Journal

class TestCLI(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for our mock CSV files
        self.test_dir = tempfile.TemporaryDirectory()
        self.students_csv = os.path.join(self.test_dir.name, 'students.csv')
        self.journals_csv = os.path.join(self.test_dir.name, 'journals.csv')
        self.output_csv = os.path.join(self.test_dir.name, 'output.csv')

    def tearDown(self):
        self.test_dir.cleanup()

    def test_parse_students(self):
        with open(self.students_csv, 'w', encoding='utf-8') as f:
            f.write("id,name,choice1,choice2,choice3\n")
            f.write("1,Alice,Journal A,Journal B,\n")
            f.write("2, Bob , Journal B , ,\n")  # Test whitespace and empty cells

        prefs, all_students = parse_students(self.students_csv)
        
        alice = Student(1, "Alice")
        bob = Student(2, "Bob")
        
        self.assertEqual(len(all_students), 2)
        self.assertEqual(all_students[1], alice)
        self.assertEqual(all_students[2], bob)
        
        self.assertEqual(prefs[alice], ["Journal A", "Journal B"])
        self.assertEqual(prefs[bob], ["Journal B"])

    def test_parse_journals(self):
        # Transposed representation
        with open(self.journals_csv, 'w', encoding='utf-8') as f:
            f.write("Labels,Journal A,Journal B\n")
            f.write("Capacity,2,1\n")
            f.write("Rank 1,2,1\n")
            f.write("Rank 2,1,\n") # Missing cell on the right handled gracefully
        
        alice = Student(1, "Alice")
        bob = Student(2, "Bob")
        all_students = {1: alice, 2: bob}
        
        journals_dict = parse_journals(self.journals_csv, all_students)
        
        self.assertEqual(len(journals_dict), 2)
        self.assertEqual(journals_dict["Journal A"].capacity, 2)
        self.assertEqual(journals_dict["Journal A"].ranked_students, [bob, alice]) # Bob is ID 2, Alice is ID 1
        
        self.assertEqual(journals_dict["Journal B"].capacity, 1)
        self.assertEqual(journals_dict["Journal B"].ranked_students, [alice])

    def test_write_results(self):
        alice = Student(1, "Alice")
        bob = Student(2, "Bob")
        charlie = Student(3, "Charlie")
        
        all_students = [alice, bob, charlie]
        
        final_matches = {
            "Journal A": [alice, bob],
            "Journal B": []
        }
        
        write_results(self.output_csv, final_matches, all_students)
        
        # Read the written CSV to verify
        with open(self.output_csv, 'r', encoding='utf-8') as f:
            reader = list(csv.reader(f))
            
        self.assertEqual(reader[0], ["Journal A", "Journal B", "Unmatched Students"])
        self.assertEqual(reader[1], ["Alice (1)", "", "Charlie (3)"])
        self.assertEqual(reader[2], ["Bob (2)", "", ""]) 

if __name__ == "__main__":
    unittest.main()
