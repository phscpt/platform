import grader
import json
import os
import random
import time
import markdown
from flask import Flask, request, render_template, redirect
app = Flask(__name__)

max_testcases = 10
games = []

# PROBLEM CREATION/EDITING/SOLUTION GRADING

def get_problems():
    problem_names = os.listdir("problems")
    problems = []
    for p in problem_names:
        prob = json.load(open("problems/" + p, encoding='utf-8'))
        prob["id"] = p.split(".")[0]
        problems.append(prob)
    return problems

@app.route("/list", methods=["GET"])
def catalogue():    
    return render_template("list.html", problems = get_problems())

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        id = request.form["id"]
        title = request.form["title"]
        description = markdown.markdown(request.form["description"])
        testcases = []
        for i in range(max_testcases):
            inp = request.form["input" + str(i)]
            out = request.form["output" + str(i)]
            # check if empty
            if inp.rstrip() != "" and out.rstrip() != "":
                testcases.append([inp, out])
        open("problems/" + id + ".json", "w", encoding='utf-8').write(json.dumps({"title": title, "description": description, "testcases": testcases}))
        return redirect("/")
    return render_template("create.html", max_testcases=max_testcases)

@app.route("/edit", methods=["GET", "POST"])
def edit():
    p = request.args.get("id")
    with open("problems/" + p + ".json", encoding='utf-8') as f:
        data = json.load(f)
    data["id"] = p
    if request.method == "POST":
        id = request.form["id"]
        title = request.form["title"]
        description = markdown.markdown(request.form["description"])
        testcases = []
        for i in range(max_testcases):
            inp = request.form["input" + str(i)]
            out = request.form["output" + str(i)]
            # check if empty
            if inp.rstrip() != "" and out.rstrip() != "":
                testcases.append([inp, out])
        open("problems/" + id + ".json", "w", encoding='utf-8').write(json.dumps({"title": title, "description": description, "testcases": testcases}))
        return redirect("/")
    return render_template("edit.html", max_testcases=max_testcases, data=data)

@app.route('/problem', methods=["GET", "POST"])
def problem():
    p = request.args.get("id")
    with open("problems/" + p + ".json", encoding='utf-8') as f:
        data = json.load(f)
    if request.method == "POST":
        print(request.files)
        file = request.files['file']

        fname = "tmp/" + file.filename
        file.save(fname)
        lang = request.form["language"]

        results = grader.grade(fname, data["testcases"], lang)

        num_ac = 0
        for res in results:
            if res[0] == "AC":
                num_ac += 1
        
        g_id = request.args.get("g_id")
        p_id = request.args.get("player")
        if (g_id != None) and (p_id != None):
            print("giving score to", p_id, "from game", g_id)
            for game in games:
                if game.id == g_id:
                    for pl in game.players:
                        if pl[0] == p_id:
                            if num_ac == len(results):
                                num_points = 100
                            elif num_ac > 1:
                                num_points = 30
                            else:
                                num_points = -1
                            game.give_points(p_id, p, num_points)

        return render_template("problem.html", results=results, data=data)
    return render_template("problem.html", results=False, data=data)

# GAME CREATION/JOINING
def random_id():
    return "".join([random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(6)])

class Game:
    def __init__(self, problems, totalTime, doTeams):
        self.id = random_id()
        self.players = []
        self.status = "waiting"
        #time is in minutes
        try:
            self.time = int(totalTime) * 60
        except:
            self.time = -1
        self.teams = doTeams
        self.problems = [problem.rstrip() for problem in problems]
        print("created game", self.id)
        print("problems:", problems)
    def add_player(self, name):
        player_id = random_id()
        self.players.append([player_id, name, [0] * len(self.problems)])
        return player_id
    def start(self):
        self.status = "started"
        self.start_time = time.time()
    def give_points(self, player, problem, points):
        problem_index = self.problems.index(problem)
        for pl in self.players:
            if pl[0] == player:
                pl[2][problem_index] = points

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            name = request.form["player_name"]
            id = request.form["game_id"]
        except:
            return render_template("index.html")
        id = id.rstrip().upper()
        for game in games:
            if game.id == id:
                player = game.add_player(name)
                return redirect(f"/waiting?id={id}&player={player}")
    return render_template("index.html")

@app.route("/select", methods=["GET", "POST"])
def problem_select():
    if request.method == "POST":
        game = Game(request.form["problems"].rstrip().split("\n"), request.form["timer"], request.form.get("teams"))
        games.append(game)
        return redirect(f"host_waiting?id={game.id}")
    return render_template("select.html", problems=get_problems())

@app.route("/host_waiting", methods=["GET", "POST"])
def host():
    id = request.args.get("id")
    if request.method == "POST":
        for game in games:
            if game.id == id:
                game.start()
                break
        return redirect(f"/host_scoreboard?id={id}")
    return render_template("host_waiting.html", id=id)

@app.route("/waiting", methods=["GET"])
def waiting():
    id = request.args.get("id")
    player = request.args.get("player")
    player_name = "unknown"
    for game in games:
        if game.id == id:
            for p in game.players:
                if p[0] == player:
                    player_name = p[1]
    return render_template("waiting.html", id=request.args.get("id"), player=player_name, player_id=player)

@app.route("/api/game_status", methods=["GET"])
def get_game_status():
    id = request.args.get("id")
    for game in games:
        if game.id == id:
            return '{"status":"%s"}' % game.status

@app.route("/api/players", methods=["GET"])
def get_players():
    id = request.args.get("id")
    for game in games:
        if game.id == id:
            return json.dumps(game.players)
    return "error"

# SCOREBOARD

@app.route("/scoreboard", methods=["GET"])
def scoreboard():
    id = request.args.get("id")
    player = request.args.get("player")
    for game in games:
        if game.id == id:
            for p in game.players:
                if p[0] == player:
                    return render_template(
                        "scoreboard.html",
                        id=id, player=player,
                        player_name=p[1],
                        problems=game.problems,
                        time = game.time - (time.time() - game.start_time)
                    )

@app.route("/host_scoreboard", methods=["GET"])
def scoreboard_host():
    id = request.args.get("id")
    for game in games:
        if game.id == id:
            return render_template(
                "host_scoreboard.html",
                id=id,
                problems=game.problems,
                time = game.time - (time.time() - game.start_time)
            )
    return "error"

if __name__ == "__main__":
    app.run("0.0.0.0")