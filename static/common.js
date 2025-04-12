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

setColorMode();
// storm();