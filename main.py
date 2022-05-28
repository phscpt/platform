import grader
import json
import os
import random
import markdown
from flask import Flask, request, render_template, redirect
app = Flask(__name__)

max_testcases = 10

# PROBLEM CREATION/EDITING/SOLUTION GRADING

@app.route("/list", methods=["GET"])
def catalogue():
    problem_names = os.listdir("problems")
    problems = []
    for p in problem_names:
        prob = json.load(open("problems/" + p, encoding='utf-8'))
        prob["id"] = p.split(".")[0]
        problems.append(prob)
    return render_template("list.html", problems = problems)

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
        return render_template("problem.html", results=results, data=data)
    return render_template("problem.html", results=False, data=data)

# GAME CREATION/JOINING
def random_id():
    return "".join([random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(6)])

games = []

class Game:
    def __init__(self, problems):
        self.id = random_id()
        self.players = []
        self.status = "waiting"
        self.problems = problems
    def addPlayer(self, name):
        player_id = random_id()
        self.players.append([player_id, name, [0] * len(self.problems)])
        return player_id

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            name = request.form["player_name"]
            id = request.form["game_id"]
        except:
            return render_template("index.html")
        for game in games:
            if game.id == id:
                player = game.addPlayer(name)
                return redirect(f"/waiting?id={id}&player={player}")
    return render_template("index.html")

@app.route("/select", methods=["GET", "POST"])
def problem_select():
    if request.method == "POST":
        game = Game(request.form["problems"].split("\n"))
        games.append(game)
        return redirect(f"host_waiting?id={game.id}")
    return render_template("select.html")

@app.route("/host_waiting", methods=["GET", "POST"])
def host():
    id = request.args.get("id")
    if request.method == "POST":
        for game in games:
            if game.id == id:
                game.status = "started"
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
    return render_template("waiting.html", id=request.args.get("id"), player=player_name)

@app.route("/api/game_status", methods=["GET"])
def get_game_status():
    id = request.args.get("id")
    for game in games:
        if game.id == id:
            return game.status

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
    pass

@app.route("/host_scoreboard", methods=["GET"])
def scoreboard_host():
    pass

if __name__ == "__main__":
    app.run("0.0.0.0")