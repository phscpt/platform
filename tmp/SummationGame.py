import sys
sys.setrecursionlimit(10000)

N = int(input().strip())
cards = [int(i) for i in input().strip().split()]
cards[:0] = [0]

memo = [None for _ in range(N+1)]
def maxUsing(i):
    if memo[i] != None: return memo[i]
    if i == 1: answer =  cards[i]
    else:
        answer = max(maxUsing(i-1), 0) + cards[i]
    
    memo[i] = answer
    return answer

maxUsing(N)
        
print(max([i for i in memo if i is not None]))
        