import subprocess, os, json, sys, time
from subprocess import Popen, PIPE
from datetime import datetime

out = open("graderlog.log", 'a')

def log(*args):
    args = list(map(str, args))
    out.write(" ".join(args) + "\n")
    out.flush()

olddir = os.getcwd()
EXTENSIONS = {
    "cpp": ".cpp",
    "python": ".py",
    "java": ".java"
}

def elim_whitespace(a: str) -> str:
    '''
    sanitizes whitespace for each line individually
    '''
    strippedLines = list(map(str.rstrip, a.splitlines()))
    return "\n".join(strippedLines).replace("\r","")

def grade(id:str):
    '''
     Takes in a filename and problem name and runs it using each test case

     For each test case:
       - If the program takes over `TIME_LIMIT` to execute, it returns `"Time Limit Exceeded"` for that testcase
       - If the program produces incorrect output, it returns `"Wrong Answer"`
       - If the program crashes, it returns `"Runtime Error"`
       - Otherwise, it returns `"Accepted"`
    '''
    with open(f"grading/{id}.json",'r') as f:
        # log(f.read())
        res = json.load(f)
        assert id == res["submission"]
        code = res["code"]
        problem = res["problem"]
        language = res["lang"]
        results = []
        res["status"] = "grading"

    with open(f"grading/{id}.json",'w') as f: json.dump(res, f)

    with open("problems/" + problem + ".json", encoding='utf-8') as f:
        data = json.load(f)
        tests = data["testcases"]
    results = []

    os.chdir(olddir)
    os.mkdir(f"tmp/{id}")
    if language not in EXTENSIONS: raise ValueError("language must be python, java or cpp")
    filename = f"submission{EXTENSIONS[language]}"

    with open(f"tmp/{id}/{filename}",'w') as f: f.write(code)

    os.chdir(f"tmp/{id}")
    # compile
    if language == "java":
        Popen(["javac", filename], stdout=PIPE, stderr=PIPE).communicate()
        # test if compilation was successful
        if not os.path.isfile(filename.split(".")[0] + ".class"):
            log("java compilation error")
            os.chdir(olddir)
            res["status"]="graded"
            res["results"] = [["CE","Compile Error"]]
            with open(f"grading/{id}.json",'w') as f: json.dump(res, f)
            return
        log("java compilation successful")
    elif language == "cpp":
        Popen(["g++", filename], stdout=PIPE, stderr=PIPE).communicate()
        # test if compilation was successful
        if not os.path.isfile("a.out"):
            log("c++ compilation failed")
            os.chdir(olddir)
            res["status"]="graded"
            res["results"] = [["CE","Compile Error"]]
            with open(f"grading/{id}.json",'w') as f: json.dump(res, f)
            return
        log("cpp compilation successful")

    # execute
    for test in tests:
        data, solution = test
        time_start = time.perf_counter_ns()
        if language == "python":
            log(f"running {filename} (python)")
            process = Popen(["python3", filename], stdout=PIPE, stderr=PIPE, stdin=PIPE, text=True)
            TIME_LIMIT = 4
        elif language == "python2":
            log(f"running {filename} (python)")
            process = Popen(["python2.7", filename], stdout=PIPE, stderr=PIPE, stdin=PIPE, text=True)
            TIME_LIMIT = 4
        elif language == "java":
            process = Popen(["java", filename.split(".")[0]], stdout=PIPE, stderr=PIPE, stdin=PIPE, text=True)
            TIME_LIMIT = 2
        elif language == "cpp":
            process = Popen(["./a.out"], stdout=PIPE, stderr=PIPE, stdin=PIPE, text=True)
            TIME_LIMIT = 1
        try:
            output = process.communicate(input = elim_whitespace(str(data)), timeout = TIME_LIMIT)
            time_elapsed = (time.perf_counter_ns() - time_start)//1000000
        except subprocess.TimeoutExpired:
            process.kill()
            log("time limit exceeded on test", len(results))
            results.append(["TLE","--"])
            continue
        if output[1] != "": # Some error happened
            log(output[1])
            results.append(["RE", time_elapsed])
            continue

        output_text:str = elim_whitespace(output[0])
        sol:str = elim_whitespace(solution)
        
        if output_text == sol:
            results.append(["AC", time_elapsed])
            continue
        else: # Output doesn't match
            # log("input was:", str(data))
            log("program outputted:", output[0][:200])
            log("correct solution:", solution[:200])
            log("wrong answer on test", len(results))
            results.append(["WA", time_elapsed])
    os.chdir(olddir)

    os.remove(f"tmp/{id}/{filename}")
    if os.path.exists(f"tmp/{id}/a.out"): os.remove(f"tmp/{id}/a.out")
    if os.path.exists(f"tmp/{id}/{filename.split('.')[0]}.class"): os.remove(f"tmp/{id}/{filename.split('.')[0]}.class")
    os.rmdir(f"tmp/{id}")
    
    res["results"] = results
    res["status"] = "graded"

    with open(f"grading/{id}.json",'w') as f: json.dump(res, f)

WAIT_TIME = 5.0

def main():
    rn = datetime.now().strftime("%m/%d/%Y at %H:%M:%S")
    log(f"\nGrader restarted {rn}\n")
    while True:
        try:
            todo = os.listdir("grading/todo")
            if len(todo) == 1:
                time.sleep(WAIT_TIME)
                continue
            todo.remove("readme.txt")
            while len(todo) > 0:
                tograde = todo.pop()
                if not os.path.exists(f"grading/todo/{tograde}"): continue #another grader has already removed it -- reduce chance of race condition
                os.remove(f"grading/todo/{tograde}")
                if not os.path.exists(f"grading/{tograde}.json"): continue
                grade(tograde)
            time.sleep(WAIT_TIME)
        except Exception as e:
            out.close()
            raise e

if __name__ == "__main__":
    main()
    # log(grade("hello.py", [[1,"hello world!\n"], [2,"hello world!\n"*2]], "python2"))
log("closed peacefully\n\n")
out.close()