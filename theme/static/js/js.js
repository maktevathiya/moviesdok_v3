function initializePageScripts() {
  // 🏆 Re-run your carousel logic
  document.querySelectorAll(".carousel-container-scroll").forEach(carousel => {
      const scrollContainer = carousel.querySelector(".overflow-x-auto");
      const leftButton = carousel.querySelector(".scroll-left");
      const rightButton = carousel.querySelector(".scroll-right");
      const items = carousel.querySelectorAll(".overflow-x-auto > li");

      const calculateScrollDistance = () => {
          const containerWidth = scrollContainer.offsetWidth;
          let totalWidth = 0;
          let visibleItems = 0;

          for (const item of items) {
              const itemWidth = item.offsetWidth + 20;
              if (totalWidth + itemWidth <= containerWidth) {
                  totalWidth += itemWidth;
                  visibleItems++;
              } else {
                  break;
              }
          }

          return totalWidth;
      };

      leftButton.addEventListener("click", () => {
          scrollContainer.scrollBy({ left: -calculateScrollDistance(), behavior: "smooth" });
      });

      rightButton.addEventListener("click", () => {
          scrollContainer.scrollBy({ left: calculateScrollDistance(), behavior: "smooth" });
      });
  });

  // 🏆 Re-run modal logic
  document.querySelectorAll('.info-modal-button').forEach(button => {
      button.addEventListener('click', () => {
          document.getElementById('info-modal-title').textContent = button.dataset.title;
          document.getElementById('info-modal-genre').textContent = button.dataset.genre;
          document.getElementById('info-modal-release-date').textContent = button.dataset.releaseDate;
          document.getElementById('info-modal-description').textContent = button.dataset.description;
      });
  });

  // 🏆 Re-run video trailer logic
  const iframe = document.querySelector('#trailer-modal iframe');
  document.querySelectorAll('[data-trailer]').forEach(button => {
      button.addEventListener('click', () => {
          iframe.src = `https://www.youtube.com/embed/${button.getAttribute('data-trailer')}`;
      });
  });

  document.querySelector('[data-drawer-hide="trailer-modal"]').addEventListener('click', () => {
      iframe.src = '';
  });

  // 🏆 Re-run image fallback logic
  document.querySelectorAll('.video-thumbnail').forEach(img => {
      img.onload = function () {
          if (img.naturalWidth === 120 && img.naturalHeight === 90) {
              img.src = img.getAttribute('data-fallback-src');
          }
      };
  });

  // 🏆 Re-run "Show More" logic
  document.querySelectorAll(".description-container").forEach(container => {
      const wrapper = container.closest(".description-wrapper");
      if (!wrapper) return;

      const moreButton = wrapper.querySelector(".more-button");
      if (!moreButton) return;

      const checkOverflow = () => {
          if (container.scrollHeight > container.offsetHeight) {
              container.classList.add("hide-last-word");
              moreButton.classList.remove("hidden");
          } else {
              container.classList.remove("hide-last-word");
              moreButton.classList.add("hidden");
          }
      };

      checkOverflow();
      window.addEventListener('resize', checkOverflow);
  });

  // Call Flowbite Reinitialization
  reinitializeFlowbite();

}

// Function to reinitialize Flowbite
function reinitializeFlowbite() {
  console.log("Reinitializing Flowbite...");
  window.dispatchEvent(new Event("load")); // This forces Flowbite to reinitialize
}

// 🚀 Run the scripts when the page loads
document.addEventListener("DOMContentLoaded", initializePageScripts);
document.body.addEventListener("htmx:historyRestore", initializePageScripts);
document.body.addEventListener('htmx:afterSettle', initializePageScripts);

document.addEventListener("htmx:afterSwap", function() {
  window.scrollTo(0, 0);
});

function addLoaderBars() {
    document.querySelectorAll('.loader').forEach(loader => {
      // Avoid adding bars if they already exist
      if (loader.children.length === 0) {
        for (let i = 0; i < 12; i++) {
          const bar = document.createElement('div');
          loader.appendChild(bar);
        }
      }
    });
  }
  
  // Run on page load
  addLoaderBars();
  
  // Re-run when HTMX updates the DOM
  document.body.addEventListener('htmx:afterSettle', addLoaderBars);
  