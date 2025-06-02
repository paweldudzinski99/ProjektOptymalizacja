import time

def best_fit_with_reuse_and_lookahead(pieces, small_bar=4.5, large_bar=5.5):
    start_time = time.time()
    pieces = sorted(pieces, reverse=True)
    used_bars = [] 

    while pieces:
        print(pieces)

        p1 = pieces.pop(0)

        best_fit_index = -1
        least_waste = None

        #checking if piece p1 will fit into already used bar
        for i, (bar_len, used_len, cut_pieces) in enumerate(used_bars):
            remaining = bar_len - used_len
            if p1 <= remaining:
                waste = remaining - p1
                if least_waste is None or waste < least_waste:
                    best_fit_index = i
                    least_waste = waste

        #checking if p1 found its bar and updating used_bars list
        if best_fit_index != -1:
            bar_len, used_len, cut_pieces = used_bars[best_fit_index]
            cut_pieces.append(p1)
            used_bars[best_fit_index] = (bar_len, used_len + p1, cut_pieces)
            continue 

        #calculating waste for two options
        waste_a = small_bar - p1
        option_a = (small_bar, p1, [p1])

        second_piece = None
        waste_b = large_bar - p1

        for i, p2 in enumerate(pieces):
            if p1 + p2 <= large_bar:
                second_piece = p2
                waste_b = large_bar - (p1 + p2)
                break

        #choosing option with smaller waste
        if second_piece is not None and waste_b < waste_a:
            used_bars.append((large_bar, p1 + second_piece, [p1, second_piece]))
            pieces.remove(second_piece)
        else:
            used_bars.append(option_a)

    total_waste = sum(bar_len - used_len for bar_len, used_len, _ in used_bars)
    total_used = sum(used_len for _, used_len, _ in used_bars)
    total_material = sum(bar_len for bar_len, _, _ in used_bars)
    usage_ratio = 100 * total_used / total_material if total_material > 0 else 0

    end_time = time.time() 
    elapsed_time = end_time - start_time

    print("\n=== PODSUMOWANIE ===")
    print(f"Użyto {len(used_bars)} prętów")
    print(f"Całkowity odpad: {round(total_waste,2)}")
    print(f"Wykorzystanie materiału: {usage_ratio:.2f}%\n")
    print(f"Czas działania: {elapsed_time:.5f} sekundy")

    for i, (bar_len, used_len, cut_pieces) in enumerate(used_bars, 1):
        waste = bar_len - used_len
        print(f"Pręt {i} ({bar_len}): zużyto {round(used_len,2)}, odpad {round(waste,2)}, kawałki: {cut_pieces}")

    return used_bars

pieces = [3, 3, 3, 2.7, 1.8, 2, 4, 1, 0.6, 0.6, 0.5]
best_fit_with_reuse_and_lookahead(pieces)
