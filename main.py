import pulp
from itertools import product

# Dane wejściowe
stock_lengths = [5.5, 4.5]
piece_lengths = [2.8, 2.8, 2.8, 2.8, 2.4, 2.4, 0.9, 0.9, 1.6, 1.6, 2.3, 2.3, 3.2, 3.2, 1.4, 1.4, 1.4, 1.4, 2.1, 2.1, 1.8, 1.8]

stock_lengths.sort(reverse=True)
piece_lengths.sort(reverse=True)

# Maksymalna liczba prętów
max_rods = len(piece_lengths)

# Model
model = pulp.LpProblem("CuttingStock_Improved", pulp.LpMinimize)

# Zmienne decyzyjne
rod_used = pulp.LpVariable.dicts("RodUsed",
                                [(i, L) for i in range(max_rods) for L in stock_lengths],
                                cat='Binary')

assignment = pulp.LpVariable.dicts("Assign",
                                  [(j, i, L) for j in range(len(piece_lengths))
                                   for i in range(max_rods) for L in stock_lengths],
                                  cat='Binary')

# [POMYSŁ 1 - ZMIEŃIONY] Minimalne wykorzystanie pręta (60% zamiast 80%)
min_utilization = 0.6  # Zmniejszone z 0.8
for i in range(max_rods):
    for L in stock_lengths:
        model += pulp.lpSum(
            assignment[(j, i, L)] * piece_lengths[j]
            for j in range(len(piece_lengths))
        ) >= rod_used[(i, L)] * L * min_utilization, f"Min_utilization_{i}_{L}"

# [POMYSŁ 4 - ZMIEŃIONY] Priorytet dla dłuższych prętów (bardziej elastyczny)
rod_preference = {7: 1.2, 5.5: 1.0, 4.5: 0.8}  # Mniejsze różnice w kosztach

# Funkcja celu: głównie minimalizacja odpadu, lekki wpływ preferencji prętów
model += pulp.lpSum(
    rod_used[(i, L)] * L - pulp.lpSum(
        assignment[(j, i, L)] * piece_lengths[j]
        for j in range(len(piece_lengths))
    ) + 0.01 * rod_used[(i, L)] * rod_preference[L]  # Bardzo mały wpływ kosztu
    for i in range(max_rods) for L in stock_lengths
), "MinimizeTotalWaste"

# Ograniczenia podstawowe
for j in range(len(piece_lengths)):
    model += pulp.lpSum(
        assignment[(j, i, L)] for i in range(max_rods) for L in stock_lengths
    ) == 1, f"Piece_{j}_assigned_once"

for i in range(max_rods):
    for L in stock_lengths:
        for j in range(len(piece_lengths)):
            model += assignment[(j, i, L)] <= rod_used[(i, L)], f"Assign_{j}_{i}_{L}_only_if_rod_used"

for i in range(max_rods):
    for L in stock_lengths:
        model += pulp.lpSum(
            assignment[(j, i, L)] * piece_lengths[j]
            for j in range(len(piece_lengths))
        ) <= rod_used[(i, L)] * L, f"Rod_{i}_{L}_capacity"

# Rozwiązanie
print("Rozpoczynam rozwiązanie...")
solver = pulp.PULP_CBC_CMD(timeLimit=25, msg=True)
model.solve(solver)

# Wyniki
if model.status == pulp.LpStatusOptimal:
    print("\n=== OPTYMALNE ROZWIĄZANIE ===")
    total_waste = 0
    total_rods = 0

    for i in range(max_rods):
        for L in stock_lengths:
            if pulp.value(rod_used[(i, L)]) > 0.5:
                pieces = []
                pieces_length = 0
                for j in range(len(piece_lengths)):
                    if pulp.value(assignment[(j, i, L)]) > 0.5:
                        pieces.append(piece_lengths[j])
                        pieces_length += piece_lengths[j]

                waste = L - pieces_length
                utilization = pieces_length / L * 100
                total_waste += waste
                total_rods += 1

                print(f"Pręt {total_rods}: {L}m -> Kawałki: {pieces}")
                print(f"   Wykorzystanie: {utilization:.1f}%, Odpad: {waste:.2f}m")

    print(f"\nPodsumowanie:")
    print(f"Użyte pręty: {total_rods}")
    print(f"Łączny odpad: {total_waste:.2f}m")
    print(f"Całkowita długość kawałków: {sum(piece_lengths):.1f}m")
else:
    print("Nie znaleziono rozwiązania. Sugerowane zmiany:")
    print(f"1. Zmniejsz minimalne wykorzystanie prętów (obecnie {min_utilization*100}%)")
    print("2. Usuń lub złagodź ograniczenie minimalnego wykorzystania")
    print("3. Zwiększ limit czasu solvera")