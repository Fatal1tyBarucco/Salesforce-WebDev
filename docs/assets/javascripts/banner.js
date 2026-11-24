document.addEventListener("DOMContentLoaded", function () {
  const banners = [
    {
      base: "assets/banner1",
      alt: "Salesforce Release Intelligence — Pipeline automatizado de Release Notes com IA"
    },
    {
      base: "assets/banner2",
      alt: "Salesforce Release Intelligence — Dashboard interativo de features e releases"
    }
  ];

  const chosen = banners[Math.floor(Math.random() * banners.length)];
  const target = document.getElementById("random-banner");
  if (!target) return;

  // Set alt text
  target.alt = chosen.alt;

  // Replace <img> with <picture> for proper format selection and performance
  // Browsers will pick the first supported format (AVIF > WebP > PNG)
  const picture = document.createElement('picture');

  // AVIF sources (best compression)
  const avif400 = document.createElement('source');
  avif400.type = 'image/avif';
  avif400.srcset = `${chosen.base}-400w.avif`;
  avif400.media = '(max-width: 400px)';

  const avif800 = document.createElement('source');
  avif800.type = 'image/avif';
  avif800.srcset = `${chosen.base}-800w.avif`;
  avif800.media = '(max-width: 800px)';

  const avif1200 = document.createElement('source');
  avif1200.type = 'image/avif';
  avif1200.srcset = `${chosen.base}-1200w.avif`;

  // WebP sources (good fallback)
  const webp400 = document.createElement('source');
  webp400.type = 'image/webp';
  webp400.srcset = `${chosen.base}-400w.webp`;
  webp400.media = '(max-width: 400px)';

  const webp800 = document.createElement('source');
  webp800.type = 'image/webp';
  webp800.srcset = `${chosen.base}-800w.webp`;
  webp800.media = '(max-width: 800px)';

  const webp1200 = document.createElement('source');
  webp1200.type = 'image/webp';
  webp1200.srcset = `${chosen.base}-1200w.webp`;

  // Fallback img (PNG)
  const img = document.createElement('img');
  img.src = `${chosen.base}-800w.png`; // Use smaller PNG as fallback
  img.alt = chosen.alt;
  img.sizes = "(max-width: 400px) 400px, (max-width: 800px) 800px, 960px";
  img.width = 960;
  img.height = 540; // Reserve space to prevent CLS

  // Append sources in order of preference
  picture.append(avif400, avif800, avif1200, webp400, webp800, webp1200, img);

  // Replace the img with picture
  target.parentNode.replaceChild(picture, target);

  // Fade in animation
  requestAnimationFrame(() => {
    img.style.opacity = "1";
  });

  // Initially hidden
  img.style.opacity = "0";
  img.style.transition = "opacity 0.4s ease-in-out";

  // Handle load/error
  img.onload = img.onerror = () => {
    img.style.opacity = "1";
  };

  // If already loaded
  if (img.complete && img.naturalWidth > 0) {
    img.style.opacity = "1";
  }
});
