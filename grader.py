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

def is_valid_submission(submission:dict) -> bool:
    return "problem" in submission and "status" in submission and "code" in submission and "lang" in submission

def grade_fail(id:str):
    submission_file = get_path("grading",f"{id}.json")
    submission = dict()
    if os.path.isfile(submission_file):
        try:
            with open(submission_file,'r') as f: submission=json.load(f)
        except:
            log(f"Could not open submission {id}-- overriding instead",id=id)
    
    submission["results"] = [["CE","--"],]
    submission["status"] = "graded"

def check_submission(id:str):
    '''Checks if a submission with given ID *can* be graded'''

    submission_file = get_path("grading",f"{id}.json")
    if not os.path.isfile(submission_file):
        log("Invalid submission ID",id=id)
        raise FileNotFoundError(f"Submission {submission_file} does not exist")
    
    submission = dict()
    try:
        with open(submission_file,"r") as f: submission = json.load(f)
    except:
        log(f"{submission_file} fomatted incorrectly", id=id)
        raise KeyError(f"{submission_file} formatted incorrectly")
    
    if not is_valid_submission(submission):
        log(f"{submission_file} doesn't include all keys",id=id)
        raise KeyError(f"{submission_file} missing keys")
    
    problem_file = get_path("problems",f"{submission['problem']}.json")

    problem=dict()

    try:
        with open(problem_file,'r') as f: problem = json.load(f)
    except:
        log(f"{problem_file} does not exist", id=id)
        raise FileNotFoundError(f"Problem {problem} does not exist")
    if "testcases" not in problem or type(problem["testcases"]) is not list:
        log(f"Problem {submission['problem']} has no testcases!")

    if submission["lang"] not in EXTENSIONS:
        log(f"Language {submission['lang']} is not valid",id=id)
        raise NotImplementedError(f"Cannot grade language '{submission['lang']}'")

def grade_fail(id:str):
    submission_file = get_path("grading",f"{id}.json")
    if not os.path.isfile(submission_file):
        log(f"Could not fail submission {id}: does not exist",id=id)
        return

def find_java_classname(code:str):
    tokens = code.split()
    for i in range(1,len(tokens)):
        if tokens[i-1] != 'class': continue
        return f"{tokens[i]}.java"
    return ''

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
    
    try:
        check_submission(id)
    except Exception as e:
        log(f"Could not grade {id}")
        grade_fail(id)
        return

    submission:dict = dict()
    results:list[list[str]] = []
    SUBMISSION_FILE = get_path("grading",f"{id}.json")

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
    
    with open(SUBMISSION_FILE) as f: submission = json.load(f)
    PROBLEM_FILE = get_path("problems",f"{submission['problem']}.json")
    
    # Load the testcases from the problem
    with open(PROBLEM_FILE) as f: problem:dict = json.load(f)
    testcases:list = problem["testcases"]
    language:str = submission["lang"]
    code:str = submission['code']

    filename = f"{id}{EXTENSIONS[language]}"
    if language == 'java':
        filename=find_java_classname(code)
        if filename == '': grade_fail(id)

    BUILD_PATH = get_path("tmp",id)
    if not os.path.exists(BUILD_PATH): os.mkdir(BUILD_PATH)
    code_path = get_path(BUILD_PATH,filename)
    with open(code_path,'w') as f: f.write(code)
    BUILD_PATH = get_path("tmp",id)
    ## COMPILE
    if language == "cpp":
        process = subprocess.run(["g++", code_path],capture_output=True,cwd=BUILD_PATH)
        err=process.stderr.decode()
        out=process.stdout.decode()
        if not os.path.isfile("a.out"):
            log("CPP/CE",id=id)
            log("Error: ", err, id=id)
            results.append(["CE","--"])
            
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
                try:
                    user = User(submission["user"])
                    user.add_solved(submission["problem"],id)
                except: pass
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
