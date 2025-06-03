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
const submissionText = document.getElementById("submission-text");

languageText.oninput = () => { userChosenTextType = true; }

const inGame = (p_id != null && g_id != null);
if (inGame) {
    document.getElementById("scoreboard_button").addEventListener("click", () => { location.href = "scoreboard?id=" + g_id + "&player=" + p_id; });
    document.getElementById("scoreboard_button").style.display = "block";
    document.getElementById("catalog_button").style.display = "none";
}


/** @param {string} text  */
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

submissionText.onchange = () => {

    submissionText.value = fixQuotes(submissionText.value);
    if (userChosenTextType) return;

    /** @type {string} */
    const text = submissionText.value;

    const pyHints = ["print(", "input()", "##PY", "else:"];
    const cppHints = ["cout", "long long", "#include <", "using namespace std;"];
    const javaHints = ["public static void main("];

    cppHints.forEach((hint) => { if (text.includes(hint)) lang = 0; });
    pyHints.forEach((hint) => { if (text.includes(hint)) lang = 3; });
    javaHints.forEach((hint) => { if (text.includes(hint)) lang = 1; });

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
 * @param {string} submissionID has results in a list of length-2 lists in the form [RESULT, time]
 */
const fillResults = (results, submissionID) => {
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

    document.querySelector("#past-sols").innerHTML = `<a href="api/submission?submission=${submissionID}">
        ${submissionID.substring(0, submissionID.lastIndexOf("-"))}
    </a>`;
}

const getGrade = async (submissionID) => {
    const data = await fetch("/api/submission_result?submission=" + submissionID).then(response => response.json());
    if (data.error == "unready") setTimeout(getGrade.bind(this, submissionID), 1000);
    if (data.error && data.error != "none") return;
    fillResults(data.results, submissionID);
}

const startLoading = () => {
    submissionBox.reset();
    document.getElementById("submit").disabled = true;
    resultsContainer.innerHTML = `
    <div id="loading-spinny-container" class="box loading-spinny-container" style="display:block">
        <div class="loading-spinny"></div>
    </div><h2>grading...</h2>`;
}

const stopLoading = () => {
    document.getElementById("loading-spinny-container").style.display = "none";
    document.getElementById("submit").disabled = false;
}

const submitCode = (code, language) => {
    startLoading();
    fetch("/api/submit" + window.location.search, {
        method: "POST",
        body: JSON.stringify({
            submission: code,
            lang: language
        }),
        headers: { "Content-type": "application/json; charset=UTF-8" }
    })
        .then(response => response.json())
        .then(data => getGrade(data.submissionID));
}

const reader = new FileReader();
reader.onload = () => {
    const sol_text = reader.result;
    /** @type {string} */
    const language = document.getElementById("language").value;
    submitCode(sol_text, language);
}

/**
 * Submits the submission text or file (based on tab)
 * @throws {Error} if no file selected
 */
const submit = () => {
    if (selectedTab == 1) {
        if (!submissionBox.reportValidity()) throw new Error("Invalid form contents");
        /** @type {File} */
        const file = document.getElementById("file").files[0];

        reader.readAsText(file);
    }
    else submitCode(submissionText.value, languageText.value);
}

/** @param {number} tab */
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

user.addEventListener("login", () => {
    if (problem in user.attempted) {
        getGrade(user.attempted[problem]);
    }
})