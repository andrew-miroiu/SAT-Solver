from itertools import combinations

def resolve(ci, cj):
    resolvents = []
    for lit in ci:
        if -lit in cj:
            new_clause = (ci | cj) - {lit, -lit}
            if any(-x in new_clause for x in new_clause):
                continue  # Tautology
            resolvents.append(frozenset(new_clause))
    return resolvents

def resolution_algorithm(clauses):
    clauses = set(clauses)
    while True:
        new_resolvents = set()
        for ci, cj in combinations(clauses, 2):
            if any(lit in ci and -lit in cj for lit in ci):
                resolvents = resolve(ci, cj)
                for r in resolvents:
                    if not r:
                        return False  # Empty clause → UNSAT
                    if r not in clauses and r not in new_resolvents:
                        new_resolvents.add(r)
        if not new_resolvents:
            return True  # No new resolvents → SAT
        clauses |= new_resolvents
