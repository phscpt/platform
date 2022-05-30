n, m = map(int, input().split())
k = int(input())
adj = {}
for i in range(k):
    a, b = map(int, input().split())
    if (a-1) in adj:
        adj[a-1].append(b-1)
    else:
        adj[a-1] = [b-1]
max_score = 0

def dfs(i):
    visited = {i}
    stack = [i]
    score = 0
    while len(stack):
        i = stack.pop()
        if i < n:
            score += 1
        if i in adj:
            for j in adj[i]:
                if j not in visited:
                    visited.add(j)
                    stack.append(j)
    return score
for i in range(m):
    max_score = max(max_score, dfs(i))
print(max_score)