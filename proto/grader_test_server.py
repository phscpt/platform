import grader
from flask import Flask, request, render_template
app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        print(request.files)
        file = request.files['file']
        file.save("tmp.py")
        results = grader.grade("tmp.py", [[n,"hello world!\n"*n] for n in range(1,10)])
        return render_template("problem.html", results=results)
    return render_template("problem.html", results=False)

if __name__ == "__main__":
    app.run("0.0.0.0")