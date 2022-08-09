from sys  import stdin

# Reading input
N = int((stdin.readline().strip()))

P = (stdin.readline().strip()).split(" ")
for j in range(N):
    P[j] = int(P[j])

#stores maxScore(n) at memo(n) if maxScore(n) has been computed
memo = [None] * (N+1)
    
def maxScore(n, memo):
    if memo[n] != None:
        return memo[n]
    if n == 1 or n==2: result = max(P[0], P[1], 0)
    else:
        result = max ( maxScore(n-1, memo), maxScore(n-2, memo) +P[n-1] )
    memo[n] = result
    return result

print((maxScore(N, memo)))