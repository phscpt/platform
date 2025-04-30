let salt = "";
let id = "";

const crypto = window.crypto;
document.getElementById("submit").disabled = true;

const getSalt = async () => {
    const data = await fetch("/api/auth/start_signup").then(response => response.json());
    if (data.error && data.error != "none") return;

    salt = data.salt;
    id = data.id;
    document.getElementById("submit").disabled = false;
}


getSalt();
const form = document.getElementById("credentials");

const doError = () => {
    form.reset();
    if (!document.getElementById("error")) {
        const a = document.createElement("p");
        a.id = "error";
        a.innerText = "Account already exists with username or email";
        a.style.color = "red";
        form.appendChild(a);
    }
    else {
        const errorText = document.getElementById("error");
        errorText.style.transition = "all 0.1s ease-in-out"
        errorText.style.fontWeight = 750;
        setTimeout(() => {
            errorText.style.transition = "all 1s ease-in-out";
            errorText.style.fontWeight = 400;
        }, 1000);
    }
    submit.disabled = false;
}

const email = document.getElementById("email");
const pass = document.getElementById("password");
const username = document.getElementById("username");

document.getElementById("submit").onclick = async () => {
    let bad = false
    if (! /\w{1,}@{1}\w{1,}[.]{1}\w{1,}/.test(email.value)) {
        email.setCustomValidity("Enter a valid email");
        email.reportValidity();
        bad = true;
    }
    if (pass.value.length < 8) {

        pass.setCustomValidity("Enter a password with atleast 8 characters");
        pass.reportValidity();
        bad = true;
    }
    if (username.value.length == 0) {
        username.setCustomValidity("Enter a password with atleast 8 characters");
        username.reportValidity();
        bad = true;
    }
    if (bad) return;

    const hashHex = await hash(pass.value + salt);
    const data = await fetch(`/api/auth/finish_signup?username=${username.value}&email=${email.value}&id=${id}`, {
        method: "POST",
        body: JSON.stringify({ hashed_pass: hashHex }),
        headers: { "Content-type": "application/json; charset=UTF-8" }
    }).then(response => response.json());


    if (data.error != "none") {
        doError();
    }
    else location.href = "/log_in";
}