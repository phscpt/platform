let duration = parseInt(document.body.getAttribute("tim"));
let timerActive = (duration != -1);
let totalTime = duration;
let opac = 0;

const params = new URLSearchParams(window.location.search);
const id = params.get("id");

async function setTable() {
    //update table
    const data = await fetch(`/api/players?id=${id}`).then(response => response.json());
    if (data.error != "none") return;

    let players = data.players;
    for (let player of players) {
        player.push(player[2].reduce((a, b) => a + b, 0)); // push sum of scores to end of player list
    }

    players.sort((a, b) => {
        if (b[5] != a[5]) return b[5] - a[5]; // time
        return a[4] - b[4]; // score
    })

    document.getElementById("player-list").innerHTML = "";
    for (let i = 0; i < players.length; i++) {
        let rank = i + 1;
        if (document.body.hasAttribute("player_name")) if (players[i][1] == document.body.getAttribute("player_name")) {
            rank = "→ " + String(i + 1);
        }
        let row = document.createElement("tr");

        let rowStyle = "";
        if (i == 0) rowStyle = `style="color:#E6AB21;"`;
        if (i == 1) rowStyle = `style="color:#D81159;"`;
        if (i == 2) rowStyle = `style="color:#324376;"`;

        row.innerHTML = `
            <td ${rowStyle}"> ${rank}</td>
            <td ${rowStyle}><b>${players[i][1]}</b></td>
            <td>${Math.round(players[i][5])}</td>
        `;

        for (let j = 0; j < players[i][2].length; j++) {
            let cell = document.createElement("td");
            cell.innerHTML = Math.round(players[i][2][j]);
            if (players[i][2][j] == 100) cell.className = "prob success";
            else if (players[i][2][j] > 0) cell.className = "prob partial";
            else if (players[i][2][j] == 0) cell.className = "prob";
            else cell.className = "prob fail";
            row.appendChild(cell);
        }
        document.getElementById("player-list").appendChild(row);
    }
}
let updates = 0;
function update() {
    updates++;
    if ((duration >= 0 || !timerActive) && updates % 5 == 0) setTable();

    if (!timerActive) return;

    if (duration >= 0) {
        let hours = parseInt(duration / 3600, 10)
        let minutes = parseInt(duration / 60 % 60, 10);
        let seconds = parseInt(duration % 60, 10);

        hours = hours < 10 ? "0" + hours : hours;
        minutes = minutes < 10 ? "0" + minutes : minutes;
        seconds = seconds < 10 ? "0" + seconds : seconds;

        document.getElementById("timer").innerHTML = hours + ":" + minutes + ":" + seconds;
    }
    else document.getElementById("timer").innerHTML = "Contest Over";

    duration--;

    if (!document.getElementById("panic-inducer")) return;

    if (parseFloat(duration) < 0) {
        opac -= 0.1;
        document.getElementById("panic-inducer").style.opacity = Math.max(opac, 0);
    }
    else if (parseFloat(duration) / parseFloat(totalTime) < 0.1) {
        opac = .6 - 6 * parseFloat(duration) / parseFloat(totalTime);
        document.getElementById("panic-inducer").style.opacity = opac;
    }

}

setInterval(update, 1000);
update();
setTable();