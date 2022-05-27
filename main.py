import grader
import json
import os
import markdown
from flask import Flask, request, render_template
app = Flask(__name__)

max_testcases = 10

@app.route("/", methods=["GET"])
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

    return render_template("create.html", max_testcases=max_testcases)

@app.route('/problem', methods=["GET", "POST"])
def problem():
    p = request.args.get("id")
    with open("problems/" + p + ".json", encoding='utf-8') as f:
        data = json.load(f)
    if request.method == "POST":
        print(request.files)
        file = request.files['file']
        file.save("tmp.py")
        lang = request.form["language"]
        results = grader.grade("tmp.py", data["testcases"], lang)
        return render_template("problem.html", results=results, data=data)
    return render_template("problem.html", results=False, data=data)

if __name__ == "__main__":
    app.run("0.0.0.0")