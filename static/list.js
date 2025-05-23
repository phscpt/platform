/*
 * This code is too dry :/
 * we should fix it at some point
 */

const public_problems = document.getElementById("public-problems");
const publvate_problems = document.getElementById("publvate-problems");
const private_problems = document.getElementById("private-problems");

let public_details = [];
let publvate_details = [];
let private_details = [];

let showTags = true;
if (localStorage.getItem("show-tags")) showTags = (localStorage.getItem("show-tags") == "true" ? true : false)

const toggleTags = () => {
    showTags = !showTags;
    localStorage.setItem("show-tags", showTags);
}

const diffToNum = {
    "trivial": 0,
    "easy": 1,
    "medium": 2,
    "hard": 3,
    "very hard": 4
}

const getProblems = async () => {
    const problems = await fetch("/api/problem_names").then(response => response.json());
    if (problems.error && problems.error != "none") return;

    /** @type {[string, string][]} */
    const public = problems.public;

    /** @type {[string, string][]} */
    const publvate = problems.publvate;

    /** @type {[string, string][]} */
    const private = problems.private;

    if (publvate.length == 0 && private.length == 0) {
        document.getElementById("publvate-container").style.display = "none";
        document.getElementById("private-container").style.display = "none";
        document.getElementById("public-title").innerText = "Catalogue";
    }

    /**
     * @param {[string, string]} a
     * @param {[string, string]} b
     */
    const cmp = (a, b) => {
        if (b.difficulty.toLowerCase() in diffToNum && a.difficulty.toLowerCase() in diffToNum) {
            let bDiff = diffToNum[b.difficulty.toLowerCase()];
            let aDiff = diffToNum[a.difficulty.toLowerCase()];

            if (aDiff != bDiff) return aDiff - bDiff;
        }
        else if (b.difficulty.toLowerCase() in diffToNum) return 1; //b goes first
        else if (a.difficulty.toLowerCase() in diffToNum) return -1; // a goes first

        if (a.id > b.id) return 1;
        if (b.id > a.id) return -1;
        return 0;
    }
    public.sort(cmp);
    publvate.sort(cmp);
    private.sort(cmp);
    public_details = new Array(public.length);
    publvate_details = new Array(publvate.length);
    private_details = new Array(private.length);

    const grabInfo = async (problems, details, problemContainer) => {
        let l = 0;
        problems.forEach(async (problemTuple, i) => {
            const data = await fetch(`/api/problem_data?id=${problemTuple.id}&title&difficulty&tags&status`).then(response => response.json());
            if (data.error != "none" && data.error) return;

            details[i] = data;
            while (details[l] != undefined) {
                problemContainer.innerHTML += renderProblem(details[l]);
                l++;
            }
            if (l < details.length) return;

            if (localStorage.getItem("sort-type")) {
                currDir = -1 * Number(localStorage.getItem("sort-dir"));
                currSort = localStorage.getItem("sort-type");
                changeSort(currSort);
            }
            else changeSort("difficulty");
        });
    }

    grabInfo(public, public_details, public_problems);
    grabInfo(publvate, publvate_details, publvate_problems);
    grabInfo(private, private_details, private_problems);
}
getProblems();

const reverse = (func) => {
    return (a, b) => func(b, a);
}

const cmpDiff = (a, b) => {
    if (b.difficulty.toLowerCase() in diffToNum && a.difficulty.toLowerCase() in diffToNum) {
        /** @type {number} */
        let bDiff = diffToNum[b.difficulty.toLowerCase()];

        /** @type {number} */
        let aDiff = diffToNum[a.difficulty.toLowerCase()];

        if (aDiff != bDiff) return aDiff - bDiff;
    }
    else if (b.difficulty.toLowerCase() in diffToNum) return 1; //b goes first
    else if (a.difficulty.toLowerCase() in diffToNum) return -1; // a goes first

    if (a.title > b.title) return 1;
    if (b.title > a.title) return -1;
    return 0;
}

const cmpAlph = (a, b) => {
    if (a.title > b.title) return 1;
    if (b.title > a.title) return -1;
    return 0;
}

const renderProblem = (p) => {
    if (!p) return "";
    let colorType = "";

    if (p.id in user.attempted) colorType = "partial";
    if (p.id in user.solved) colorType = "solved";

    return `
        <tr ${colorType != "" ? ("class=" + colorType) : ""}>
        <td style="padding: 10px width:50%">
            <a href="problem?id=${p.id}">${p.title}</a>
        </td>
        <td style="padding: 10px; width: 20%;">
            ${p.difficulty ? p.difficulty : "N/A"}
        </td>
        
        <td style="padding: 10px; width: 25%;">
            ${showTags ? (p.tags ? p.tags : "N/A") : ""}
        </td>
        ${user.admin ?
            `<td style="padding: 10px; width: 5 %; ">
                <a href="${`/edit?id=` + p.id}"><span class="material-symbols-outlined">edit</span></a>
            </td >` : ""}
        </tr>`
};

