const params = new URLSearchParams(window.location.search);
const id = params.get("id");
setInterval(
    () => getContent(`/api/players?id=${id}`, (data) => {
        document.getElementById("player-grid").innerHTML = "";
        for (const player of data.players) {
            let box = document.createElement("div");
            box.className = "box";
            box.innerHTML = player[1];
            document.getElementById("player-grid").appendChild(box);
        }
    }), 1000);

document.getElementById("gamecode").innerText = `Game Code: ${id}`;