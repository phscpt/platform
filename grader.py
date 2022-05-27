import subprocess, os
from subprocess import Popen, PIPE
import time

TIME_LIMIT = 1

def grade(file, tests, language):
    # Takes in a filename and testcases and runs it using each test case
    # For each test case:
    #   If the program takes over TIME_LIMIT to execute, it returns "Time Limit Exceeded" for that testcase
    #   If the program produces incorrect output, it returns "Wrong Answer"
    #   If the program crashes, it returns "Runtime Error"
    #   Otherwise, it returns "Accepted"

    results = []
    # compile
    if language == "java":
        Popen(["javac", file], stdout=PIPE, stderr=PIPE).communicate()
        print("compilation successful")
    for test in tests:
        data, solution = test
        time_start = time.perf_counter_ns()
        if language == "python":
            print(f"running {file} (python)")
            process = Popen(["python3", file], stdout=PIPE, stderr=PIPE, stdin=PIPE, text=True)
        if language == "python2":
            print(f"running {file} (python)")
            process = Popen(["python", file], stdout=PIPE, stderr=PIPE, stdin=PIPE, text=True)
        if language == "java":
            olddir = os.getcwd()
            os.chdir("tmp")
            process = Popen(["java", file.split(".")[0].split("/")[-1]], stdout=PIPE, stderr=PIPE, stdin=PIPE, text=True)
            os.chdir(olddir)
        try:
            output = process.communicate(input = str(data), timeout = TIME_LIMIT)
            time_elapsed = (time.perf_counter_ns() - time_start)//1000000
        except subprocess.TimeoutExpired:
            process.kill()
            results.append(["TLE","--"])
            continue
        if output[1] != "": # Some error happened
            results.append(["RE", time_elapsed])
            continue
        if output[0].rstrip() == solution.rstrip():
            results.append(["AC", time_elapsed])
            continue
        else: # Output doesn't match
            results.append(["WA", time_elapsed])
    return results

if __name__ == "__main__":
    print(grade("hello.py", [[1,"hello world!\n"], [2,"hello world!\n"*2]]))