const showProblems = () => {
    let newPublic = "";
    let newPublvate = "";
    let newPrivate = "";
    for (const p of public_details) newPublic += renderProblem(p);
    for (const p of publvate_details) newPublvate += renderProblem(p);
    for (const p of private_details) newPrivate += renderProblem(p);

    public_problems.innerHTML = newPublic;
    publvate_problems.innerHTML = newPublvate;
    private_problems.innerHTML = newPrivate;

    updateArrows();
}

/** @param {Function} cmp */
const sortBy = (cmp) => {
    public_details.sort(cmp);
    publvate_details.sort(cmp);
    private_details.sort(cmp);

    showProblems();
}

let currSort = "OTZ";
let currDir = 1;

const updateArrows = () => {
    for (const item of document.getElementsByClassName("problem-title")) {
        const a = item.getElementsByTagName("span").item(0);

        if (currSort == "alphabet") {
            a.style.display = "initial";
            if (currDir == 1) a.innerText = "arrow_downward";
            else a.innerText = "arrow_upward";
        }
        else a.style.display = "none";
    }
    for (const item of document.getElementsByClassName("difficulty-title")) {
        const a = item.getElementsByTagName("span").item(0);

        if (currSort == "difficulty") {
            a.style.display = "initial";
            if (currDir == -1) a.innerText = "arrow_downward";
            else a.innerText = "arrow_upward";
        }
        else a.style.display = "none";
    }

    for (const item of document.getElementsByClassName("tags-title")) {
        const a = item.getElementsByTagName("span").item(0);

        if (showTags) a.innerText = "visibility";
        else a.innerText = "visibility_off";
    }
}

const changeSort = (sortName) => {
    if (sortName == currSort) currDir *= -1;
    else {
        currDir = 1;
        currSort = sortName;
    }

    let cmpFunc = (a, b) => 0;

    if (currSort == "difficulty") cmpFunc = cmpDiff;
    else if (currSort == "alphabet") cmpFunc = cmpAlph;

    if (currDir == -1) cmpFunc = reverse(cmpFunc);

    localStorage.setItem("sort-type", currSort);
    localStorage.setItem("sort-dir", currDir);
    sortBy(cmpFunc);
}


let tableHeadInterior = `
        <tr>
        <th style="width:50%;" class="problem-title">
            <div class="head-int">Problem <span class="material-symbols-outlined"></span></div>
        </th>
        <th style="width:20%;" class="difficulty-title">
            <div class="head-int">Difficulty <span class="material-symbols-outlined"></span></div>
        </th>
        <th style="width:30%;" class="tags-title">
            <div class="head-int">Tags<span class="material-symbols-outlined"></span></div>
        </th>
    </tr > `


for (const item of document.getElementsByTagName("thead")) item.innerHTML = tableHeadInterior;
for (const item of document.getElementsByClassName("problem-title")) item.onclick = changeSort.bind(this, "alphabet");
for (const item of document.getElementsByClassName("difficulty-title")) item.onclick = changeSort.bind(this, "difficulty");

for (const item of document.getElementsByClassName('tags-title')) item.onclick = () => {
    toggleTags();
    showProblems();
}

document.body.onload = () => {
    showProblems();
}

user.addEventListener("admin", () => {
    tableHeadInterior = `
    <tr>
        <th style="width:50%;" class="problem-title">
            <div class="head-int">Problem <span class="material-symbols-outlined"></span></div>
        </th>
        <th style="width:20%;" class="difficulty-title">
            <div class="head-int">Difficulty <span class="material-symbols-outlined"></span></div>
        </th>
        <th style="width:25%;" class="tags-title">
            <div class="head-int">Tags<span class="material-symbols-outlined"></span></div>
        </th>
        <th style="width:5%;" class="edit-title">
            <div class="head-int">Edit</div>
        </th>
    </tr > `
    for (const item of document.getElementsByTagName("thead")) item.innerHTML = tableHeadInterior;
    showProblems();
    for (const item of document.getElementsByClassName("problem-title")) item.onclick = changeSort.bind(this, "alphabet");
    for (const item of document.getElementsByClassName("difficulty-title")) item.onclick = changeSort.bind(this, "difficulty");

    for (const item of document.getElementsByClassName('tags-title')) item.onclick = () => {
        toggleTags();
        showProblems();
    }
    document.getElementById("upload-link").style.display = "block";
})