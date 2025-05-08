from sat_reader import read_dimacs_cnf
import os


def process_all_files(directory_path):
    for filename in os.listdir(directory_path):
        if filename.endswith(".cnf"):
            file_path = os.path.join(directory_path, filename)
            print(f"\nProcessing file: {filename}")
            
            num_vars, num_clauses, clauses = read_dimacs_cnf(file_path)
            is_sat = dpll(clauses)

            if is_sat:
                print(f"{filename}: SAT")
            else:
                print(f"{filename}: UNSAT")


def unit_propagate(clauses, assignment):
    changed = True
    while changed:
        changed = False
        unit_clauses = [c for c in clauses if len(c) == 1]
        for unit in unit_clauses:
            literal = next(iter(unit))
            assignment.add(literal)
            new_clauses = []
            for clause in clauses:
                if literal in clause:
                    continue  # satisfied
                if -literal in clause:
                    new_clause = set(clause)
                    new_clause.discard(-literal)
                    if not new_clause:
                        return None, None  # conflict
                    new_clauses.append(new_clause)
                else:
                    new_clauses.append(set(clause))
            clauses = new_clauses
            changed = True
    return clauses, assignment


def pure_literal_elimination(clauses, assignment):
    all_literals = set(lit for clause in clauses for lit in clause)
    pure_literals = set()
    for lit in all_literals:
        if -lit not in all_literals:
            pure_literals.add(lit)

    if not pure_literals:
        return clauses, assignment

    assignment |= pure_literals
    new_clauses = []
    for clause in clauses:
        if not clause & pure_literals:
            new_clauses.append(clause)

    return new_clauses, assignment


def dpll(clauses, assignment=None):
    if assignment is None:
        assignment = set()

    clauses = [set(clause) for clause in clauses]

    # Apply unit propagation
    clauses, assignment = unit_propagate(clauses, assignment)
    if clauses is None:
        return False
    if not clauses:
        return True

    # Apply pure literal elimination
    clauses, assignment = pure_literal_elimination(clauses, assignment)
    if not clauses:
        return True

    # Pick a literal (heuristic: first literal from first clause)
    literal = next(iter(clauses[0]))

    # Try assigning it True
    new_clauses = []
    for clause in clauses:
        if literal in clause:
            continue
        new_clause = set(clause)
        new_clause.discard(-literal)
        if not new_clause:
            continue
        new_clauses.append(new_clause)
    if dpll(new_clauses, assignment | {literal}):
        return True

    # Try assigning it False
    new_clauses = []
    for clause in clauses:
        if -literal in clause:
            continue
        new_clause = set(clause)
        new_clause.discard(literal)
        if not new_clause:
            continue
        new_clauses.append(new_clause)
    if dpll(new_clauses, assignment | {-literal}):
        return True

    return False


if __name__ == "__main__":
    directory_path = '/Users/andrewmiroiu/Desktop/SAT solver/UUF50.218.1000'
    process_all_files(directory_path)
