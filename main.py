# https://flask.palletsprojects.com/en/stable/quickstart/

import json, os, random, time, markdown, uuid, hashlib, glob, string, html, traceback, datetime
from contest import *
from flask import Flask, request, render_template, redirect, abort, make_response
from user import User, Users
from config import EXTENDED_ALPHABET, MAX_TESTCASES
app = Flask(__name__)

last_users_clean = time.time()

# PROBLEM CREATION/EDITING/SOLUTION GRADING

def admin_check(request) -> bool:
    try: user = get_logged_in_user(request)
    except: return False
    return user.admin

@app.route("/public", methods=["GET","POST"])
def public_catalogue():
    return render_template("list_public.html")

# TODO: make this an API endpoint as well!
@app.route("/upload", methods=["GET", "POST"])
def upload():
    # ensure only admin can access this page
    if not admin_check(request): abort(401)
    if request.method == "GET": return render_template("create.html", max_testcases=MAX_TESTCASES)
    return _update_problem(request.form["id"],request.form)

# TODO make this call out to api 
@app.route("/edit", methods=["GET", "POST"])
def edit():
    if not admin_check(request): abort(401)
    p = request.args.get("id")
    if not p: abort(404)
    with open("problems/" + p + ".json", encoding='utf-8') as f:
        data = json.load(f)
    data["id"] = p
    if request.method == "POST":
        return _update_problem(p,request.form)
    return render_template("edit.html", max_testcases=MAX_TESTCASES, data=data)

def _update_problem(problem_id, problem_form):
    id = problem_id
    with open("problems/" + id + ".json", encoding='utf-8') as f:
        data = json.load(f)
    data["id"] = id
    title = problem_form["title"]
    status = problem_form["status"]
    description = problem_form["description"]
    testcases = []
    for i in range(MAX_TESTCASES):
        inp:str = problem_form["input" + str(i)]
        out:str = problem_form["output" + str(i)]
        # check if empty
        if inp.rstrip() != "" and out.rstrip() != "": testcases.append([inp, out])
    open("problems/" + id + ".json", "w", encoding='utf-8').write(json.dumps({
        "title": title,
        "status": status,
        "difficulty": problem_form["difficulty"],
        "tags": problem_form["tags"],
        "description": description,
        "testcases": testcases
    }))
    update_problem_statuses()
    return redirect("/problem?id="+id)

# TODO lowk just make problems grab text from /api/problem_data
@app.route('/problem', methods=["GET", "POST"])
def problem():
    # Get problem id
    p = request.args.get("id")
    if not p: abort(404)
    # Load problem description + convert to html
    try:
        with open("problems/" + p + ".json", encoding='utf-8') as f:
            data = json.load(f)
            data["description"] = markdown.markdown(data["description"], extensions=['fenced_code'])
    except: abort(404)

    return render_template("problem.html", data=data)

# MAIN
# TODO: figure out what the POST request is doing here (for game join?) and jam it into api
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET": return render_template("index.html")
    
    try:
        name = request.form["player_name"]
        id = request.form["game_id"]
    except: return render_template("index.html")
    id = id.rstrip().upper()
    print(name, id)

    # for g_id in games:
    #     games[g_id].validate_players()
    try:
        game = get_game(id)
        p_id = game.add_player(name)
        return redirect(f"/waiting?id={id}&player={p_id}")
    except: pass
    return abort(404)


# ABOUT
@app.route("/about")
def about():
    return render_template("about.html")

# JOIN
# TODO: api-ify
@app.route("/join", methods=["GET", "POST"])
def join():
    id = request.args.get("id")
    if request.method == "GET": return render_template("join.html")
    if not id: return abort(404)
    try: name = html.escape(request.form["player_name"], True)
    except: return render_template("join.html")
    id = id.rstrip().upper()
    try:
        game = get_game(id)
        p_id = game.add_player(name)
        return redirect(f"/waiting?id={id}&player={p_id}")
    except: pass
    return abort(404)


