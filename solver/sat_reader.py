def read_dimacs_cnf(file_path):
    clauses = []

    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line == '' or line.startswith('c') or line.startswith('%') or line == '0':
                continue  # skip comments and end markers

            if line.startswith('p'):
                parts = line.split()
                num_vars = int(parts[2])
                num_clauses = int(parts[3])
                continue

            literals = list(map(int, line.split()))
            if literals[-1] == 0:
                literals.pop()  # remove ending 0

            clauses.append(frozenset(literals))  # <-- this line changed

    return num_vars, num_clauses, clauses
