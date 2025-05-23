// get the IDs of every problem
let problems = [];

const a = async () => {
    const bruh = await fetch("/api/problem_names").then(response => response.json());
    problems = problems.concat(bruh.public).concat(bruh.publvate).concat(bruh.private);
    console.log(problems);
}

a();
// var allProblems = [];
// for (const element of problems){
//  allProblems.push(element["title"]);
// }

function autocomplete(inp) {

    /*the autocomplete function takes two arguments,
    the text field element and an array of possible autocompleted values:*/
    var currentFocus;
    /*execute a function when someone writes in the text field:*/
    inp.addEventListener("input", function (e) {
        var a, b, i, val = this.value;
        /*close any already open lists of autocompleted values*/
        closeAllLists();
        if (!val) { return false; }
        currentFocus = -1;
        /*create a DIV element that will contain the items (values):*/
        a = document.createElement("DIV");
        a.setAttribute("id", this.id + "autocomplete-list");
        a.setAttribute("class", "autocomplete-items");
        /*append the DIV element as a child of the autocomplete container:*/
        this.parentNode.appendChild(a);
        /*for each item in the array...*/
        for (i = 0; i < problems.length; i++) {
            /*check if the item starts with the same letters as the text field value:*/
            if (problems[i]["title"].substr(0, val.length).toUpperCase() == val.toUpperCase()) {
                /*create a DIV element for each matching element:*/
                b = document.createElement("div");
                b.className = "autocomplete-suggestion";
                /*make the matching letters bold:*/
                b.innerHTML = "<strong>" + problems[i]["title"].substr(0, val.length) + "</strong>";
                b.innerHTML += problems[i]["title"].substr(val.length);
                /*insert a input field that will hold the current array item's value:*/
                b.innerHTML += "<input type='hidden' value='" + problems[i]["title"] + "'>";
                /*execute a function when someone clicks on the item value (DIV element):*/
                b.addEventListener("click", function (e) {
                    /*insert the value for the autocomplete text field:*/
                    inp.value = this.getElementsByTagName("input")[0].value;
                    /*close the list of autocompleted values,
                    (or any other open lists of autocompleted values:*/
                    closeAllLists();
                    add_question();
                });
                a.appendChild(b);
            }
        }
    });
    /*execute a function presses a key on the keyboard:*/
    inp.addEventListener("keydown", function (e) {
        var x = document.getElementById(this.id + "autocomplete-list");
        if (x) x = x.getElementsByTagName("div");
        if (e.keyCode == 40) {
            /*If the arrow DOWN key is pressed,
            increase the currentFocus variable:*/
            currentFocus++;
            /*and and make the current item more visible:*/
            addActive(x);
        } else if (e.keyCode == 38) { //up
            /*If the arrow UP key is pressed,
            decrease the currentFocus variable:*/
            currentFocus--;
            /*and and make the current item more visible:*/
            addActive(x);
        } else if (e.keyCode == 13) {
            /*If the ENTER key is pressed, prevent the form from being submitted,*/
            e.preventDefault();
            if (currentFocus > -1) {
                /*and simulate a click on the "active" item:*/
                if (x) x[currentFocus].click();
            }
        }
    });
    function addActive(x) {
        /*a function to classify an item as "active":*/
        if (!x) return false;
        /*start by removing the "active" class on all items:*/
        removeActive(x);
        if (currentFocus >= x.length) currentFocus = 0;
        if (currentFocus < 0) currentFocus = (x.length - 1);
        /*add class "autocomplete-active":*/
        x[currentFocus].classList.add("autocomplete-active");
    }
    function removeActive(x) {
        /*a function to remove the "active" class from all autocomplete items:*/
        for (var i = 0; i < x.length; i++) {
            x[i].classList.remove("autocomplete-active");
        }
    }
    function closeAllLists(elmnt) {
        /*close all autocomplete lists in the document,
        except the one passed as an argument:*/
        var x = document.getElementsByClassName("autocomplete-items");
        for (var i = 0; i < x.length; i++) {
            if (elmnt != x[i] && elmnt != inp) {
                x[i].parentNode.removeChild(x[i]);
            }
        }
    }
    /*execute a function when someone clicks in the document:*/
    document.addEventListener("click", function (e) {
        closeAllLists(e.target);
    });
}
autocomplete(document.getElementById("inputProblems"));

var usingProblems = [];

function add_question() {

    var thisQuestion;

    for (let i = 0; i < problems.length; i++) {
        if (problems[i]["title"] == document.getElementById("inputProblems").value) {
            thisQuestion = problems[i];
            break;
        }
    }

    if (thisQuestion == null || usingProblems.includes(thisQuestion)) {
        document.getElementById("inputProblems").value = "";
    }

    else {
        usingProblems.push(thisQuestion);
        document.getElementById("problems").innerHTML = "";
        for (problem of usingProblems) {
            document.getElementById("problems").innerHTML += problem.id + "\n";
        }

        let box = document.createElement("div");
        box.className = "box";
        box.innerHTML = thisQuestion["title"];
        document.getElementById("question-grid").appendChild(box);
        document.getElementById("inputProblems").value = "";
    }
}