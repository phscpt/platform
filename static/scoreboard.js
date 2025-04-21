let duration = parseInt(document.body.getAttribute("tim"));
let timerActive = (duration != -1);
let totalTime = duration;
let opac = 0;

const params = new URLSearchParams(g_id = window.location.search);
const id = params.get("id");

function setTable() {
    //update table
    fetch(`/api/players?id=${id}`)
        .then(response => response.json())
        .then(function (players) {
            for (let player of players) {
                player.push(player[2].reduce((a, b) => a + b, 0));
            }
            // sort by time
            players.sort((a, b) => a[4] - b[4]);

            // sort by score
            players.sort((a, b) => b[5] - a[5]);

            document.getElementById("player-list").innerHTML = "";
            for (let i = 0; i < players.length; i++) {
                let rank = i + 1;
                if (document.body.hasAttribute("player_name")) if (players[i][1] == document.body.getAttribute("player_name")) {
                    rank = "→ " + String(i + 1);
                }
                let row = document.createElement("tr");

                if (i == 0) {
                    row.innerHTML = `
                    <td style="color:#E6AB21;"> ${rank}</td>
                    <td style="color:#E6AB21;"><b>${players[i][1]}</b></td>
                    <td style="color:#000000;">${Math.round(players[i][5])}</td>
                    `;
                }

                if (i == 1) {
                    row.innerHTML = `
                    <td style="color:#D81159;"> ${rank}</td>
                    <td style="color:#D81159;"><b>${players[i][1]}</b></td>
                    <td style="color:#000000;">${Math.round(players[i][5])}</td>
                    `;
                }

                if (i == 2) {
                    row.innerHTML = `
                    <td style="color:#324376;"> ${rank}</td>
                    <td style="color:#324376;"><b>${players[i][1]}</b></td>
                    <td style="color:#000000;">${Math.round(players[i][5])}</td>
                    `;
                }

                if (i > 2) {
                    row.innerHTML = `
                    <td> ${rank}</td>
                    <td><b> ${players[i][1]}</b></td>
                    <td> ${Math.round(players[i][5])}</td>
                    `;
                }

                for (let j = 0; j < players[i][2].length; j++) {
                    let cell = document.createElement("td");
                    cell.innerHTML = Math.round(players[i][2][j]);
                    if (players[i][2][j] == 100) {
                        cell.className = "prob success";
                    }
                    else if (players[i][2][j] > 0) {
                        cell.className = "prob partial";
                    }
                    else if (players[i][2][j] == 0) {
                        cell.className = "prob";
                    }
                    else {
                        cell.className = "prob fail";
                    }
                    row.appendChild(cell);
                }
                document.getElementById("player-list").appendChild(row);
            }
        });
}
let updates = 0;
function update() {
    updates++;
    if (timerActive) {
        if (duration >= 0) {
            hours = parseInt(duration / 3600, 10)
            minutes = parseInt(duration / 60 % 60, 10);
            seconds = parseInt(duration % 60, 10);

            hours = hours < 10 ? "0" + hours : hours;
            minutes = minutes < 10 ? "0" + minutes : minutes;
            seconds = seconds < 10 ? "0" + seconds : seconds;

            document.getElementById("timer").innerHTML = hours + ":" + minutes + ":" + seconds;
        }
        else {
            document.getElementById("timer").innerHTML = "Contest Over";
        }

        duration--;
        if (document.getElementById("panic-inducer")) {
            if (parseFloat(duration) < 0) {
                opac -= 0.1;
                document.getElementById("panic-inducer").style.opacity = Math.max(opac, 0);
            }
            else if (parseFloat(duration) / parseFloat(totalTime) < 0.1) {
                opac = .6 - 6 * parseFloat(duration) / parseFloat(totalTime);
                document.getElementById("panic-inducer").style.opacity = opac;
            }
        }
    }

    if ((duration >= 0 || !timerActive) && updates % 5 == 0) setTable();
}

setInterval(update, 1000);
update();
setTable();