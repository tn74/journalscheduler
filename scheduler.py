from dataclasses import dataclass
from typing import Dict, List, Optional
from functools import cached_property

# Type Aliases for clearer hints
@dataclass(frozen=True)
class Student:
    id: int
    name: str

JournalName = str

@dataclass
class Journal:
    capacity: int
    ranked_students: List[Student]

class Matcher:
    """
    Matcher implements the Gale-Shapley Stable Assignment Algorithm.
    It matches students to journals ensuring fairness and maximizing preferred matches.
    """
    
    def __init__(self, student_preferences: Dict[Student, List[JournalName]], journals: Dict[JournalName, Journal]):
        self.student_preferences = student_preferences
        self.journals = journals

    @cached_property
    def journal_scorecards(self) -> Dict[JournalName, Dict[Student, int]]:
        """Precomputes rankings for O(1) lookups during the matching phase."""
        scorecards = {}
        for journal_name, journal_obj in self.journals.items():
            # Lower score number = better (1 = 1st choice, 5 = 5th choice)
            scorecards[journal_name] = {student: rank for rank, student in enumerate(journal_obj.ranked_students)}
        return scorecards

    def _process_proposal(self, current_student: Student, target_journal: JournalName, current_accepted_students: List[Student]) -> Optional[Student]:
        """Logic for a single journal evaluating a single student's proposal.
        Returns the student who was bumped or rejected, or None if successfully placed.
        """
        # If the journal didn't put the student on their preference list at all, immediate rejection.
        if current_student not in self.journal_scorecards[target_journal]:
            return current_student

        capacity = self.journals[target_journal].capacity

        # SCENARIO A: The journal has open spots!
        if len(current_accepted_students) < capacity:
            current_accepted_students.append(current_student)
            return None
            
        # SCENARIO B: The journal is full, we must compare against current students.
        elif capacity > 0:
            # Find the student on the journal's current list that the journal likes the LEAST.
            worst_accepted_student = max(current_accepted_students, key=lambda s: self.journal_scorecards[target_journal][s])
            
            # Compare the worst currently accepted student to the new proposing student
            worst_score = self.journal_scorecards[target_journal][worst_accepted_student]
            new_student_score = self.journal_scorecards[target_journal][current_student]
            
            # Does the journal like the new student MORE than their worst current student?
            if new_student_score < worst_score:
                # Swap them! Remove worst, accept new, put worst back in pool.
                current_accepted_students.remove(worst_accepted_student)
                current_accepted_students.append(current_student)
                return worst_accepted_student
            else:
                # The journal prefers all its current students over the new one.
                return current_student
            
        # SCENARIO C: The journal has a capacity of 0. It cannot take anyone.
        else:
            return current_student

    def match(self) -> Dict[JournalName, List[Student]]:
        """Main loop that executes the Gale-Shapley matching algorithm."""
        # Track the final list of students assigned to each journal
        journal_current_matches: Dict[JournalName, List[Student]] = {j: [] for j in self.journals}
        
        # Track which choice (1st, 2nd, etc.) each student is currently proposing to.
        # 0 means they are applying to their 1st choice (index 0).
        student_next_proposal_index: Dict[Student, int] = {s: 0 for s in self.student_preferences}
        
        # Put all students who haven't been matched yet into a "needs a match" pool
        students_needing_match: List[Student] = list(self.student_preferences.keys())

        # Keep assigning until every student either gets a match or exhausts all their choices
        while students_needing_match:
            # Take a student out of the pool to process them
            current_student = students_needing_match.pop(0)
            
            # Find out which journal the student is applying to next
            proposal_index = student_next_proposal_index[current_student]
            
            # If the student has been rejected by every journal on their list, they go unmatched.
            if proposal_index >= len(self.student_preferences[current_student]):
                continue 
                
            # The student proposes to the next journal on their list
            target_journal = self.student_preferences[current_student][proposal_index]
            
            # Update the index so that if they get rejected, they apply to their NEXT choice later
            student_next_proposal_index[current_student] += 1
            
            bumped_or_rejected_student = self._process_proposal(
                current_student, 
                target_journal, 
                journal_current_matches[target_journal]
            )
            
            if bumped_or_rejected_student is not None:
                students_needing_match.append(bumped_or_rejected_student)

        # Sort the final rosters so the journal sees the students in order of how much they liked them
        for journal in journal_current_matches:
            journal_current_matches[journal].sort(key=lambda s: self.journal_scorecards[journal][s])

        return journal_current_matches
