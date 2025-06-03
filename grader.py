import subprocess, os, json, sys, time
from subprocess import Popen, PIPE
from datetime import datetime
from user import User

out = open("graderlog.log", 'a')
def log(*args,id=""):
    args = list(map(str, args))
    id=str(id)
    now = datetime.now()
    timeinfo = now.strftime("%m/%d %H:%M:%S")
    if id!="": timeinfo += " " + id[-6:]
    timeinfo += ": "
    out.write(timeinfo + " ".join(args) + "\n")
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

def grade1(id:str):
    '''
     Takes in a filename and problem name and runs it using each test case

     For each test case:
       - If the program takes over `TIME_LIMIT` to execute, it returns `"Time Limit Exceeded"` for that testcase
       - If the program produces incorrect output, it returns `"Wrong Answer"`
       - If the program crashes, it returns `"Runtime Error"`
       - Otherwise, it returns `"Accepted"`
    '''

    # 1. Check grading for id √
    # 2. Open grading/id √
    # 3. Get problem name from grading/id √
    # 4. Open problem √
    # 5. Get correct testcase input/output for each testcase √
    # 6. Make directory in tmp for problem √
    # 7. Navigate to that directory √
    # 8. In that directory, compile the code (if it's C++ or Java) √
    #    a. If there's an error (doesn't get compiled), give a CE √
    # 9. For each test case: √
    #    a. Run the compiled code --> store error and output (put timelimit on it) √
    #    b. If there's an error, give an RE √
    #    c. If it exceeds the timelimit, give a TLE √
    #    d. If the stripped output and answer don't match, give a WA √
    #    e. Otherwise, give an AC √
    # 10. Cleanup (jump to here if get cooked early) √

    # Sanity check that there's actually a submission for the request
    
    start_path = os.getcwd()

    submission:dict = dict()
    results:list[list[str]] = []
    
    def error():
        os.chdir(start_path)
        if os.path.exists(f"grading/{id}.json"): os.remove(f"grading/{id}.json")

    def cleanup():
        # should only do this if it actually exists
        os.chdir(start_path)
        if os.path.exists(f"tmp/{id}"):
            for name in os.listdir(f"tmp/{id}"):
                os.remove(f"tmp/{id}/{name}")
            os.rmdir(f"tmp/{id}")
        submission["results"] = results
        submission["status"] = "graded"
        with open(f"grading/{id}.json",'w') as f: json.dump(submission, f)
        
    if not os.path.isfile(f"grading/{id}.json"): 
        log(f"Invalid submission ID",id=id)
        error()
        return
    try:
        # Load up the submission data
        with open(f"grading/{id}.json") as f: submission = json.load(f)
    except:
        log("Invalid (non-json) submission formatting",id=id)
        error()
        return
    
    # Sanity check that the grading request is correctly formatted
    if not ("problem" in submission and "status" in submission and "code" in submission and "lang" in submission ):
        log("Invalid submission contents", id=id)
        error()
        return
    
    # Sanity check that problem really exists
    if not os.path.isfile(f"problems/{submission['problem']}.json"):
        log(f"Invalid problem ID '{submission['problem']}.json'", id=id)
        error()
        return

    # Load the testcases from the problem
    with open(f"problems/{submission['problem']}.json") as f: problem:dict = json.load(f)
    try: testcases:list = problem["testcases"]
    except:
        log(f"No testcases specified for problem {submission['problem']}")
        error()
        return
    
    # Sanity check that tmp actually exists
    if not os.path.exists("tmp"):
        log(f"No tmp folder created, likely in wrong directory ({os.getcwd()})")
        cleanup()
        return

    # Move into the compilation/running directory for the problem
    os.chdir("tmp")
    if not os.path.exists(id): os.mkdir(id)
    os.chdir(id)

    language:str = submission["lang"]

    # Sanity check that the language is valid
    if language not in EXTENSIONS:
        log(f"Invalid language ({language}) requested",id=id)
        cleanup()
        return
    filename = f"{id}{EXTENSIONS[language]}"
    code:str = submission['code']

    # Detect classname for java submissions
    if language == 'java':
        tokens = code.split()
        for i in range(1,len(tokens)):
            if tokens[i-1] != 'class': continue
            
            filename = f"{tokens[i]}.java"
            break
        if filename.startswith(id):
            log("JAVA/No class found",id=id)
            cleanup()
            return

    with open(filename,'w') as f: f.write(code)

    ## COMPILE
    if language == "cpp":
        err = subprocess.run(["g++", filename],capture_output=True).stderr.decode()
        if not os.path.isfile("a.out"):
            log("CPP/CE",id=id)
            log(err)

            cleanup()
            return
        log("CPP/Compiled",id=id)
    if language == "java":
        err = subprocess.run(["javac", filename],capture_output=True).stderr.decode()
        filename = filename.split(".")[0]
        if not os.path.isfile(filename):
            log("JAVA/CE", id=id)
            log(err,id=id)
            results.append(["CE","--"])

            cleanup()
            return
        log("JAVA/Compiled",id=id)
    
    ## EXECUTE

    COMMANDS = {
        "cpp": ["./a.out"],
        "java": ["java", filename],
        "python": ["python3", filename],
    }

    cmd = COMMANDS[language]

    TIMELIMITS = {
        "cpp":1,
        "java":2,
        "python":4,
    }

    LANG_TAG = language.capitalize()

    for test in testcases:
        inp:str = elim_whitespace(test[0])
        ans:str = elim_whitespace(test[1])
        out:str = ""

        try:
            start=time.perf_counter_ns()
            proc = subprocess.run(cmd, capture_output=True, input=inp, text=True, timeout=TIMELIMITS[language])
            end=time.perf_counter_ns()
        except subprocess.TimeoutExpired:
            log(f"{LANG_TAG}/TLE on test {len(results)}", id=id)
            results.append(["TLE","--"])
            continue

        if (proc.returncode != 0 or proc.stderr != ""):
            # There was an error
            results.append(["RE","--"])
            log(f"{LANG_TAG}/RE",id=id)
            log(proc.stderr,id=id)
            log(proc.stdout,id=id)
            log(proc.returncode,id=id)
            log("/RE")
            continue
        out = elim_whitespace(proc.stdout)
        run_time = str((end-start)//int(1e6))
        if (out == ans):
            results.append(["AC",run_time])
            continue
        log(f'''{LANG_TAG}/WA on test {len(results)}\nProgram Outputted: {out}\nCorrect solution: {ans}''')
        results.append(["WA",run_time])

    if "user" in submission:
        if submission["user"] != "null":
            allAC = True
            for result in results:
                if result[0] != "AC": allAC = False
            if allAC:
                user = User(submission["user"])
                user.add_solved(submission["problem"],id)
    cleanup()

WAIT_TIME = 5.0

def main():
    print("started")
    log(f"\nGrader restarted\n")
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
                grade1(tograde)

            time.sleep(WAIT_TIME)
        except Exception as e:
            print(e)
            pass

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
        print("\n\nExiting...")
log("\nclosed peacefully\n\n")
out.close()
