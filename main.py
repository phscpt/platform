# https://flask.palletsprojects.com/en/stable/quickstart/

import json, os, random, time, markdown, uuid, hashlib, glob, string, html, traceback
from datetime import datetime
from contest import *
from flask import Flask, request, render_template, redirect, abort
from user import User
app = Flask(__name__)

max_testcases = 10

users = []

def loadSecret() -> None:
    global secret
    secret = open("SECRET.txt", "r").read().rstrip()

def changeSecret() -> None:
    global secret
    ALLOWED = "QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm"
    LENGTH = 100
    now = datetime.now()
    secret = "".join([random.choice(ALLOWED) for _ in range(LENGTH)]) + now.strftime("%m-%Y")
    with open("SECRET.txt",'w') as f:
        f.write(secret)

loadSecret()

# PROBLEM CREATION/EDITING/SOLUTION GRADING
def sortByDifficulty(x) -> int:
    # comparator used to sort problems in increasing difficulty
    mapping = {
        "trivial": 0, "easy": 1, "medium": 2, "hard": 3, "very hard": 4
    }
    if "difficulty" in x and x["difficulty"].lower() in mapping:
        return mapping[x["difficulty"].lower()]
    return 5

def get_problem_names() -> list:
    # Get all problems, in sorted order
    problem_names = os.listdir("problems")
    problems = []
    for p in problem_names:
        if not ".json" in p:
            continue
        prob = json.load(open("problems/" + p, encoding='utf-8'))
        prob["id"] = p.split(".")[0]
        new_prob = {
            "id": prob["id"],
            "status": prob["status"],
            "title": prob["title"],
        }
        if "difficulty" in prob and prob["difficulty"] != "":
            new_prob["difficulty"] = prob["difficulty"]
        if "tags" in prob and prob["tags"] != "":
            new_prob["tags"] = prob["tags"]
        problems.append(new_prob)
    problems.sort(key = lambda x: x["title"])
    problems.sort(key = sortByDifficulty)
    return problems

def admin_check(req) -> bool:
    loadSecret()
    if (secret[-7:] != datetime.now().strftime("%m-%Y")[-7:]): changeSecret()
    return req.cookies.get("userid") == secret

@app.route("/list", methods=["GET","POST"])
def catalogue():
    if admin_check(request):
        return render_template("list.html", problems = get_problem_names())
    abort(401)

@app.route("/public", methods=["GET","POST"])
def public_catalogue():
    return render_template("list_public.html")

@app.route("/upload", methods=["GET", "POST"])
def upload():
    # ensure only admin can access this page
    if not admin_check(request):
        abort(401)

    if request.method == "POST":
        id = request.form["id"]
        title = request.form["title"]
        status = request.form["status"]
        #description = markdown.markdown(request.form["description"])
        description = request.form["description"]
        testcases = []
        for i in range(max_testcases):
            inp = request.form["input" + str(i)]
            out = request.form["output" + str(i)]
            # check if empty
            if inp.rstrip() != "" and out.rstrip() != "":
                testcases.append([inp, out])
        open("problems/" + id + ".json", "w", encoding='utf-8').write(
            json.dumps({
                "title": title,
                "status": status,
                "difficulty": request.form["difficulty"],
                "tags": request.form["tags"],
                "description": description,
                "testcases": testcases
            })
        )
        update_problem_statuses()
        return redirect("/")
    return render_template("create.html", max_testcases=max_testcases)

@app.route("/edit", methods=["GET", "POST"])
def edit():
    if not admin_check(request):
        abort(401)
    p = request.args.get("id")
    with open("problems/" + p + ".json", encoding='utf-8') as f:
        data = json.load(f)
    data["id"] = p
    if request.method == "POST":
        id = request.form["id"]
        title = request.form["title"]
        status = request.form["status"]
        description = request.form["description"]
        testcases = []
        for i in range(max_testcases):
            inp = request.form["input" + str(i)]
            out = request.form["output" + str(i)]
            # check if empty
            if inp.rstrip() != "" and out.rstrip() != "":
                testcases.append([inp, out])
        open("problems/" + id + ".json", "w", encoding='utf-8').write(json.dumps({
            "title": title,
            "status": status,
            "difficulty": request.form["difficulty"],
            "tags": request.form["tags"],
            "description": description,
            "testcases": testcases
        }))
        update_problem_statuses()
        return redirect("/list")
    return render_template("edit.html", max_testcases=max_testcases, data=data)

