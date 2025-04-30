class User extends EventTarget {
    id = null;
    username = null;
    #admin = false;
    attempted = {};
    solved = {};
    #loggedIn = false;

    constructor() {
        super();
        if (getCookie("user_id") == "") return;

        this.id = getCookie("user_id");
    }

    clear() {
        this.id = null;
        this.username = null;
        this.attempted = {};
        this.isAdmin = false;
        this.loggedIn = false;
    }

    get admin() { return this.#admin; }
    set admin(isAdmin) {
        if (isAdmin) this.dispatchEvent(new Event("admin"));
        this.#admin = isAdmin;
    }

    get loggedIn() { return this.#loggedIn }
    set loggedIn(loginState) {
        this.#loggedIn = loginState;
        if (loginState) this.dispatchEvent(new Event("login"));
        else this.dispatchEvent(new Event("logout"));
    }

    async login() {
        if (this.id == null) {
            this.admin = false;
            return false;
        }

        const loginData = await fetch(`/api/auth/login`).then(response => response.json());
        if (loginData.error != "none") {
            console.log("Could not log in", loginData);
            this.loggedIn = false;
            return false;
        }
        this.admin = loginData.user.admin;
        this.attempted = loginData.user.attempted;
        this.solved = loginData.user.solved;
        this.username = loginData.user.username;
        this.loggedIn = true;
        return true;
    }
}

const user = new User();
user.login();

function storm() {
    const stormScript = document.createElement("script", { src: "//cdnjs.cloudflare.com/ajax/libs/Snowstorm/20131208/snowstorm-min.js" });
    stormScript.onload = () => {
        snowStorm.excludeMobile = false;
        snowStorm.followMouse = false;
        snowStorm.snowCharacter = '&#10052;'; //snowflake character
        snowStorm.snowColor = '#9a9ea1'; //give the snowflakes another colour
        snowStorm.snowStick = false; //if true, the snow will stick to the bottom of the screen
        snowStorm.animationInterval = 30; //milliseconds per frame, the higher the less CPU load
        snowStorm.flakesMaxActive = 10; //maximum number of active snow flakes, the lower the less CPU/GPU is needed to draw them
        snowStorm.freezeOnBlur = true; //recommended: stops the snow effect when the user switches to another tab or window
        snowStorm.usePositionFixed = true; //if the user scrolls, the snow is not affected by the window scroll. Disable to prevent extra CPU load
        snowStorm.vMaxX = 5;
        snowStorm.vMaxY = 2;
        snowStorm.flakeWidth = 20;
        snowStorm.flakeHeight = 20;
    }
}

let mode = parseInt(localStorage.getItem("mode")) || 1;
const messages = ["Are you sure you want to join the dark side?", "smh using dark mode", "Do you want to make text less readable?", "Every time you use dark mode, you break Jieruei's heart", "Once you start down the dark path, forever it will dominate your destiny.", "The dark side clouds everything."];

function switchColorMode() {
    if (mode == 1) {
        if (!confirm(messages[Math.floor(Math.random() * messages.length)])) return;
    }
    mode *= -1;
    localStorage.setItem("mode", mode);
    setColorMode();
}

function setColorMode() {
    if (mode == -1) {
        document.getElementById("water_css").href = "https://cdn.jsdelivr.net/npm/water.css@2/out/dark.css";
        document.getElementById("custom_css").href = "static/style_dark.css";
    }
    else {
        document.getElementById("water_css").href = "https://cdn.jsdelivr.net/npm/water.css@2/out/light.css";
        document.getElementById("custom_css").href = "static/style.css";
    }
}

function setCookie(cname, cvalue, exdays) {
    const d = new Date();
    d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
    const expiree = d.toUTCString();
    document.cookie = `${cname}=${cvalue};expires=${expiree};path=/`;
}

function getCookie(cname) {
    let name = cname + "=";
    let decodedCookie = decodeURIComponent(document.cookie);
    let ca = decodedCookie.split(';');
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) == ' ') c = c.substring(1);
        if (c.indexOf(name) == 0) return c.substring(name.length, c.length);
    }
    return "";
}

setColorMode();
// storm();

// copy function for input/output
for (codeblock of document.getElementsByTagName("pre")) {
    codeblock.onclick = function () { navigator.clipboard.writeText(this.innerText); }
}

/**
 * GET and process json data
 * @param {string} url the url to GET json data from
 * @param {Function} callback ingest json data from the url
 */
const getContent = async (url, callback) => {
    const data = await fetch(url).then(response => response.json());
    if (data.error == "dne") return;
    if (data.error == "unready") {
        setTimeout(getContent, 500, url, callback);
        return;
    }
    callback(data);
}

const encoder = new TextEncoder();

const hash = async (text) => {
    const data = encoder.encode(text);

    const hash = await crypto.subtle.digest("SHA-256", data);
    const hashArray = Array.from(new Uint8Array(hash));
    const hashHex = hashArray
        .map((val) => val.toString(16).padStart(2, "0"))
        .join("");

    return hashHex;
}

if (document.getElementById("year") != null) document.getElementById("year").innerHTML = new Date().getFullYear();