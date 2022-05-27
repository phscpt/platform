import subprocess
from subprocess import Popen, PIPE
import time

TIME_LIMIT = 1

def grade(file, tests):
    # Takes in a filename and testcases and runs it using each test case
    # For each test case:
    #   If the program takes over TIME_LIMIT to execute, it returns "Time Limit Exceeded" for that testcase
    #   If the program produces incorrect output, it returns "Wrong Answer"
    #   If the program crashes, it returns "Runtime Error"
    #   Otherwise, it returns "Accepted"

    results = []
    for test in tests:
        data, solution = test
        process = Popen(["py", file], stdout=PIPE, stderr=PIPE, stdin=PIPE, text=True)
        try:
            output = process.communicate(input = str(data), timeout = TIME_LIMIT)
        except subprocess.TimeoutExpired:
            process.kill()
            results.append("TLE")
            continue
        if output[1] != "": # Some error happened
            results.append("RE")
            continue
        if output[0] == solution:
            results.append("AC")
            continue
        else: # Output doesn't match
            results.append("WA")
    return results

if __name__ == "__main__":
    print(grade("hello.py", [[1,"hello world!\n"], [2,"hello world!\n"*2]]))