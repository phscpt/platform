user.onLogin = () => {
    document.getElementById("sign_up").style.display = "none";
    document.getElementById("log_in").style.display = "none";
    document.getElementById("sign_out").style.display = "initial";
}

user.onAdmin = () => {
    document.getElementById("catalogue").style.display = "initial";
    document.getElementById("addQuestion").style.display = "none";
}

user.onLogout = () => {
    document.getElementById("sign_up").style.display = "initial";
    document.getElementById("log_in").style.display = "initial";
    document.getElementById("sign_out").style.display = "none";

    document.getElementById("catalogue").style.display = "none";
    document.getElementById("addQuestion").style.display = "initial";
    setCookie("user_id", "", 30);
}

document.getElementById("sign_out").style.display = "none";
document.getElementById("catalogue").style.display = "none";
document.getElementById("sign_out").addEventListener("click", () => { user.clear() });
user.login();