@app.route("/log_in", methods=["GET"])
def log_in():
    return render_template("log_in.html")

@app.route("/sign_up", methods=["GET"])
def sign_up():
    return render_template("sign_up.html")

# TODO Turn this into api call as well
@app.route("/select", methods=["GET", "POST"])
def problem_select():
    if request.method == "POST":
        try: duration = int(request.form["timer"])
        except: duration = -1

        game = Game(problems=request.form["problems"].rstrip().split("\n"),  totalTime=duration,
                    tst=request.form.get("tst"), doTeams=bool(request.form.get("teams"))) # both props are inactive
        game.save()
        # games[game.id] = game
        return redirect(f"host_waiting?id={game.id}")
    return render_template("select.html")

# TODO: make api
@app.route("/host_waiting", methods=["GET", "POST"])
def host():
    id = request.args.get("id")
    if not id: return abort(404)
    if request.method == "POST":
        try:
            game = get_game(id)
            game.start()
            return redirect(f"/host_scoreboard?id={id}")
        except KeyError:
            print(f"Game {id} not found. Active games: {'games dp is off bc lollers'}")
    return render_template("host_waiting.html")

# TODO: make api
@app.route("/waiting", methods=["GET"])
def waiting():
    id = request.args.get("id")
    player = request.args.get("player")
    player_name = "unknown"
    if id == None or player == None: return abort(404)
    try:
        game = get_game(id)
        p = game.get_player(player)
        player_name = p.name
    except KeyError:
        print(f"Game or player not found :(")
    return render_template("waiting.html", id=request.args.get("id"), player=player_name, player_id=player)

def update_problem_statuses():
    prob_paths = os.listdir("problems")

    public = []
    publvate = []
    private = []

    for problem in prob_paths:
        if not ".json" in problem: continue
        try:
            with open(f"problems/{problem}") as f: data = json.load(f)
        except:
            print(f"Could not open problem {problem}")
            continue
        id = '.'.join(problem.split('.')[:-1])

        if "difficulty" not in data: data["difficulty"] = ""

        prob = {
            "id":id,
            "difficulty":data["difficulty"],
            "title":data["title"]
        }
        if data["status"] == "public": public.append(prob)
        elif data["status"] == "publvate": publvate.append(prob)
        else: private.append(prob)

    with open("problems_by_status.json",'w') as f:
        json.dump({"public": public, "publvate": publvate, "private": private},f)

# SCOREBOARD
# #TODO: make it grab info from (need to make) games API... itd make so much more sense please bro
@app.route("/scoreboard", methods=["GET"])
def scoreboard():
    id = request.args.get("id")
    player = request.args.get("player")
    if id == None or player == None: return abort(404)
    try:
        game = get_game(id)
        p = game.get_player(player)
        return render_template(
            "scoreboard.html",
            id=id,
            player = player,
            player_name = p.name,
            problems = game.problems,
            time = game.time_remaining()
        )
    except: print(f"Scoreboard for game {id}, player {player} not found")
    abort(404)

# TODO api ify
@app.route("/host_scoreboard", methods=["GET"])
def scoreboard_host():
    id = request.args.get("id")
    if id==None: abort(404)
    try:
        game = get_game(id)
        return render_template(
            "host_scoreboard.html",
            id = id,
            problems = game.problems,
            tst = False,
            time = game.time_remaining()
        )
    except KeyError:
        print(f"Game with id {id} not found")
    abort(404)
# API

def api_error():
    return make_response(json.dumps({"error":"dne"}))

# API/ auth stuff

def get_logged_in_user(request_obj):
    if "user_id" not in request_obj.cookies or "hashed_pass" not in request_obj.cookies:
        raise LookupError
    try:
        user = User(request_obj.cookies.get("user_id"))
    except FileNotFoundError: raise LookupError(f"User with ID {request_obj.cookies.get('user_id')} not found.")
    if user.check_login(request_obj.cookies.get("hashed_pass")): return user
    raise LookupError

