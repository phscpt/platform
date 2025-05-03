user.addEventListener("login", () => {
    document.getElementById("sign_up").style.display = "none";
    document.getElementById("log_in").style.display = "none";
    document.getElementById("sign_out").style.display = "initial";
});

user.addEventListener("logout", () => {
    document.getElementById("sign_up").style.display = "initial";
    document.getElementById("log_in").style.display = "initial";
    document.getElementById("sign_out").style.display = "none";
    setCookie("user_id", "", 30);
});

document.getElementById("sign_out").style.display = "none";
document.getElementById("sign_out").addEventListener("click", () => { user.clear() });


let lastClick = Date.now().valueOf();

setTimeout(() => { document.getElementById("orz").disabled = false; }, 5000);

document.getElementById('orz').onclick = async () => {
    const data = await fetch("/api/orz").then(response => response.json());
    if (data.error && data.error != "none") {
        console.log("wtf bro");
        return;
    }

    document.getElementById('orzcount').innerText = data.cnt;

    document.getElementById('orz-for-scale').style.display = "none";
    document.getElementById('orzcount').style.display = "block";

    setTimeout(
        () => {
            document.getElementById('orz-for-scale').style.display = "block";
            document.getElementById('orzcount').style.display = "none";
        }, 2000
    );
    document.getElementById("orz").disabled = true;
    setTimeout(() => { document.getElementById("orz").disabled = false; }, 2000);
}