@app.route('/problem', methods=["GET", "POST"])
def problem():
    # Get problem id
    p = request.args.get("id")

    # Load problem description + convert to html
    try:
        with open("problems/" + p + ".json", encoding='utf-8') as f:
            data = json.load(f)
            data["description"] = markdown.markdown(data["description"], extensions=['fenced_code'])
    except: abort(404)

    return render_template("problem.html", results=False, data=data)

# GAME CREATION/JOINING
def random_id():
    return "".join([random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(6)])

def random_player_id():
    return "".join([random.choice(string.ascii_uppercase + string.ascii_lowercase + "1234567890") for _ in range(20)])

# MAIN
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            name = request.form["player_name"]
            id = request.form["game_id"]
        except:
            return render_template("index.html")
        id = id.rstrip().upper()
        print(name, id)

        for g_id in games:
            games[g_id].validate_players()
        try:
            game = get_game(id)
            p_id = game.add_player(name)
            return redirect(f"/waiting?id={id}&player={p_id}")
        except KeyError: pass
    return render_template("index.html")

# ABOUT
@app.route("/about")
def about():
    return render_template("about.html")

# JOIN
@app.route("/join", methods=["GET", "POST"])
def join():
    id = request.args.get("id")
    if request.method == "POST":
        try:
            name = html.escape(request.form["player_name"],True)
        except:
            return render_template("join.html", id=id)
        id = id.rstrip().upper()
        try:
            game = get_game(id)
            p_id = game.add_player(name)
            return redirect(f"/waiting?id={id}&player={p_id}")
        except KeyError:
            ...
            # print(f"Game {id} not found. Active games: {" ".join([game.id for game in Games.__games])}")
    return render_template("join.html", id=id)

def hash_password(password):
    salt = uuid.uuid4().hex
    return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt

def check_password(hashed_password, user_password):
    password, salt = hashed_password.split(':')
    return password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest()

def is_admin(email, username, hashedPass):
    if email == "jierueic@gmail.com" and username == "knosmos" and check_password("c8cd035724dd2cc48f87c17f21c4cb7f9bdf9cf767bc88e5fcefefbf8f73dd0f:533a7722507f4d1da1bdfca16bf70675", hashedPass):
        return True
    if email == "nicholas.d.hagedorn@gmail.com" and username == "Nickname" and check_password("6d6438706baee7793b76597a15628859cf9b47c0097f814d06187247d120ceb7:6316c3b35173482db353c2a2baa8301e", hashedPass):
        return True

    return False

def is_account(cred, email_or_username, password):
    return check_password( cred[2], password) and (email_or_username == cred[0] or email_or_username == cred[1])

# This class is unused; it remains in the code in case user accounts are implented in the future
# class User:
#     def __init__(self, email, username, password):
#         self.user_ID = str(id(str(email)+str(username)+str(hash_password(password))))
#         self.isAdmin = is_admin(email, username, password)
#         self.credentials = [email, username, hash_password(password), self.user_ID, self.isAdmin]

#     def is_repeat(self, users):
#         for otherUser in users:
#             if otherUser.credentials[0] == self.credentials[0] or otherUser.credentials[1] == self.credentials[1]:
#                 return True
#         return False

#     def store_account(self):
#         open("users/" + self.user_ID + ".json", "w", encoding='utf-8').write(json.dumps(self.credentials))