@app.route("/api/auth/start_signup")
def start_signup():
    usr = User()
    return json.dumps({"salt": usr.set_salt(), "id":usr.id,"error":"none"})

@app.route("/api/auth/finish_signup", methods=["POST"])
def finish_signup():
    if "id" not in request.args or "email" not in request.args or "username" not in request.args: return json.dumps({"error":"dne"})
    id = request.args.get("id")
    hashed_pass = request.get_json()["hashed_pass"]
    username = request.args.get("username")
    email = request.args.get("email")
    assert id
    try: user = User(id)
    except FileNotFoundError: return api_error()
    print(hashed_pass)

    Users.load_indexing()

    if user.hashed_pass != "": return api_error()
    # print(Users.email_to_id, Users.username_to_id)
    if email in Users.email_to_id: return api_error()
    if username in Users.username_to_id: return api_error()
    user.set_details(username, email)
    user.set_hash_pass(hashed_pass)

    return json.dumps({"jonathan":"orz","error":"none"})

@app.route("/api/auth/login_salt")
def get_login_salt():
    if "email_username" not in request.args:
        print("bad args")
        return api_error()
    Users.load_indexing()
    email_username = request.args.get("email_username")
    id=""
    if email_username in Users.email_to_id: id=Users.email_to_id[email_username]
    elif email_username in Users.username_to_id: id=Users.username_to_id[email_username]
    else:
        print("no user")
        return api_error()

    user = User(id)
    if user.hashed_pass == "" or user.salt == "": return api_error()
    return json.dumps({"salt": user.salt, "id":id, "error":"none"})

@app.route("/api/auth/login",methods=["POST","GET"])
def login():
    def user_json(u:User):
        return {"admin":u.admin, "attempted":u.attempted_problems, "solved": u.solved_problems, "username":u.username, "id":u.id}
    if time.time() - last_users_clean >= 1800: Users.del_empty()

    def clear_login_fail():
        res = api_error()
        res.delete_cookie("hashed_pass")
        res.delete_cookie("user_id")
        return res
    
    if request.method == "GET":
        try: user = get_logged_in_user(request)
        except: return clear_login_fail()
        return json.dumps({"error":"none","user":user_json(user)})
    
    data = request.get_json()

    try: user = User(data["id"])
    except: return api_error()
    if not user.check_login(data["hashed_pass"]): return api_error()

    res = make_response(json.dumps({"error":"none","user":user_json(user)}))
    THIRTY_DAYS = datetime.timedelta(days=30)

    res.set_cookie("hashed_pass",data["hashed_pass"], max_age=THIRTY_DAYS,secure=True, httponly=True, samesite="Strict")
    res.set_cookie("user_id",user.id,max_age=THIRTY_DAYS)

    return res
    

    

# API/ game info

@app.route("/api/games/game_data")
def game_data():
    try:
        g_id = request.args.get("id")
        if not g_id: return api_error()
        game = get_game(g_id)
    except: return api_error()
    data = game.to_json()
    data["error"] = "none"
    return json.dumps(data)
    

# API/ problem info

@app.route("/api/problem_names")
def problem_names():
    '''
    Returns by status
    '''
    if not os.path.exists("problems_by_status.json"): update_problem_statuses()
    with open("problems_by_status.json") as f: all_problems = json.load(f)

    public_only = {"public":all_problems["public"], "publvate":[],"private":[]}
    if not admin_check(request): return json.dumps(public_only)

    return json.dumps(all_problems)

@app.route("/api/problem_data")
def problem_data():
    id = request.args["id"]
    is_admin = admin_check(request)
    if not os.path.exists(f"problems/{id}.json"): return api_error()

    with open(f"problems/{id}.json") as f: problem = json.load(f)

    if problem["status"] == "private" and not is_admin: return api_error()
    res = {"id":id}

    for property in ["title", "status", "difficulty", "tags", "description"]:
        if property in request.args:
            if property not in problem: problem[property] = ""
            res[property] = problem[property]

    if "testcases" in request.args and is_admin: res["testcases"] = problem["testcases"]

    return json.dumps(res)

