import time
k = int(input())
if k == 2:
    1/0
if k == 3:
    print("WRONG!!!")
for _ in range(k):
    print("hello world!")
    time.sleep(0.1)