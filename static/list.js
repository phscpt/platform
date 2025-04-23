const public_problems = document.getElementById("public-problems");
const publvate_problems = document.getElementById("publvate-problems");
const private_problems = document.getElementById("private-problems");

const problem_names = getContent("/api/problem_names", (problems) => {
    const public = problems.public;
    const publvate = problems.publvate;
    const private = problems.private;

    if (publvate.length == 0 && private.length == 0) {
        document.getElementById("publvate-container").style.display = "none";
        document.getElementById("private-container").style.display = "none";
        document.getElementById("public-title").innerText = "Catalogue";
    }

    diffToNum = {
        "trivial": 0,
        "easy": 1,
        "medium": 2,
        "hard": 3,
        "very hard": 4
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
    let public_details = new Array(public.length);
    let public_l = 0;
    public.forEach((problemTuple, i) => {
        getContent(`/api/problem_data?id=${problemTuple[0]}&title&difficulty&tags&status`, (problem) => {
            // console.log(problem);
            public_details[i] = `
                <tr>
                <td style="padding: 10px">
                    <a href="problem?id=${problem.id}">${problem.title}</a>
                </td>
                <td style="padding: 10px">
                    ${problem.difficulty ? problem.difficulty : "N/A"}
                </td>
                <td style="padding: 10px">
                    ${problem.tags ? problem.tags : "N/A"}
                </td>
                </tr>
            `
            while (public_details[public_l] != undefined) {
                public_problems.innerHTML += public_details[public_l];
                public_l++;
            }
        })
    })
    let publvate_details = new Array(publvate.length);
    let publvate_l = 0;
    publvate.forEach((problemTuple, i) => {
        getContent(`/api/problem_data?id=${problemTuple[0]}&title&difficulty&tags&status`, (problem) => {
            // console.log(problem);
            publvate_details[i] = `
                <tr>
                <td style="padding: 10px">
                    <a href="problem?id=${problem.id}">${problem.title}</a>
                </td>
                <td style="padding: 10px">
                    ${problem.difficulty ? problem.difficulty : "N/A"}
                </td>
                <td style="padding: 10px">
                    ${problem.tags ? problem.tags : "N/A"}
                </td>
                </tr>
            `
            while (publvate_details[publvate_l] != undefined) {
                publvate_problems.innerHTML += publvate_details[publvate_l];
                publvate_l++;
            }
        })
    })
    let private_details = new Array(private.length);
    let private_l = 0;
    private.forEach((problemTuple, i) => {
        getContent(`/api/problem_data?id=${problemTuple[0]}&title&difficulty&tags&status`, (problem) => {
            // console.log(problem);
            private_details[i] = `
                <tr>
                <td style="padding: 10px">
                    <a href="problem?id=${problem.id}">${problem.title}</a>
                </td>
                <td style="padding: 10px">
                    ${problem.difficulty ? problem.difficulty : "N/A"}
                </td>
                <td style="padding: 10px">
                    ${problem.tags ? problem.tags : "N/A"}
                </td>
                </tr>
            `
            while (private_details[private_l] != undefined) {
                private_problems.innerHTML += private_details[private_l];
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