# API/ problem submission

@app.route("/api/submit", methods=["POST"])
def submit_solution():
    submission = request.get_json()

    # print(f"received problem submission for {p}:", file.filename)
    now = datetime.datetime.now()
    SUBMISSION_ID = now.strftime("%m-%d-%Y-%H-%M-%S-") + "".join([random.choice(EXTENDED_ALPHABET) for _ in range(6)])
    res = {
        "submission": SUBMISSION_ID,
        "problem": request.args.get("id"),
        "status": "waiting for grading server",
        "code": submission["submission"],
        "lang": submission["lang"],
        "results": []
    }
    if "g_id" in request.args and "player" in request.args:
        res["game"] = request.args.get("g_id")
        res["player"] = request.args.get("player")

    try: res["user"] = request.cookies.get("user_id")
    except: pass

    with open(f"grading/{SUBMISSION_ID}.json",'w') as f: json.dump(res,f)
    with open(f"grading/todo/{SUBMISSION_ID}",'w') as f: f.write("")

    try:
        user = get_logged_in_user(request)
        user.add_attempted(request.args.get("id"),SUBMISSION_ID)
    except: pass

    return json.dumps({"submissionID": SUBMISSION_ID, "error":"none"})

@app.route("/api/submission_result", methods=["GET"])
def get_problem_results():
    if "submission" not in request.args: return api_error()
    submission = request.args.get("submission")
    if not os.path.exists(f"grading/{submission}.json"): return api_error()

    with open(f"grading/{submission}.json",'r') as f: res = json.load(f)
    if res["status"] != "graded": return json.dumps({"error":"unready"})
    results = res["results"]

    return json.dumps({"results":res["results"],"error":"none"})

@app.route("/api/submission",methods=["GET"])
def get_submission():
    if "submission" not in request.args: return api_error()
    sub_id = request.args.get("submission")
    if not os.path.exists(f"grading/{sub_id}.json"): return api_error()

    with open(f"grading/{sub_id}.json",'r') as f: submission = json.load(f)

    try:
        if get_logged_in_user(request).id != submission["user"]: return api_error()
        code = submission["code"]
        return code
    except:
        return api_error()

#API/ practice contests

@app.route("/api/game_status", methods=["GET"])
def get_game_status():
    id = request.args.get("id")
    if not id: return api_error()
    try:
        game = get_game(id)
        return json.dumps({"status":game.status, "error":"none"})
    except:
        # print(f"API request for status of game id {id} failed.")
        return api_error()

@app.route("/api/players", methods=["GET"])
def get_players():
    id = request.args.get("id")
    if not id: return api_error()
    try:
        game = get_game(id)
        listified = list(map(Player.to_list,game.players))
        return json.dumps({"players":listified,"error":"none"})
    except KeyError:
        print(f"No game found with id {id}")
    return api_error()

last_orz = time.time()

#API/ random stuff
@app.route("/api/orz",methods=["GET"])
def orz():
    global last_orz
    if time.time() - last_orz < 2: return json.dumps({"error":"too fast :/"})
    last_orz = time.time()
    if not os.path.exists("orz"):
        with open("orz",'w') as f: f.write("0")
    with open("orz",'r') as f: cnt=int(f.read())

    cnt+=1
    with open("orz",'w') as f: f.write(str(cnt))
    return json.dumps({"cnt":cnt})

# ERROR PAGES
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.errorhandler(401)
def unauthorized(e):
    return render_template('401.html'), 401

# @app.route("/crash")
# def crash():
#     raise Exception("Intentional crash tester function triggered")
#     return

Users.del_empty()
if __name__ == "__main__":
    app.run("127.0.0.1",8000)
    # app.run("0.0.0.0")
