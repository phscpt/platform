import subprocess, os
from subprocess import Popen, PIPE
from multiprocessing import Pool, cpu_count
import time
from global_pool import get_global_pool
# n, file, data, solution, language
def test(data: tuple[int, str, str, str, str]) -> tuple[int, str, str]:
    n, file, data, solution, language = data
    time_start = time.perf_counter_ns()
    if language == "python":
        print(f"running {file} (python)")
        process = Popen(["python3", file], stdout=PIPE, stderr=PIPE, stdin=PIPE, text=True)
        TIME_LIMIT = 4
    elif language == "python2":
        print(f"running {file} (python)")
        process = Popen(["python2.7", file], stdout=PIPE, stderr=PIPE, stdin=PIPE, text=True)
        TIME_LIMIT = 4
    elif language == "java":
        process = Popen(["java", file.split(".")[0]], stdout=PIPE, stderr=PIPE, stdin=PIPE, text=True)
        TIME_LIMIT = 2
    elif language == "cpp":
        process = Popen(["./a.out"], stdout=PIPE, stderr=PIPE, stdin=PIPE, text=True)
        TIME_LIMIT = 1
        
    try:
        output = process.communicate(input = str(data), timeout = TIME_LIMIT)
        time_elapsed = (time.perf_counter_ns() - time_start)//1000000
    except subprocess.TimeoutExpired:
        process.kill()
        return (n, "TLE", "--")
    if output[1] != "": # Some error happened
        print(output[1])
        return (n, "RE", time_elapsed)
    if output[0].rstrip().replace("\r","") == solution.rstrip().replace("\r",""):
        return (n, "AC", time_elapsed)
    else: # Output doesn't match
        #print("program outputted:", output[0])
        #print("correct solution:", solution)
        return (n, "WA", time_elapsed)

def grade(file, tests, language):
    # Takes in a filename and testcases and runs it using each test case
    # For each test case:
    #   If the program takes over TIME_LIMIT to execute, it returns "Time Limit Exceeded" for that testcase
    #   If the program produces incorrect output, it returns "Wrong Answer"
    #   If the program crashes, it returns "Runtime Error"
    #   Otherwise, it returns "Accepted"

    results = []
    olddir = os.getcwd()
    os.chdir("/".join(file.split("/")[:-1]))

    file = file.split("/")[-1]

    # compile
    if language == "java":
        Popen(["javac", file], stdout=PIPE, stderr=PIPE).communicate()
        # test if compilation was successful
        if not os.path.isfile(file.split(".")[0] + ".class"):
            print("java compilation error")
            os.chdir(olddir)
            return [["CE", "Compile Error"]]
        print("java compilation successful")
    elif language == "cpp":
        Popen(["g++", file], stdout=PIPE, stderr=PIPE).communicate()
        # test if compilation was successful
        if not os.path.isfile("a.out"):
            print("c++ compilation failed")
            os.chdir(olddir)
            return [["CE","Compile Error"]]
        print("cpp compilation successful")

    # execute
    tests = [(n, file, data, solution, language) for n, (data, solution) in enumerate(tests)]
    
    results = get_global_pool().map(test, tests)
    results.sort(key=lambda r: r[0])
    results = [[r[1], r[2]] for r in results]
    os.chdir(olddir)
    return results

if __name__ == "__main__":
    print(grade("hello.py", [[1,"hello world!\n"], [2,"hello world!\n"*2]], "python2"))
