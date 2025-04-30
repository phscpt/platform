const params = new URLSearchParams(window.location.search);
const id = params.get("id");

const playerGrid = document.getElementById("player-grid");

setInterval(async () => {
    const data = await fetch(`/api/players?id=${id}`).then(response => response.json());
    if (data.error && data.error != "none") return;

    let newGrid = "";
    for (const player of data.players) newGrid += `<div class="box">${player[1]}</div>`;
    playerGrid.innerHTML = newGrid;
}, 1000);

document.getElementById("gamecode").innerText = `Game Code: ${id}`;