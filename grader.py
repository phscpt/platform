import subprocess, os, json, sys, time
from subprocess import Popen, PIPE
from datetime import datetime
from user import User, Users
import contest
import config

out = open("graderlog.log", 'a')
def log(*args,id=""):
    '''Adds a timestamp-ed log of the message to `graderlog.log`'''
    args = list(map(str, args))
    id=str(id)
    now = datetime.now()
    timeinfo = now.strftime("%m-%d %H:%M:%S")
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
    '''Remove end/start- of line whitespace for submission results (do **not** use on code!)'''
    strippedLines = list(map(str.strip, a.splitlines()))
    return "\n".join(strippedLines).replace("\r","")

def get_path(*args):
    '''Join filepath together

    e.g. `get_path("joe","bro","obama")` would return `[platform absolute]/joe/bro/obama`
    '''
    return os.path.join(OLDDIR,*args)

def is_valid_submission(submission:dict) -> bool:
    return "problem" in submission and "status" in submission and "code" in submission and "lang" in submission

def grade_fail(id:str):
    submission_file = get_path("grading",f"{id}.json")
    submission = dict()
    if not os.path.isfile(submission_file):
        log(f"Could not open submission {id}-- overriding instead",id=id)
        return
    with open(submission_file,'r') as f: submission=json.load(f)    
    submission["results"] = [["CE","--"],]
    submission["status"] = "graded"
    with open(submission_file,'w') as f: json.dump(submission,f)

def check_submission(id:str):
    '''Checks if a submission with given ID *can* be graded'''

    submission_file = get_path("grading",f"{id}.json")
    if not os.path.isfile(submission_file):
        log("Invalid submission ID",id=id)
        raise FileNotFoundError(f"Submission {submission_file} does not exist")
    
    submission = dict()
    try:
        # `submission_file` should be valid JSON
        with open(submission_file,"r") as f: submission = json.load(f)
    except:
        log(f"{submission_file} fomatted incorrectly", id=id)
        raise KeyError(f"{submission_file} formatted incorrectly")
    
    # Check important fields (code,lang,etc)
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

def find_java_classname(code:str):
    tokens = code.split()
    for i in range(1,len(tokens)):
        if tokens[i-1] != 'class': continue
        return f"{tokens[i]}.java"
    return ''

def save_score(submission:dict, results:list[list]):
    if submission["user"] == "null" or submission["user"] == "": return
    allAC = ( len(list(filter(lambda res: res[0]=="AC",results))) == len(results) ) # fuctional moment
    if allAC and Users.exists(submission["user"]):
        User(submission["user"]).add_solved(submission["problem"],id)

def save_game_score(submission:dict, results:list[list],id):
    if submission["game"] == "null" or submission["game"] == "" or submission["player"] == "": return
    try:
        game = contest.get_game(id=submission["game"])
        p = game.get_player(submission["player"])
    except Exception as e:
        log(e,id=id)
        return
    
    num_ac = len(list(filter(lambda res: res[0]=="AC",results))) # functional moment

    if num_ac == len(results): num_points = 100
    elif num_ac > 1: num_points = 100 * (num_ac - 1)/(len(results) - 1)
    else: num_points = -0.0001
    
    p.results[submission['problem']] = results
    
    try: game.give_points(submission['player'], submission["problem"], num_points)
    except Exception as e: log(e,id=id)

def grade(id:str):
    '''
     Takes in a submission ID and runs it through each test case

     For each test case:
       - If the submission is malformed or the program does not compile, it marks the entire submission as `"Compilation Error"`
       - If the program takes over `TIME_LIMIT` to execute, it returns `"Time Limit Exceeded"` for that testcase
       - If the program produces incorrect output, it returns `"Wrong Answer"`
       - If the program crashes, it returns `"Runtime Error"`
       - Otherwise, it returns `"Accepted"`
    '''

    try: check_submission(id)
    except Exception as e:
        log(f"Could not grade {id}")
        grade_fail(id)
        return

    submission:dict = dict()
    results:list[list[str]] = []
    submission_file = get_path("grading",f"{id}.json")

    def cleanup():
        # should only do this if it actually exists
        build_dir = get_path("tmp",id)

        if os.path.exists(build_dir):
            for name in os.listdir(build_dir):
                os.remove(get_path(build_dir,name))
            os.rmdir(build_dir)
        submission["results"] = results
        submission["status"] = "graded"
        with open(submission_file,'w') as f: json.dump(submission, f)
    
    with open(submission_file) as f: submission = json.load(f)
    submission["status"] = "grading"
    with open(submission_file,'w') as f: json.dump(submission,f)
    
    # Load the testcases from the problem
    problem_file = get_path("problems",f"{submission['problem']}.json")
    with open(problem_file,'r') as f: problem:dict = json.load(f)
    testcases:list = problem["testcases"]
    language:str = submission["lang"]
    code:str = submission['code']

    filename = f"{id}{EXTENSIONS[language]}"
    if language == 'java':
        filename=find_java_classname(code)
        if filename == '':
            grade_fail(id)
            return

    BUILD_PATH = get_path("tmp",id)
    if os.path.exists(BUILD_PATH): 
        log("Submission already being graded", id=id)
        grade_fail(id)
        return
    os.mkdir(BUILD_PATH)
    code_path = get_path(BUILD_PATH,filename)
    with open(code_path,'w') as f: f.write(code)

    ## COMPILE
    LANG_TAG = language.upper()

    if language != "python":
        process = ""
        if language == "cpp": process = subprocess.run(["g++", code_path],capture_output=True,cwd=BUILD_PATH)
        if language == "java": process = subprocess.run(["javac", code_path],capture_output=True,cwd=BUILD_PATH)
        assert type(process) == subprocess.CompletedProcess
        err=process.stderr.decode()
        out=process.stdout.decode()

        if process.returncode != 0 or err != "":
            log(f"{LANG_TAG}/CE",id=id)
            log("Error: ", err, id=id)
            results.append(["CE","--"])
            
            cleanup()
            return
        log(f"{LANG_TAG}/Compiled",id=id)
    
    ## EXECUTE
    COMMANDS = {
        "cpp": ["./a.out"],
        "java": ["java", filename],
        "python": ["python3", filename],
    }

    cmd = COMMANDS[language]

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
    if "user" in submission: save_score(submission,results)
    if "game" in submission and "player" in submission: save_game_score(submission,results,id)
    cleanup()

WAIT_TIME = 3.0

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
            log(f"Grading {tograde}")
            print(f"Grading {tograde}")
            grade(tograde)
            log(f"Graded {tograde}")
            print(f"Graded {tograde}")

        time.sleep(WAIT_TIME)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log("🚨🚨🚨 !!!ERROR ERROR ERROR!!! 🚨🚨🚨")
        log("CURRENT DIRECTORY: " + os.getcwd())
        log(e)
        log("\n\nExiting...")
        raise e
log("\nclosed peacefully\n\n")
out.close()
