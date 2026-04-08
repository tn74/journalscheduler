import unittest
from scheduler import Matcher, Journal, Student

class TestScheduler(unittest.TestCase):
    def test_gale_shapley_matching(self):
        # MOCK DATA
        ALICE = Student(1, "Alice")
        BOB = Student(2, "Bob")
        CHARLIE = Student(3, "Charlie")
        DIANA = Student(4, "Diana")
        EVE = Student(5, "Eve")
        FRANK = Student(6, "Frank")
        GRACE = Student(7, "Grace")
        HANK = Student(8, "Hank")
        
        # 8 Students applying to 3 Journals.
        student_prefs = {
            ALICE: ["Journal A", "Journal B", "Journal C"],
            BOB: ["Journal A", "Journal C"],
            CHARLIE: ["Journal B", "Journal A"],
            DIANA: ["Journal C", "Journal A", "Journal B"],
            EVE: ["Journal A"],
            FRANK: ["Journal B", "Journal C"],
            GRACE: ["Journal C", "Journal B", "Journal A"],
            HANK: ["Journal A", "Journal B"]
        }
        
        journals = {
            "Journal A": Journal(
                capacity=2, 
                ranked_students=[BOB, ALICE, DIANA, HANK, CHARLIE, EVE]
            ),
            "Journal B": Journal(
                capacity=2,
                ranked_students=[ALICE, FRANK, CHARLIE, HANK]
            ),
            "Journal C": Journal(
                capacity=2,
                ranked_students=[DIANA, GRACE, BOB, FRANK, ALICE]
            )
        }
        
        matcher = Matcher(student_prefs, journals)
        final_roster = matcher.match()
        
        self.assertEqual(final_roster, {
            "Journal A": [BOB, ALICE],
            "Journal B": [FRANK, CHARLIE],
            "Journal C": [DIANA, GRACE]
        })

    def test_unmatched_student_handling(self):
        EVE = Student(5, "Eve")
        student_prefs = {
            EVE: ["Journal A"],
        }
        journals = {
            "Journal A": Journal(capacity=0, ranked_students=[EVE]) # Cap 0
        }
        
        matcher = Matcher(student_prefs, journals)
        final_roster = matcher.match()
        self.assertEqual(final_roster["Journal A"], [])

    def test_prevents_unfair_lockout(self):
        S1 = Student(1, "S1")
        S2 = Student(2, "S2")
        S4 = Student(4, "S4")
        student_prefs = {
            S1: ["A", "B"],
            S2: ["B"],
            S4: ["A"]
        }
        journals = {
            "A": Journal(capacity=1, ranked_students=[S4, S1]),
            "B": Journal(capacity=1, ranked_students=[S1, S2])
        }
        
        matcher = Matcher(student_prefs, journals)
        final_roster = matcher.match()
        
        self.assertEqual(final_roster, {
            "A": [S4],
            "B": [S1]
        })

    def test_more_students_than_spots(self):
        S1 = Student(1, "S1")
        S2 = Student(2, "S2")
        S3 = Student(3, "S3")
        student_prefs = {
            S1: ["A"],
            S2: ["A"],
            S3: ["A"]
        }
        journals = {
            "A": Journal(capacity=1, ranked_students=[S2, S1, S3]) 
        }
        
        matcher = Matcher(student_prefs, journals)
        final_roster = matcher.match()
        
        self.assertEqual(final_roster, {
            "A": [S2]
        })

    def test_simplest_rogue_pair_scenario(self):
        # S1 applies to J1 first and gets conditionally accepted.
        # S2 applies to J1.
        # If naive "first-come, first-serve": S2 is rejected by J1 and goes to J2.
        # Result: S1 is at J1. S2 is at J2.
        # BUT J1 actually prefers S2 over S1, and S2 prefers J1! This is a rogue (blocking) pair.
        # Gale-Shapley prevents this by dynamically bumping S1 so S2 can take J1.
        S1 = Student(1, "S1")
        S2 = Student(2, "S2")

        student_prefs = {
            S1: ["J1", "J2"],
            S2: ["J1", "J2"]
        }
        journals = {
            "J1": Journal(capacity=1, ranked_students=[S2, S1]),
            "J2": Journal(capacity=1, ranked_students=[S1, S2])
        }

        matcher = Matcher(student_prefs, journals)
        final_roster = matcher.match()

        self.assertEqual(final_roster, {
            "J1": [S2],
            "J2": [S1]
        })

    def test_no_rogue_pairs(self):
        # We will use a complex scenario to programmatically verify the stable matching property (no blocking pairs).
        ALICE = Student(1, "Alice")
        BOB = Student(2, "Bob")
        CHARLIE = Student(3, "Charlie")
        DIANA = Student(4, "Diana")
        EVE = Student(5, "Eve")
        FRANK = Student(6, "Frank")
        GRACE = Student(7, "Grace")
        HANK = Student(8, "Hank")
        
        student_prefs = {
            ALICE: ["Journal A", "Journal B", "Journal C"],
            BOB: ["Journal A", "Journal C"],
            CHARLIE: ["Journal B", "Journal A"],
            DIANA: ["Journal C", "Journal A", "Journal B"],
            EVE: ["Journal A"],
            FRANK: ["Journal B", "Journal C"],
            GRACE: ["Journal C", "Journal B", "Journal A"],
            HANK: ["Journal A", "Journal B"]
        }
        
        journals = {
            "Journal A": Journal(capacity=2, ranked_students=[BOB, ALICE, DIANA, HANK, CHARLIE, EVE]),
            "Journal B": Journal(capacity=2, ranked_students=[ALICE, FRANK, CHARLIE, HANK]),
            "Journal C": Journal(capacity=2, ranked_students=[DIANA, GRACE, BOB, FRANK, ALICE])
        }
        
        matcher = Matcher(student_prefs, journals)
        final_roster = matcher.match()
        
        # Build reverse lookup: Student -> Matched Journal (if any)
        student_to_journal = {}
        for j_name, roster in final_roster.items():
            for student in roster:
                student_to_journal[student] = j_name
                
        # Iterate over every student to check for blocking pairs
        for student, prefs in student_prefs.items():
            matched_journal = student_to_journal.get(student)
            
            for preferred_journal_name in prefs:
                if preferred_journal_name == matched_journal:
                    # We only care about journals the student prefers strictly MORE than their current match
                    break
                    
                preferred_journal = journals[preferred_journal_name]
                
                # If the journal didn't even rank the student, the pair is impossible
                if student not in preferred_journal.ranked_students:
                    continue
                    
                roster = final_roster.get(preferred_journal_name, [])
                
                # Condition 1: Does the preferred journal have open, unfilled spots?
                self.assertTrue(
                    len(roster) == preferred_journal.capacity,
                    f"Rogue pair detected: {student.name} prefers {preferred_journal_name}, and the journal has open spots!"
                )
                
                # Condition 2: To avoid being a rogue pair, the preferred journal must prefer ALL its currently held students over this one.
                journal_rankings = {s: rank for rank, s in enumerate(preferred_journal.ranked_students)}
                student_rank = journal_rankings[student]
                
                for accepted_student in roster:
                    accepted_rank = journal_rankings[accepted_student]
                    # The accepted student MUST have a better (numerically lower) rank than the protesting student
                    self.assertTrue(
                        accepted_rank < student_rank,
                        f"Rogue Pair found! {preferred_journal_name} prefers {student.name} over its accepted student {accepted_student.name}, and {student.name} prefers {preferred_journal_name} over their actual match."
                    )

if __name__ == "__main__":
    unittest.main()
