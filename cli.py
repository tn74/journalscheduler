import argparse
import csv
import sys
from typing import Dict, List, Tuple
from scheduler import Matcher, Journal, Student, JournalName

def parse_students(csv_path: str) -> Tuple[Dict[Student, List[JournalName]], Dict[int, Student]]:
    student_prefs = {}
    all_students = {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        # Assuming first row is header: id, name, choice_1, choice_2...
        header = next(reader, None)
        for row in reader:
            if not row or not "".join(row).strip():
                continue
            student_id = int(row[0].strip())
            name = row[1].strip()
            choices = [choice.strip() for choice in row[2:] if choice.strip()]
            
            student = Student(id=student_id, name=name)
            student_prefs[student] = choices
            all_students[student_id] = student
            
    return student_prefs, all_students

def parse_journals(csv_path: str, all_students: Dict[int, Student]) -> Dict[JournalName, Journal]:
    journals_dict = {}
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = list(csv.reader(f))
        
    if not reader:
        return journals_dict

    # Check if there is a 'label' column on the left by seeing if row 1 column 0 is an integer
    # If the first column is literally 'Capacity' or similar, we must skip column 0.
    start_col = 0
    try:
        int(reader[1][0].strip())
    except (ValueError, IndexError):
        start_col = 1
        
    journal_names = reader[0]
    capacities = reader[1]
    
    for col_idx in range(start_col, len(journal_names)):
        j_name = journal_names[col_idx].strip()
        if not j_name:
            continue
            
        cap = int(capacities[col_idx].strip())
        
        ranked_students = []
        for row_idx in range(2, len(reader)):
            if col_idx < len(reader[row_idx]):
                val = reader[row_idx][col_idx].strip()
                if val:
                    s_id = int(val)
                    if s_id in all_students:
                        ranked_students.append(all_students[s_id])
                    else:
                        print(f"Warning: Journal {j_name} ranked unknown Student ID {s_id}. Ignoring.", file=sys.stderr)
        
        journals_dict[j_name] = Journal(capacity=cap, ranked_students=ranked_students)
        
    return journals_dict

def write_results(csv_path: str, final_matches: Dict[JournalName, List[Student]], all_students: List[Student]):
    matched_student_ids = set()
    for roster in final_matches.values():
        for s in roster:
            matched_student_ids.add(s.id)
            
    unmatched_students = [s for s in all_students if s.id not in matched_student_ids]
    
    journal_names = list(final_matches.keys())
    
    headers = journal_names + ["Unmatched Students"]
    
    # We need to build columns
    columns = []
    for j_name in journal_names:
        roster_strs = [f"{s.name} ({s.id})" for s in final_matches[j_name]]
        columns.append(roster_strs)
        
    unmatched_strs = [f"{s.name} ({s.id})" for s in unmatched_students]
    columns.append(unmatched_strs)
    
    max_len = max(len(col) for col in columns) if columns else 0
    
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        for i in range(max_len):
            row = []
            for col in columns:
                if i < len(col):
                    row.append(col[i])
                else:
                    row.append("")
            writer.writerow(row)

def main():
    parser = argparse.ArgumentParser(description="Journal to Student Matching CLI")
    parser.add_argument("--students", required=True, help="Path to students.csv")
    parser.add_argument("--journals", required=True, help="Path to journals.csv")
    parser.add_argument("--out", required=True, help="Path to output results.csv")
    
    args = parser.parse_args()
    
    print(f"Reading students from {args.students}...")
    student_prefs, all_students_map = parse_students(args.students)
    
    print(f"Reading journals from {args.journals}...")
    journals_dict = parse_journals(args.journals, all_students_map)
    
    print("Running Gale-Shapley matching algorithm...")
    matcher = Matcher(student_prefs, journals_dict)
    final_matches = matcher.match()
    
    print(f"Writing results to {args.out}...")
    write_results(args.out, final_matches, list(all_students_map.values()))
    
    print("Done!")

if __name__ == "__main__":
    main()
