let selectedTab = 2;
let userChosenTextType = false;
let lang = 0;

// scoreboard button
const params = new URLSearchParams(window.location.search);
const p_id = params.get("player");
const g_id = params.get("g_id");
const problem = params.get("id");
const submissionBox = document.getElementById("submission-box");
const resultsContainer = document.getElementById('results-container');
const languageText = document.getElementById("language-text");

languageText.oninput = () => { userChosenTextType = true; }

const inGame = (p_id != null && g_id != null);
if (inGame) {
    document.getElementById("scoreboard_button").addEventListener("click", () => { location.href = "scoreboard?id=" + g_id + "&player=" + p_id; });
    document.getElementById("scoreboard_button").style.display = "block";
    document.getElementById("catalog_button").style.display = "none";
}


/**
 * 
 * @param {string} text 
 */
const fixQuotes = (text) => text.replaceAll(`‘`, `'`).replaceAll(`’`, `'`).replaceAll(`“`, `"`).replaceAll(`”`, '"');

// deal with form
document.getElementById("file").onchange = () => {
    const extension = String((document.getElementById("file")).value).split('.').pop();
    let i = 0;
    if (extension == "cpp") i = 0
    if (extension == "java") i = 1
    if (extension == "py") i = 3
    document.getElementById("language").options[i].selected = true;
}

const submissionText = document.getElementById("submission-text");
submissionText.onchange = () => {
    submissionText.value = fixQuotes(submissionText.value);
    if (userChosenTextType) return;

    const text = new String(submissionText.value);

    const pyHints = ["print(", "input()", "##PY", "else:"];
    const cppHints = ["cout", "ll", "long long", "#include <", "using namespace std;"];
    const javaHints = ["public static void main(",]

    pyHints.forEach((hint) => { if (text.includes(hint)) lang = 3; })
    cppHints.forEach((hint) => { if (text.includes(hint)) lang = 0; })
    javaHints.forEach((hint) => { if (text.includes(hint)) lang = 1; })

    languageText.options[0].selected = false;
    languageText.options[lang].selected = true;
}

const resultName = {
    "AC": "Accepted",
    "WA": "Wrong Answer",
    "TLE": "Time Limit Exceeded",
    "RE": "Runtime Error",
    "CE": "Compile Error"
}

/**
 * Fill the results panel with recieved submission results
 * @param {string[][]} results has results in a list of length-2 lists in the form [RESULT, time]
 */
const fillResults = (results) => {
    const resultDisplay = document.createElement("div");
    resultDisplay.className = "grid-tiny";
    results.forEach((result, i) => {
        resultDisplay.innerHTML += `
            <div class = "result-box ${(result[0] == "AC") ? "success" : "fail"}" title = ${resultName[result[0]]}>
                ${i + 1} <b>${result[0]}</b><p>${result[1]}${result[0] == "CE" ? "" : "ms"}</p>
            </div> `;
    });

    resultsContainer.innerHTML = `<div id="loading-spinny-container" class="box loading-spinny-container"><div class="loading-spinny"></div></div>`;
    resultsContainer.appendChild(resultDisplay);
    stopLoading();
}

const getGrade = (submissionID) => {
    if (localStorage.getItem("submission-" + problem) != submissionID) localStorage.setItem("submission-" + problem, submissionID);

    getContent("/api/submission_result?submission=" + submissionID, (data) => {
        console.log(data);
        fillResults(data.results);
    });
}

const startLoading = () => {
    submissionBox.reset();
    resultsContainer.innerHTML = `
    <div id="loading-spinny-container" class="box loading-spinny-container" style="display:block">
        <div class="loading-spinny"></div>
    </div><h2>grading...</h2>`;
}

const stopLoading = () => { document.getElementById("loading-spinny-container").style.display = "none"; }

const submitFile = () => {
    if (!submissionBox.reportValidity()) throw new Error("Could not submit: invalid form contents")

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
            .then(response => {
                startLoading();
                return response.json()
            })
            .then(data => getGrade(data.submissionID));
    }
    reader.readAsText(file);
}

const submitText = () => {
    const language = languageText.value;

    const sol_text = submissionText.value;
    if (sol_text == "") return;
    "".replaceAll(`“”`)
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
        .then(response => {
            startLoading();
            return response.json()
        })
        .then(data => getGrade(data.submissionID));
}

const submit = () => {
    if (selectedTab == 1) submitFile();
    else submitText();
}

if (localStorage.getItem("submission-" + problem) != null) getGrade(localStorage.getItem("submission-" + problem));

const setSelectedTab = (tab) => {
    if (selectedTab == tab) return;

    document.getElementById(`tab-${selectedTab}-content`).style.display = "none";
    document.getElementById(`tab-${tab}-content`).style.display = "block";

    document.getElementById(`tab-${selectedTab}`).className = "tab";
    document.getElementById(`tab-${tab}`).className = "tab selected";

    selectedTab = tab;
}

document.getElementById("tab-1").onclick = setSelectedTab.bind(this, 1);
document.getElementById("tab-2").onclick = setSelectedTab.bind(this, 2);

setSelectedTab(1)