@app.route("/log_in", methods=["GET", "POST"])
def log_in():
    if request.method == "POST":
        try:
            emailUsername = request.form["emailUsername"].strip()
            password = request.form["password"].strip()

            for filename in glob.glob(os.path.join("users/", '*.json')): #only process .JSON files in folder.
                with open(filename, encoding='utf-8') as currentFile:
                    data = json.load(currentFile)
                    if is_account(data, emailUsername, password):

                        userID = secret
                        isAdmin = data[4]

                        return render_template(
                            "log_in.html",
                            admin = isAdmin,
                            userid = userID
                        )
                        # return redirect(f"/?id={userID}") #change to put userID in the URL
        except:
            pass

    return render_template("log_in.html")

@app.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        email = request.form["email"].strip()
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        user = User(email, username, password)
        if "@" in email and len(username) > 4 and len(password) > 4 and not user.is_repeat(users):
            user.store_account()
            userID = user.credentials[3]
            return redirect(f"/") #change to put userID in the URL
    return render_template("sign_up.html")

@app.route("/select", methods=["GET", "POST"])
def problem_select():
    if request.method == "POST":
        print("value is")
        print(request.form.get("tst"))
        try:
            duration = int(request.form["timer"])
        except:
            duration = -1

        game = Game(problems=request.form["problems"].rstrip().split("\n"), totalTime=duration, tst=request.form.get("tst"), doTeams=request.form.get("teams"))

        games[game.id] = game
        return redirect(f"host_waiting?id={game.id}")
    problems = get_problem_names()
    public_problems = []
    if not admin_check(request):
        print("not admin")
        for problem in problems:
            if problem["status"] == "public":
                public_problems.append(problem)
        return render_template("select.html", problems = public_problems)

    # admins have access to all problems
    for problem in problems:
        print(problem["status"])
        if problem["status"] == "public" or problem["status"] == "publvate":
            public_problems.append(problem)
    return render_template("select.html", problems = public_problems)

@app.route("/host_waiting", methods=["GET", "POST"])
def host():
    id = request.args.get("id")
    if request.method == "POST":
        try:
            game = get_game(id)
            game.start()
            return redirect(f"/host_scoreboard?id={id}")
        except KeyError:
            print(f"Game {id} not found. Active games: {[games[g_id].id for g_id in games] }")
    return render_template("host_waiting.html", id=id)

@app.route("/waiting", methods=["GET"])
def waiting():
    id = request.args.get("id")
    player = request.args.get("player")
    player_name = "unknown"

    try:
        game = get_game(id)
        p = game.get_player(player)
        print(p, "bruh")
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
        with open(f"problems/{problem}") as f: data = json.load(f)
        id = '.'.join(problem.split('.')[:-1])
        if "difficulty" not in data: data["difficulty"] = ""
        if data["status"] == "public": public.append([id,data["difficulty"]])
        elif data["status"] == "publvate": publvate.append([id,data["difficulty"]])
        else: private.append([id,data["difficulty"]])
    with open("problems_by_status.json",'w') as f:
        json.dump({"public": public, "publvate": publvate, "private": private},f)

@app.route("/api/start_signup")
def start_signup():
    usr = User()
    return json.dumps({"salt": usr.set_salt(), "id":usr.id,"error":"none"})

@app.route("/api/finish_signup", methods=["POST"])
def finish_signup():
    if "id" not in request.args or "email" not in request.args or "username" not in request.args: return json.dumps({"error":"dne"})
    id = request.args.get("id")
    hashed_pass = request.get_json()["hashed_pass"]
    username = request.args.get("username")
    email = request.args.get("email")
    print(id)
    try: user = User(id)
    except FileNotFoundError: return json.dumps({"error":"dne"})
    print(hashed_pass)

    user.set_details(username, email)
    user.set_hash_pass(hashed_pass)

    return json.dumps({"jonathan":"orz","error":"none"})



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
    if not os.path.exists(f"problems/{id}.json"): return json.dumps({"error":"dne"})
    
    with open(f"problems/{id}.json") as f: problem = json.load(f)

    if problem["status"] == "private" and not is_admin: return json.dumps({"error":"dne"})
    res = {"id":id}
    
    for property in ["title", "status", "difficulty", "tags", "description"]:
        if property in request.args:
            if property not in problem: problem[property] = ""
            res[property] = problem[property]

    if "testcases" in request.args and is_admin: res["testcases"] = problem["testcases"]

    return json.dumps(res)

