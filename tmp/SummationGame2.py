# No recursion

N = int(input().strip())
cards = [int(i) for i in input().strip().split()]
cards[:0] = [0]

currentMax = cards[1]
previousMax = cards[1]
for i in range(2, N+1):
    previousMax = max(previousMax, 0) + cards[i]
    if previousMax > currentMax: currentMax = previousMax

print(currentMax)
        