let salt = "";
let id = "";


const crypto = window.crypto;
document.getElementById("submit").disabled = true;
getContent("/api/start_signup", data => {
    salt = data.salt;
    id = data.id;
    document.getElementById("submit").disabled = false;
});

document.getElementById("submit").onclick = () => {
    const pass = document.getElementById("password").value;
    const user = document.getElementById("username").value;
    const email = document.getElementById("email").value;

    const encoder = new TextEncoder();
    const data = encoder.encode(pass + salt);

    crypto.subtle.digest("SHA-256", data)
        .then(hash => {
            const hashArray = Array.from(new Uint8Array(hash));
            const hashHex = hashArray
                .map((val) => val.toString(16).padStart(2, "0"))
                .join("");

            fetch(`/api/finish_signup?username=${user}&email=${email}&id=${id}`, {
                method: "POST",
                body: JSON.stringify({ hashed_pass: hashHex }),
                headers: { "Content-type": "application/json; charset=UTF-8" }
            })
                .then(response => response.json())
                .then(data => {
                    if (data.error != "none") document.getElementById("credentials").reset();
                    location.href = "/log_in";
                    console.log("hooray!")
                })
            // this is secure enough for us right now
            // 2 second change to make it more secure though: just put all the daa in the request body + make server get all vars from body
        })

}