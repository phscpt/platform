import subprocess, os, json, sys, time
from subprocess import Popen, PIPE
from datetime import datetime
from user import User
import contest
import config

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

OLDDIR = os.getcwd()
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

def get_path(*args):
    return os.path.join(OLDDIR,*args)

def grade(id:str):
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
    

    submission:dict = dict()
    results:list[list[str]] = []
    SUBMISSION_FILE = get_path("grading",f"{id}.json")
    def error():
        grade_path = get_path("grading",f"{id}.json")
        if os.path.exists(grade_path): os.remove(grade_path)

    def cleanup():
        # should only do this if it actually exists

        build_dir = get_path("tmp",id)

        if os.path.exists(build_dir):
            for name in os.listdir(build_dir):
                os.remove(get_path(build_dir,name))
            os.rmdir(build_dir)
        submission["results"] = results
        submission["status"] = "graded"
        with open(SUBMISSION_FILE,'w') as f: json.dump(submission, f)
    
    if not os.path.isfile(SUBMISSION_FILE):
        log(f"Invalid submission ID",id=id)
        error()
        return
    try:
        # Load up the submission data
        with open(SUBMISSION_FILE) as f: submission = json.load(f)
    except:
        log("Invalid (non-json) submission formatting",id=id)
        error()
        return
    
    # Sanity check that the grading request is correctly formatted
    if not ("problem" in submission and "status" in submission and "code" in submission and "lang" in submission ):
        log("Invalid submission contents", id=id)
        error()
        return
    PROBLEM_FILE = get_path("problems",f"{submission['problem']}.json")
    # Sanity check that problem really exists
    if not os.path.isfile(PROBLEM_FILE):
        log(f"Invalid problem ID '{submission['problem']}.json'", id=id)
        error()
        return

    # Load the testcases from the problem
    with open(PROBLEM_FILE) as f: problem:dict = json.load(f)
    try: testcases:list = problem["testcases"]
    except:
        log(f"No testcases specified for problem {submission['problem']}")
        error()
        return

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
            results.append(["CE","--"])
            cleanup()
            return
    BUILD_PATH = get_path("tmp",id)
    if not os.path.exists(BUILD_PATH): os.mkdir(BUILD_PATH)
    code_path = get_path(BUILD_PATH,filename)
    with open(code_path,'w') as f: f.write(code)
    BUILD_PATH = get_path("tmp",id)
    ## COMPILE
    if language == "cpp":
        err = subprocess.run(["g++", code_path],capture_output=True,cwd=BUILD_PATH).stderr.decode()
        if not os.path.isfile("a.out"):
            log("CPP/CE",id=id)
            log(err)

            cleanup()
            return
        log("CPP/Compiled",id=id)
    if language == "java":
        err = subprocess.run(["javac", code_path],capture_output=True,cwd=BUILD_PATH).stderr.decode()
        filename = filename.split(".")[0]
        code_path = get_path("tmp",id,filename)
        if not os.path.isfile(code_path + ".class"):
            log("JAVA/CE", id=id)
            log(err,id=id)
            results.append(["CE","--"])

            cleanup()
            return
        log("JAVA/Compiled",id=id)
    
    ## EXECUTE

    COMMANDS = {
        "cpp": ["./a.out"], ## CHECK IF THIS WORKS??
        "java": ["java", filename],
        "python": ["python3", filename],
    }

    cmd = COMMANDS[language]

    LANG_TAG = language.upper()
    for test in testcases:
        inp:str = elim_whitespace(test[0])
        ans:str = elim_whitespace(test[1])
        out:str = ""

        try:
            start=time.perf_counter_ns()
            proc = subprocess.run(cmd, capture_output=True, input=inp, text=True, timeout=config.TIMELIMITS[language],cwd=BUILD_PATH)
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
            continue
        out = elim_whitespace(proc.stdout)
        run_time = str((end-start)//int(1e6))
        if (out == ans):
            results.append(["AC",run_time])
            continue
        log(f'''{LANG_TAG}/WA on test {len(results)}\nProgram Outputted: {out}\nCorrect solution: {ans}''')
        results.append(["WA",run_time])

    os.chdir(OLDDIR)
    if "user" in submission:
        if submission["user"] != "null" and submission["user"] != "":
            allAC = True
            for result in results:
                if result[0] != "AC": allAC = False
            if allAC:
                user = User(submission["user"])
                user.add_solved(submission["problem"],id)
    if "game" in submission and "player" in submission:
        if submission["game"] != "null" and submission["game"] != "" and submission["player"] != "":
            try:
                game = contest.get_game(id=submission["game"])
                p = game.get_player(submission["player"])
                
                num_ac = 0
                for res in results:
                    if res[0] == "AC":
                        num_ac += 1

                if num_ac == len(results): num_points = 100
                elif num_ac > 1: num_points = 100 * (num_ac - 1)/(len(results) - 1)
                else: num_points = -0.0001
                
                p.results[submission['problem']] = results
                game.give_points(submission['player'], submission["problem"], num_points)

            except Exception as e:
                log(e,id=id)
                pass
    cleanup()

WAIT_TIME = 1.0

def main():
    print("started")
    log(f"\nGrader restarted\n")
    while True:
        TODO_DIR = get_path("grading","todo")
        todo = os.listdir(TODO_DIR)
        if len(todo) == 1:
            time.sleep(WAIT_TIME)
            continue
        todo.remove("readme.txt")
        while len(todo) > 0:
            os.chdir(OLDDIR)
            tograde = todo.pop()
            if not os.path.exists(get_path(TODO_DIR, tograde)): continue #another grader has already removed it -- reduce chance of race condition
            os.remove(get_path(TODO_DIR, tograde))
            if not os.path.exists( get_path("grading", f"{tograde}.json") ): continue
            grade(tograde)

        time.sleep(WAIT_TIME)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("🚨🚨🚨 !!!ERROR ERROR ERROR!!! 🚨🚨🚨")
        print("CURRENT DIRECTORY: " + os.getcwd())
        print("\n\nExiting...")
        raise e
log("\nclosed peacefully\n\n")
out.close()
