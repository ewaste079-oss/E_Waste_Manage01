// Subtle parallax scroll effect
document.addEventListener("mousemove", (e) => {
  document.querySelectorAll(".parallax").forEach((element) => {
    const speed = element.getAttribute("data-speed");
    const x = (window.innerWidth - e.pageX * speed) / 100;
    const y = (window.innerHeight - e.pageY * speed) / 100;
    element.style.transform = `translateX(${x}px) translateY(${y}px)`;
  });
});
