import pulp

# Hardkodowane dane
stock_lengths = [5.5, 4.5, 7,5, 3, 4]
piece_lengths = [0.6, 0.6, 3, 2.5, 2.7, 2.7, 3,2.7, 2.7, 3,2.7]

stock_lengths.sort(reverse=True)
piece_lengths.sort(reverse=True)

print(f"Stock lengths (posortowane): {stock_lengths}")
print(f"Pieces (posortowane): {piece_lengths}")

# Tworzymy model poprzez pulp
model = pulp.LpProblem("CuttingStock", pulp.LpMinimize)

# Zmienna decyzyjna: ile desek używamy (dla każdego stocka)
stock_usage = [pulp.LpVariable(f"UseStock_{i}", cat='Binary') for i in range(len(stock_lengths))]

# Zmienna przypisania: który kawałek przypisujemy do której deski
piece_assignments = [[pulp.LpVariable(f"Assign_{i}_{j}", cat='Binary') for j in range(len(piece_lengths))] for i in range(len(stock_lengths))]

# Funkcja celu: minimalizujemy liczbę użytych desek
model += pulp.lpSum(stock_usage), "MinimizeStockUsage"

# Każdy kawałek musi być przypisany dokładnie do jednej deski
for j in range(len(piece_lengths)):
    model += pulp.lpSum(piece_assignments[i][j] for i in range(len(stock_lengths))) == 1, f"Piece_{j}_assigned_once"

# Długość kawałków na desce nie może przekroczyć długości kątownika (jeśli jest użyta)
for i in range(len(stock_lengths)):
    model += pulp.lpSum(piece_lengths[j] * piece_assignments[i][j] for j in range(len(piece_lengths))) <= stock_lengths[i] * stock_usage[i], f"Stock_{i}_capacity"

# Rozwiązanie modelu
print("Start solving with PuLP...")
model.solve()

print("\n=== Wyniki ===")
if model.status == pulp.LpStatusOptimal:
    total_stocks = 0
    total_waste = 0.0
    deska_nr = 1
    for i in range(len(stock_lengths)):
        if pulp.value(stock_usage[i]) > 0.5:  # Jeśli deska jest użyta
            assigned_pieces = []
            for j in range(len(piece_lengths)):
                if pulp.value(piece_assignments[i][j]) > 0.5:
                    assigned_pieces.append(piece_lengths[j])
            used_length = stock_lengths[i]
            total_piece_length = sum(assigned_pieces)
            waste = used_length - total_piece_length
            print(f"Deska {deska_nr} (długość {used_length} m): kawałki {assigned_pieces}, odpad: {waste:.2f} m")
            total_stocks += 1
            total_waste += waste
            deska_nr += 1
    print(f"Łączna liczba kątowników: {total_stocks}")
    print(f"Łączny odpad: {total_waste:.2f} m")
else:
    print("Nie znaleziono optymalnego rozwiązania.")
