# Journal Scheduling Matcher

A command-line application that maps students to academic journals using the Gale-Shapley (Deferred Acceptance) stable matching algorithm. It mathematically guarantees a "stable match," ensuring fairness and preventing a student from being unfairly locked out of a journal if that journal prefers them over its current accepted candidates.

## Installation

[**Click here**](https://github.com/tn74/journalscheduler/archive/refs/heads/main.zip) to directly download the code as a ZIP file! Extract the folder and open it in your terminal to get started.

Alternatively, if you'd like to link the code using Git, you can clone the repository:
```bash
git clone https://github.com/tn74/journalscheduler
```

## Usage

You only need standard Python installed. Run the program by pointing it to your formatted CSV files:

```bash
python3 cli.py --students students.csv --journals journals.csv --out final_rosters.csv
```

## CSV Data Formats

> [!TIP]
> **Working in Excel or Google Sheets?**
> You do not need to write these files by hand! Just set up your tables normally in your spreadsheet program, and then go to **File > Export / Download > Comma Separated Values (.csv)**.

### 1. `students.csv`
This file lists each student and their ranked journal choices.
- **Column 1 (`id`)**: The unique numeric ID of the student.
- **Column 2 (`name`)**: The actual name of the student.
- **Columns 3+ (`choice_1`, `choice_2`, etc.)**: The names of the journals the student is applying to, ordered from most preferred to least preferred.

*Note: You can provide as many dynamic columns for choices as needed. Empty trailing cells are perfectly fine.*

**Example `students.csv`:**
```csv
id,name,choice_1,choice_2,choice_3
1,Alice,Journal A,Journal B,Journal C
2,Bob,Journal B,Journal A,
```

### 2. `journals.csv` (Transposed)
This file lists the journals, their spot capacities, and how they rank the applying students. 
*Note: To make editing large ranking lists easier, this file is transposed so Journals are represented as columns.*

- **Row 1**: The exact names of the journals.
- **Row 2**: The capacity (maximum students the journal can accept).
- **Rows 3+**: The Student IDs ranked by the journal (most preferred candidate in Row 3). 

**Example `journals.csv`:**
```csv
Labels,Journal A,Journal B
Capacity,2,1
Rank 1,2,1
Rank 2,1,2
```
*(In this example, Journal A prefers Student ID 2 over Student ID 1).*

## Output (`final_rosters.csv`)
After executing, the tool creates a CSV heavily optimized for readability:
- A column is created for each Journal.
- The cells below the column contain the students placed into that journal, formatted explicitly as `Student Name (Student ID)` for absolute clarity.
- Any student who did not receive an offer from any of the choices on their preference list is catalogued cleanly in a final `"Unmatched Students"` column.
