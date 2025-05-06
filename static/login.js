const username = document.getElementById("emailUsername");
const password = document.getElementById("password");
const form = document.getElementById("form");
const submit = document.getElementById("submit");

const checkForm = () => {
    let canSubmit = true;
    if (!username.value) {
        username.setCustomValidity("Enter a username or email");
        username.reportValidity();
        canSubmit = false;
    }
    if (!password.value) {
        password.setCustomValidity("Enter password");
        password.reportValidity();
        canSubmit = false;
    }
    return canSubmit;

}

const doError = () => {
    form.reset();
    if (!document.getElementById("error")) {
        const a = document.createElement("p");
        a.id = "error";
        a.innerText = "Incorrect username or password";
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

const formattedDate = () => {
    const now = new Date();
    let month = new String(now.getMonth() + 1);
    let year = new String(now.getFullYear());

    while (month.length < 2) month = "0" + month;

    return `${month}-${year}`;
}

submit.onclick = async () => {
    if (!checkForm()) return;
    submit.disabled = true;

    const data = await fetch(`/api/auth/login_salt?email_username=${username.value}`).then(res => res.json());
    if (data.error != "none") {
        doError();
        return;
    }

    const salt = data.salt;
    const id = data.id;
    const hashHex = await hash(password.value + salt);
    const hashedSquared = await hash(hashHex + formattedDate());

    const loginData = await fetch(`/api/auth/login`, {
        method: "POST",
        body: JSON.stringify({ hashed_pass: hashedSquared, id: id }),
        headers: { "Content-type": "application/json; charset=UTF-8" }
    }).then(response => response.json());

    if (loginData.error != "none") {
        doError();
        return;
    }

    window.location.href = "/";
}