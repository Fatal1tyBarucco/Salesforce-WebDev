document.addEventListener("DOMContentLoaded", function () {
  const banners = [
    "assets/banner1.png",
    "assets/banner2.png",
  ];

  const chosen = banners[Math.floor(Math.random() * banners.length)];
  const target = document.getElementById("random-banner");
  if (!target) return;

  function reveal() {
    target.style.opacity = "1";
  }

  target.onload = reveal;
  target.onerror = reveal;

  if (target.complete && target.naturalWidth > 0) {
    reveal();
  }

  target.style.opacity = "0";
  target.src = chosen;
});
