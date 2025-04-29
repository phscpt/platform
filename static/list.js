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

const problem_names = getContent("/api/problem_names", (problems) => {
    const public = problems.public;
    const publvate = problems.publvate;
    const private = problems.private;

    if (publvate.length == 0 && private.length == 0) {
        document.getElementById("publvate-container").style.display = "none";
        document.getElementById("private-container").style.display = "none";
        document.getElementById("public-title").innerText = "Catalogue";
    }


    const cmp = (a, b) => {
        if (b[1].toLowerCase() in diffToNum && a[1].toLowerCase() in diffToNum) {
            let bDiff = diffToNum[b[1].toLowerCase()];
            let aDiff = diffToNum[a[1].toLowerCase()];

            if (aDiff != bDiff) return aDiff - bDiff;
        }
        else if (b[1].toLowerCase() in diffToNum) return 1; //b goes first
        else if (a[1].toLowerCase() in diffToNum) return -1; // a goes first

        if (a[0] > b[0]) return 1;
        if (b[0] > a[0]) return -1;
        return 0;
    }
    public.sort(cmp);
    publvate.sort(cmp);
    private.sort(cmp);
    public_details = new Array(public.length);
    publvate_details = new Array(publvate.length);
    private_details = new Array(private.length);

    const grabInfo = (problems, details, problemContainer) => {
        let l = 0;
        problems.forEach((problemTuple, i) => {
            getContent(`/api/problem_data?id=${problemTuple[0]}&title&difficulty&tags&status`, (problem) => {
                details[i] = problem;
                while (details[l] != undefined) {
                    problemContainer.innerHTML += renderProblem(details[l]);
                    l++;
                }
            })
        });
    }

    grabInfo(public, public_details, public_problems);
    grabInfo(publvate, publvate_details, publvate_problems);
    grabInfo(private, private_details, private_problems);

})

const reverse = (func) => {
    return (a, b) => func(b, a);
}

const cmpDiff = (a, b) => {
    if (b.difficulty.toLowerCase() in diffToNum && a.difficulty.toLowerCase() in diffToNum) {
        let bDiff = diffToNum[b.difficulty.toLowerCase()];
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

    console.log(colorType);

    return `
        <tr ${colorType != "" ? ("class=" + colorType) : ""}>
        <td style="padding: 10px width:50%">
            <a href="problem?id=${p.id}">${p.title}</a>
        </td>
        <td style="padding: 10px; width: 20%;">
            ${p.difficulty ? p.difficulty : "N/A"}
        </td>
        
        <td style="padding: 10px; width: 30%;">
            ${showTags ? (p.tags ? p.tags : "N/A") : ""}
        </td>
        </tr>
    `
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
}

/**
 * 
 * @param {Function} cmp 
 */
const sortBy = (cmp) => {
    public_details.sort(cmp);
    publvate_details.sort(cmp);
    private_details.sort(cmp);

    showProblems();
}

let currSort = "buhsort";
let currDir = 1;

const updateArrows = () => {
    for (const item of document.getElementsByClassName("problem-title")) {
        const a = item.getElementsByTagName("span").item(0);

        if (currSort == "alphabet") {
            if (currDir == 1) a.innerText = "arrow_downward";
            else a.innerText = "arrow_upward";
        }
        else a.innerText = "";
    }
    for (const item of document.getElementsByClassName("difficulty-title")) {
        const a = item.getElementsByTagName("span").item(0);

        if (currSort == "difficulty") {
            if (currDir == -1) a.innerText = "arrow_downward";
            else a.innerText = "arrow_upward";
        }
        else a.innerText = "";
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
    updateArrows();
}


const tableHeadInterior = `
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
    </tr>`



doByTag("thead", (item) => item.innerHTML = tableHeadInterior);
doByClass("problem-title", (item) => item.onclick = changeSort.bind(this, "alphabet"));
doByClass("difficulty-title", (item) => item.onclick = changeSort.bind(this, "difficulty"));

for (const item of document.getElementsByClassName('tags-title')) item.onclick = () => {
    toggleTags();
    updateArrows();
    showProblems();
}

document.body.onload = () => {
    showProblems();
    if (localStorage.getItem("sort-type")) {
        currDir = -1 * Number(localStorage.getItem("sort-dir"));
        currSort = localStorage.getItem("sort-type");
        changeSort(currSort);
    }
    else changeSort("difficulty");
    updateArrows();
}

user.onLogin = () => {
    showProblems();
}