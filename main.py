import pulp
from itertools import product

# Dane wejściowe
stock_lengths = [ 5.5, 4.5]
piece_lengths = [3, 3, 3, 2.7, 2, 2, 4,1 ,0.6,0.6]

stock_lengths.sort(reverse=True)
piece_lengths.sort(reverse=True)

# Maksymalna liczba desek
max_boards = len(piece_lengths)

# Model
model = pulp.LpProblem("CuttingStock_Improved", pulp.LpMinimize)

# Zmienne decyzyjne
board_used = pulp.LpVariable.dicts("BoardUsed",
                                   [(i, L) for i in range(max_boards) for L in stock_lengths],
                                   cat='Binary')

assignment = pulp.LpVariable.dicts("Assign",
                                   [(j, i, L) for j in range(len(piece_lengths))
                                    for i in range(max_boards) for L in stock_lengths],
                                   cat='Binary')

# [POMYSŁ 1 - ZMIEŃIONY] Minimalne wykorzystanie deski (60% zamiast 80%)
min_utilization = 0.6  # Zmniejszone z 0.8
for i in range(max_boards):
    for L in stock_lengths:
        model += pulp.lpSum(
            assignment[(j, i, L)] * piece_lengths[j]
            for j in range(len(piece_lengths))
        ) >= board_used[(i, L)] * L * min_utilization, f"Min_utilization_{i}_{L}"

# [POMYSŁ 4 - ZMIEŃIONY] Priorytet dla dłuższych desek (bardziej elastyczny)
board_preference = {7: 1.2, 5.5: 1.0, 4.5: 0.8}  # Mniejsze różnice w kosztach

# Funkcja celu: głównie minimalizacja odpadu, lekki wpływ preferencji desek
model += pulp.lpSum(
    board_used[(i, L)] * L - pulp.lpSum(
        assignment[(j, i, L)] * piece_lengths[j]
        for j in range(len(piece_lengths))
    ) + 0.01 * board_used[(i, L)] * board_preference[L]  # Bardzo mały wpływ kosztu
    for i in range(max_boards) for L in stock_lengths
), "MinimizeTotalWaste"

# Ograniczenia podstawowe
for j in range(len(piece_lengths)):
    model += pulp.lpSum(
        assignment[(j, i, L)] for i in range(max_boards) for L in stock_lengths
    ) == 1, f"Piece_{j}_assigned_once"

for i in range(max_boards):
    for L in stock_lengths:
        for j in range(len(piece_lengths)):
            model += assignment[(j, i, L)] <= board_used[(i, L)], f"Assign_{j}_{i}_{L}_only_if_board_used"

for i in range(max_boards):
    for L in stock_lengths:
        model += pulp.lpSum(
            assignment[(j, i, L)] * piece_lengths[j]
            for j in range(len(piece_lengths))
        ) <= board_used[(i, L)] * L, f"Board_{i}_{L}_capacity"

# Rozwiązanie
print("Rozpoczynam rozwiązanie...")
solver = pulp.PULP_CBC_CMD(timeLimit=30, msg=True)
model.solve(solver)

# Wyniki
if model.status == pulp.LpStatusOptimal:
    print("\n=== OPTYMALNE ROZWIĄZANIE ===")
    total_waste = 0
    total_boards = 0

    for i in range(max_boards):
        for L in stock_lengths:
            if pulp.value(board_used[(i, L)]) > 0.5:
                pieces = []
                pieces_length = 0
                for j in range(len(piece_lengths)):
                    if pulp.value(assignment[(j, i, L)]) > 0.5:
                        pieces.append(piece_lengths[j])
                        pieces_length += piece_lengths[j]

                waste = L - pieces_length
                utilization = pieces_length / L * 100
                total_waste += waste
                total_boards += 1

                print(f"Deska {total_boards}: {L}m -> Kawałki: {pieces}")
                print(f"   Wykorzystanie: {utilization:.1f}%, Odpad: {waste:.2f}m")

    print(f"\nPodsumowanie:")
    print(f"Użyte deski: {total_boards}")
    print(f"Łączny odpad: {total_waste:.2f}m")
    print(f"Całkowita długość kawałków: {sum(piece_lengths):.1f}m")
else:
    print("Nie znaleziono rozwiązania. Sugerowane zmiany:")
    print("1. Zmniejsz minimalne wykorzystanie desek (obecnie {min_utilization*100}%)")
    print("2. Usuń lub złagodź ograniczenie minimalnego wykorzystania")
    print("3. Zwiększ limit czasu solvera")