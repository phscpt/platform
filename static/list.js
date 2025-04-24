const public_problems = document.getElementById("public-problems");
const publvate_problems = document.getElementById("publvate-problems");
const private_problems = document.getElementById("private-problems");

let public_details = [];
let publvate_details = [];
let private_details = [];

let showTags = true;

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

        console.log("a");
        if (a[0] > b[0]) return 1;
        if (b[0] > a[0]) return -1;
        return 0;
    }
    public.sort(cmp);
    publvate.sort(cmp);
    private.sort(cmp);
    public_details = new Array(public.length);
    let public_l = 0;
    public.forEach((problemTuple, i) => {
        getContent(`/api/problem_data?id=${problemTuple[0]}&title&difficulty&tags&status`, (problem) => {
            // console.log(problem);
            public_details[i] = problem;
            while (public_details[public_l] != undefined) {
                const p = public_details[public_l];

                public_problems.innerHTML += `
                    <tr>
                    <td style="padding: 10px">
                        <a href="problem?id=${p.id}">${p.title}</a>
                    </td>
                    <td style="padding: 10px">
                        ${p.difficulty ? p.difficulty : "N/A"}
                    </td>
                    <td style="padding: 10px">
                        ${p.tags ? p.tags : "N/A"}
                    </td>
                    </tr>
                `;
                public_l++;
            }
        })
    })
    publvate_details = new Array(publvate.length);
    let publvate_l = 0;
    publvate.forEach((problemTuple, i) => {
        getContent(`/api/problem_data?id=${problemTuple[0]}&title&difficulty&tags&status`, (problem) => {
            // console.log(problem);
            publvate_details[i] = problem;
            while (publvate_details[publvate_l] != undefined) {
                const p = publvate_details[publvate_l];
                publvate_problems.innerHTML += `
                    <tr>
                    <td style="padding: 10px">
                        <a href="problem?id=${p.id}">${p.title}</a>
                    </td>
                    <td style="padding: 10px">
                        ${p.difficulty ? p.difficulty : "N/A"}
                    </td>
                    <td style="padding: 10px">
                        ${p.tags ? p.tags : "N/A"}
                    </td>
                    </tr>
                `;
                publvate_l++;
            }
        })
    })
    private_details = new Array(private.length);
    let private_l = 0;
    private.forEach((problemTuple, i) => {
        getContent(`/api/problem_data?id=${problemTuple[0]}&title&difficulty&tags&status`, (problem) => {
            // console.log(problem);
            private_details[i] = problem;
            while (private_details[private_l] != undefined) {
                const p = private_details[private_l];
                private_problems.innerHTML += `
                    <tr>
                    <td style="padding: 10px">
                        <a href="problem?id=${p.id}">${p.title}</a>
                    </td>
                    <td style="padding: 10px">
                        ${p.difficulty ? p.difficulty : "N/A"}
                    </td>
                    <td style="padding: 10px">
                        ${p.tags ? p.tags : "N/A"}
                    </td>
                    </tr>
                `;
                private_l++;
            }
        })
    })
    // for (const problem of private) {
    //     getContent(`/api/problem_data?id=${problem}&title&difficulty&tags&status`, (data) => {
    //         console.log(data);
    //     })
    // }
})

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

/**
 * 
 * @param {Function} cmp 
 */
const sortBy = (cmp) => {
    public_details.sort(cmp);
    publvate_details.sort(cmp);
    private_details.sort(cmp);

    let newPublic = "";
    let newPublvate = "";
    let newPrivate = "";

    for (let i = 0; i < public_details.length; i++) {
        const p = public_details[i];
        newPublic += `
            <tr>
            <td style="padding: 10px">
                <a href="problem?id=${p.id}">${p.title}</a>
            </td>
            <td style="padding: 10px">
                ${p.difficulty ? p.difficulty : "N/A"}
            </td>
            <td style="padding: 10px">
                ${p.tags ? p.tags : "N/A"}
            </td>
            </tr>
        `;
    }
    for (let i = 0; i < publvate_details.length; i++) {
        const p = publvate_details[i];
        newPublvate += `
            <tr>
            <td style="padding: 10px">
                <a href="problem?id=${p.id}">${p.title}</a>
            </td>
            <td style="padding: 10px">
                ${p.difficulty ? p.difficulty : "N/A"}
            </td>
            <td style="padding: 10px">
                ${p.tags ? p.tags : "N/A"}
            </td>
            </tr>
        `;
    }
    for (let i = 0; i < private_details.length; i++) {
        const p = private_details[i];
        newPrivate += `
            <tr>
            <td style="padding: 10px">
                <a href="problem?id=${p.id}">${p.title}</a>
            </td>
            <td style="padding: 10px">
                ${p.difficulty ? p.difficulty : "N/A"}
            </td>
            <td style="padding: 10px">
                ${p.tags ? p.tags : "N/A"}
            </td>
            </tr>
        `;
    }

    public_problems.innerHTML = newPublic;
    publvate_problems.innerHTML = newPublvate;
    private_problems.innerHTML = newPrivate;
}

let currSort = "difficulty";
let currDir = 1;

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

    sortBy(cmpFunc)

}

document.getElementById('problem-title').onclick = () => changeSort("alphabet");
document.getElementById('difficulty-title').onclick = () => changeSort("difficulty");