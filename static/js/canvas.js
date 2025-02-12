const canvas = document.getElementById("drawingCanvas");
const ctx = canvas.getContext("2d");

canvas.width = 1200;
canvas.height = 550;
let isDrawing = false;
let currentTool = "draw";

canvas.addEventListener("mousedown", startDrawing);
canvas.addEventListener("mousemove", draw);
canvas.addEventListener("mouseup", stopDrawing);

// Drawing function
function startDrawing(e) {
    isDrawing = true;
    ctx.beginPath();
    ctx.moveTo(e.offsetX, e.offsetY);
}

function draw(e) {
    if (!isDrawing) return;
    if (currentTool === "draw") {
        ctx.strokeStyle = "black";
        ctx.lineWidth = 3;
        ctx.lineTo(e.offsetX, e.offsetY);
        ctx.stroke();
    } else if (currentTool === "erase") {
        ctx.clearRect(e.offsetX, e.offsetY, 10, 10);
    }
}

function stopDrawing() {
    isDrawing = false;
}

document.getElementById("drawBtn").addEventListener("click", () => currentTool = "draw");
document.getElementById("eraseBtn").addEventListener("click", () => currentTool = "erase");
document.getElementById("textBtn").addEventListener("click", () => alert("Text tool coming soon!"));

document.getElementById("cancelBtn").addEventListener("click", () => window.history.back());
