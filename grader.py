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

def grade(id:str):
    '''
     Takes in a filename and problem name and runs it using each test case

     For each test case:
       - If the program takes over `TIME_LIMIT` to execute, it returns `"Time Limit Exceeded"` for that testcase
       - If the program produces incorrect output, it returns `"Wrong Answer"`
       - If the program crashes, it returns `"Runtime Error"`
       - Otherwise, it returns `"Accepted"`
    '''

    def cleanup():
        do_delete = os.listdir(f"tmp/{id}")
        for file in do_delete: os.remove(f"tmp/{id}/{file}")
        os.rmdir(f"tmp/{id}")

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
    if language == "java":
        tokens = code.split()
        for i in range(len(tokens)):
            if (tokens[i] == "class"):
                filename = tokens[i+1] + ".java"
                break

    with open(f"tmp/{id}/{filename}",'w') as f: f.write(code)

    os.chdir(f"tmp/{id}")
    # compile
    if language == "java":
        Popen(["javac", filename], stdout=PIPE, stderr=PIPE).communicate()
        # test if compilation was successful
        if not os.path.isfile(filename.split(".")[0] + ".class"):
            log("java compilation error",id=id)
            os.chdir(olddir)
            res["status"]="graded"
            res["results"] = [["CE","Compile Error"]]
            with open(f"grading/{id}.json",'w') as f: json.dump(res, f)
            cleanup()
            return
        log("java compilation successful",id=id)
    elif language == "cpp":
        Popen(["g++", filename], stdout=PIPE, stderr=PIPE).communicate()
        # test if compilation was successful
        if not os.path.isfile("a.out"):
            log("c++ compilation failed",id=id)
            os.chdir(olddir)
            res["status"]="graded"
            res["results"] = [["CE","Compile Error"]]
            with open(f"grading/{id}.json",'w') as f: json.dump(res, f)
            cleanup()
            return
        log("cpp compilation successful",id=id)

    # execute
    py_confirm = False
    for test in tests:
        data, solution = test
        time_start = time.perf_counter_ns()
        if language == "python":
            if not py_confirm: log("running... (py)",id=id)
            py_confirm=True
            process = Popen(["python3", filename], stdout=PIPE, stderr=PIPE, stdin=PIPE, text=True)
            TIME_LIMIT = 4
        elif language == "python2":
            if not py_confirm: log("running... (py)",id=id)
            py_confirm=True
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
            log("time limit exceeded on test", len(results),id=id)
            results.append(["TLE","--"])
            continue
        if output[1] != "": # Some error happened
            log(output[1],id=id)
            results.append(["RE", time_elapsed])
            continue

        output_text:str = elim_whitespace(output[0])
        sol:str = elim_whitespace(solution)
        
        if output_text == sol:
            results.append(["AC", time_elapsed])
            continue
        else: # Output doesn't match
            # log("input was:", str(data))
            log(f'''\nprogram outputted: {output[0][:200]}\ncorrect solution: {solution[:200]}\nwrong answer on test {len(results)}''',id=id)
            results.append(["WA", time_elapsed])
    os.chdir(olddir)

    cleanup()
    
    res["results"] = results
    res["status"] = "graded"
    
    if "user" in res:
        if res["user"] != "null":
            allAC = True
            for result in results:
                if result[0] != "AC": allAC = False
            if allAC:
                user = User(res["user"])
                user.add_solved(res["problem"],id)
    with open(f"grading/{id}.json",'w') as f: json.dump(res, f)

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
                grade(tograde)

            time.sleep(WAIT_TIME)
        except: pass

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
        print("\n\nExiting...")
log("\nclosed peacefully\n\n")
out.close()
