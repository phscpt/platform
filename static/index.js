const checkCookie = () => getCookie("username");

updateLogInOut();

function updateLogInOut() {
    thisAdmin = checkCookie();

    if (thisAdmin == "True") { // If user is an admin
        document.getElementById("catalogue").style.display = "initial";
        document.getElementById("addQuestion").style.display = "none";
    }

    else { // If user is not admin
        document.getElementById("catalogue").style.display = "none";
        document.getElementById("addQuestion").style.display = "initial";
    }

    if (thisAdmin == "NotIn" || thisAdmin == "") { // If user hasn't logged in
        document.getElementById("sign_out").style.display = "none";
        document.getElementById("log_in").style.display = "initial";
    }
    else { // If user has logged in
        document.getElementById("log_in").style.display = "none";
        document.getElementById("sign_out").style.display = "initial";
    }
}

function signOut() {
    setCookie("username", "NotIn", 30);
    setCookie("userid", "NotIn", 30);
    updateLogInOut();
}