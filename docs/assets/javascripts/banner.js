document.addEventListener("DOMContentLoaded", function () {
  const banners = [
    "../assets/banner1.png",
    "../assets/banner2.png",
  ];

  const chosen = banners[Math.floor(Math.random() * banners.length)];

  const target = document.getElementById("random-banner");
  if (target) {
    target.src = chosen;
    target.style.opacity = "0";
    target.addEventListener("load", function () {
      target.style.opacity = "1";
    });
    target.addEventListener("error", function () {
      target.style.opacity = "1";
    });
  }
});
