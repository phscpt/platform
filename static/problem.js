// scoreboard button

const params = new Proxy(new URLSearchParams(window.location.search), {
    get: (searchParams, prop) => searchParams.get(prop),
});
const p_id = params.player;
const g_id = params.g_id;
const problem = params.id;
if (p_id != null && g_id != null) {
    document.getElementById("scoreboard_button").addEventListener("click", () => { location.href = "scoreboard?id=" + g_id + "&player=" + p_id; });
    document.getElementById("scoreboard_button").style.display = "block";
    document.getElementById("catalog_button").style.display = "none";
}


// deal with form
const autoSelectExtension = () => {
    const extension = String((document.getElementById("file")).value).split('.').pop();
    let i = 0;
    if (extension == "cpp") i = 0
    if (extension == "java") i = 1
    if (extension == "py") i = 3
    document.getElementById("language").options[i].selected = true;
}
document.getElementById("file").onchange = autoSelectExtension;

const resultName = {
    "AC": "Accepted",
    "WA": "Wrong Answer",
    "TLE": "Time Limit Exceeded",
    "RE": "Runtime Error",
    "CE": "Compile Error"
}

const fillResults = (results) => {
    const resultDisplay = document.createElement("div");
    resultDisplay.className = "grid-tiny";

    results.forEach((result, i) => {
        const ansBlock = document.createElement("div");
        ansBlock.className = "result-box fail";
        ansBlock.title = resultName[result[0]];
        ansBlock.innerHTML = (i + 1) + " <b>" + result[0] + "</b><p>" + result[1] + "ms</p>";
        if (result[0] == "AC") ansBlock.className = "result-box success";

        resultDisplay.appendChild(ansBlock);
    });

    const submissionContainer = document.getElementById("file").parentNode;
    submissionContainer.innerHTML = submissionContainer.innerHTML;
    document.getElementById("file").onchange = autoSelectExtension;

    document.getElementById('results-container').innerHTML = "";
    document.getElementById('results-container').appendChild(resultDisplay);
}

const getGrade = (submissionID) => {
    if (localStorage.getItem("submission-" + problem) != submissionID) localStorage.setItem("submission-" + problem, submissionID);
    fetch("/api/submission_result?submission=" + submissionID)
        .then(response => response.json())
        .then(results => {
            if (results == "ungraded") setTimeout(getGrade, 500, [submissionID]);
            else fillResults(results);
        });
}

const submit = () => {
    const file = document.getElementById("file").files[0];
    const reader = new FileReader();

    reader.onload = () => {
        const sol_text = reader.result;
        const language = document.getElementById("language").value;

        fetch("/api/submit" + window.location.search, {
            method: "POST",
            body: JSON.stringify({
                submission: sol_text,
                lang: language
            }),
            headers: {
                "Content-type": "application/json; charset=UTF-8"
            }
        })
            .then(response => response.json())
            .then(resList => resList[0])
            .then(submissionID => getGrade(submissionID));
    }
    reader.readAsText(file);
}

if (localStorage.getItem("submission-" + problem) != null) getGrade(localStorage.getItem("submission-" + problem));