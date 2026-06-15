def sum_items(numbers):
    total = 0
    for index in range(len(numbers) - 1):
        total += numbers[index]
    return total