@app.route("/api/check_admin", methods=["GET"])
def request_is_admin():
    curr_state = {"admin":False, "logged_in":False, "error":"none"}
    if admin_check(request):
        curr_state["admin"]=True
        curr_state["logged_in"]=True
        return json.dumps(curr_state)
    return curr_state
    

@app.route("/api/submit", methods=["POST"])
def submit_solution():
    submission = request.get_json()

    # print(f"received problem submission for {p}:", file.filename)
    now = datetime.now()
    SUBMISSION_ID = now.strftime("%m-%d-%Y-%H-%M-%S-") + random_id()
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

    with open(f"grading/{SUBMISSION_ID}.json",'w') as f: json.dump(res,f)
    with open(f"grading/todo/{SUBMISSION_ID}",'w') as f: f.write("")
    # grader.grade(SUBMISSION_ID)

    return json.dumps({"submissionID": SUBMISSION_ID, "error":"none"})

@app.route("/api/submission_result", methods=["GET"])
def get_problem_results():
    if "submission" not in request.args: return json.dumps({"error":"dne"})
    submission = request.args.get("submission")
    if not os.path.exists(f"grading/{submission}.json"): return json.dumps({"error":"dne"})

    with open(f"grading/{submission}.json",'r') as f: res = json.load(f)
    if res["status"] != "graded": return json.dumps({"error":"unready"})
    results = res["results"]

    num_ac = 0
    for r in results:
        if r[0] == "AC": num_ac += 1

    if "game" not in res and "player" not in res:
        return json.dumps({"results":res["results"],"error":"none"})
    print('a')
    # give points to player if playing a game
    g_id = res["game"]
    p_id = res["player"]
    print("giving score to", p_id, "from game", g_id)
    try:
        game = get_game(g_id)
        player = game.get_player(p_id)
        if num_ac == len(results):
            num_points = 100
        elif num_ac > 1:
            num_points = 100 * (num_ac - 1)/(len(results) - 1)
        else:
            num_points = -0.0001
        player.results[res["problem"]] = results
        game.give_points(p_id, res["problem"], num_points)
    except KeyError: pass
    return json.dumps({"results":res["results"],"error":"none"})

@app.route("/api/game_status", methods=["GET"])
def get_game_status():
    id = request.args.get("id")
    try:
        game = get_game(id)
        return json.dumps({"status":game.status, "error":"none"})
    except:
        print(f"API request for status of game id {id} failed.")
        return json.dumps({"error":"dne"})

@app.route("/api/players", methods=["GET"])
def get_players():
    id = request.args.get("id")
    try:
        game = get_game(id)
        listified = list(map(Player.to_list,game.players))
        return json.dumps({"players":listified,"error":"none"})
    except KeyError:
        print(f"No game found with id {id}")
    return json.dumps({"error":"dne"})

# SCOREBOARD

@app.route("/scoreboard", methods=["GET"])
def scoreboard():
    id = request.args.get("id")
    player = request.args.get("player")
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
    except:
        print(f"Scoreboard for game {id}, player {player} not found")
    abort(404)

@app.route("/host_scoreboard", methods=["GET"])
def scoreboard_host():
    id = request.args.get("id")
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

# ERROR PAGES
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html', data = traceback.format_exc()), 500

@app.errorhandler(401)
def unauthorized(e):
    return render_template('401.html'), 401

@app.route("/crash")
def crash():
    raise Exception("Intentional crash tester function triggered")
    return

''' # Uncomment to remove old games
running_games = []
for game in games:
    if game.time_remaining() >= -1:
        running_games.append(game)
games = running_games
'''

if __name__ == "__main__":
    app.run("127.0.0.1",8000)
    # app.run("0.0.0.0")
