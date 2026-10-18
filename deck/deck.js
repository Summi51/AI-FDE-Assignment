const slides = [...document.querySelectorAll("section")];
const count = document.getElementById("count");
let i = 0;

function show(next) {
  i = Math.max(0, Math.min(slides.length - 1, next));
  slides.forEach((s, n) => s.classList.toggle("on", n === i));
  count.textContent = `${i + 1} / ${slides.length}`;
}

document.addEventListener("keydown", (e) => {
  if (e.key === "ArrowRight" || e.key === " ") show(i + 1);
  if (e.key === "ArrowLeft") show(i - 1);
});
