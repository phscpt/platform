let salt = "";
let id = "";


const crypto = window.crypto;
document.getElementById("submit").disabled = true;
getContent("/api/auth/start_signup", data => {
    salt = data.salt;
    id = data.id;
    document.getElementById("submit").disabled = false;
    console.log(salt);
    console.log(id);
});

console.log("have salt")

document.getElementById("submit").onclick = async () => {
    const pass = document.getElementById("password").value;
    const user = document.getElementById("username").value;
    const email = document.getElementById("email").value;

    let bad = false
    if (! /\w{1,}@{1}\w{1,}[.]{1}\w{1,}/.test(email)) {
        const emailEl = document.getElementById("email");
        emailEl.setCustomValidity("Enter a valid email");
        emailEl.reportValidity();
        bad = true;
    }
    if (pass.length < 8) {
        const passEl = document.getElementById("password");
        passEl.setCustomValidity("Enter a password with atleast 8 characters");
        passEl.reportValidity();
        bad = true;
    }
    if (user.length == 0) {
        const userEl = document.getElementById("username");
        userEl.setCustomValidity("Enter a password with atleast 8 characters");
        userEl.reportValidity();
        bad = true;
    }
    if (bad) return;

    const hashHex = await hash(pass + salt);
    const data = await fetch(`/api/auth/finish_signup?username=${user}&email=${email}&id=${id}`, {
        method: "POST",
        body: JSON.stringify({ hashed_pass: hashHex }),
        headers: { "Content-type": "application/json; charset=UTF-8" }
    }).then(response => response.json());

    console.log(data);

    if (data.error != "none") {
        document.getElementById("credentials").reset();
    }
    else location.href = "/log_in";
}