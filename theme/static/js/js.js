function initializePageScripts() {
  // 🏆 Re-run your carousel logic
  function initializeCarousel() {
    if (window.matchMedia("(min-width: 768px)").matches) {
        document.querySelectorAll(".carousel-container-scroll").forEach(carousel => {
            const scrollContainer = carousel.querySelector(".overflow-x-auto");
            const leftButton = carousel.querySelector(".scroll-left");
            const rightButton = carousel.querySelector(".scroll-right");
            const items = carousel.querySelectorAll(".overflow-x-auto > li");

            if (!scrollContainer || !leftButton || !rightButton || items.length === 0) return;

            // Function to calculate scroll distance based on visible items
            const calculateScrollDistance = () => {
                const containerWidth = scrollContainer.offsetWidth;
                let totalWidth = 0;

                for (const item of items) {
                    const itemWidth = item.offsetWidth + 20; // Including margin/gap
                    if (totalWidth + itemWidth <= containerWidth) {
                        totalWidth += itemWidth;
                    } else {
                        break;
                    }
                }
                return totalWidth;
            };

            // Function to check and toggle button visibility
            const updateButtonVisibility = () => {
                leftButton.querySelector("svg").style.display = scrollContainer.scrollLeft > 0 ? "block" : "none";
                rightButton.querySelector("svg").style.display =
                    Math.ceil(scrollContainer.scrollLeft + scrollContainer.clientWidth) < scrollContainer.scrollWidth
                        ? "block"
                        : "none";
            };

            // Button click functionality
            leftButton.addEventListener("click", () => {
                scrollContainer.scrollBy({ left: -calculateScrollDistance(), behavior: "smooth" });
            });

            rightButton.addEventListener("click", () => {
                scrollContainer.scrollBy({ left: calculateScrollDistance(), behavior: "smooth" });
            });

            // Auto-adjust scroll position after manual scrolling (touch/mousewheel)
            let scrollTimeout;
            scrollContainer.addEventListener("scroll", () => {
                clearTimeout(scrollTimeout);

                scrollTimeout = setTimeout(() => {
                    const scrollLeft = scrollContainer.scrollLeft;
                    const itemWidth = items[0].offsetWidth + 20; // Including margin/gap

                    // Snap to the nearest full item position
                    const newScrollLeft = Math.round(scrollLeft / itemWidth) * itemWidth;
                    scrollContainer.scrollTo({ left: newScrollLeft, behavior: "smooth" });

                    // Update button visibility after snapping
                    updateButtonVisibility();
                }, 200);
            });

            // Initial button visibility check
            updateButtonVisibility();
            scrollContainer.addEventListener("scroll", updateButtonVisibility);
            window.addEventListener("resize", updateButtonVisibility);
        });
    }
}

// Run on load
initializeCarousel();

// Re-run when screen resizes to check if we need to enable/disable
window.addEventListener("resize", () => {
    document.querySelectorAll(".carousel-container-scroll").forEach(carousel => {
        const scrollContainer = carousel.querySelector(".overflow-x-auto");
        if (window.matchMedia("(min-width: 768px)").matches) {
            initializeCarousel();
        } else {
            // Remove all inline styles and behaviors when in small screens
            if (scrollContainer) {
                scrollContainer.style.scrollSnapType = "none";
                scrollContainer.removeEventListener("scroll", updateButtonVisibility);
            }
        }
    });
});

  // 🏆 Re-run modal logic
  document.querySelectorAll('.info-modal-button').forEach(button => {
    button.addEventListener('click', () => {
        document.getElementById('info-modal-title').textContent = button.dataset.title;
        document.getElementById('info-modal-genre').textContent = button.dataset.genre;
        document.getElementById('info-modal-release-date').textContent = button.dataset.releaseDate;
        document.getElementById('info-modal-description').textContent = button.dataset.description;

        const trailerButton = document.getElementById('info-modal-trailer-key');

        // Check if the trailer key exists and is not empty
        if (button.dataset.key && button.dataset.key.trim() !== "") {
            trailerButton.dataset.trailer = button.dataset.key;
            trailerButton.dataset.title = button.dataset.title;
            trailerButton.classList.remove('hidden'); // Remove hidden class if it was hidden before
        } else {
            trailerButton.classList.add('hidden'); // Hide the button if no trailer key
        }
    });
});

  // 🏆 Re-run video trailer logic
  const iframe = document.querySelector('#trailer-modal iframe');
  document.querySelectorAll('[data-trailer]').forEach(button => {
      button.addEventListener('click', () => {
          iframe.src = `https://www.youtube.com/embed/${button.getAttribute('data-trailer')}`;
          document.getElementById('trailer-title').textContent = button.dataset.title;
      });
  });

  document.querySelector('[data-drawer-hide="trailer-modal"]').addEventListener('click', () => {
      iframe.src = '';
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
  

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".video-thumbnail").forEach(img => {
      const youtubeImgUrl = img.getAttribute("data-youtube-src");
      
      if (youtubeImgUrl) {
        const testImg = new Image();
        testImg.src = youtubeImgUrl;

        testImg.onload = function () {
          // YouTube placeholder images are always 120x90
          if (testImg.naturalWidth !== 120 || testImg.naturalHeight !== 90) {
            img.src = youtubeImgUrl; // Only swap if it's a real thumbnail
          }
        };
      }
    });
  });

  function handleImageError(img) {
    if (img.dataset.fallback) {
        img.src = img.dataset.fallback; // Replace with fallback image
        img.classList.remove("object-cover"); // Remove cropping behavior
        img.classList.add("object-contain");  // Ensure full visibility
        img.onerror = null; // Prevent infinite loop in case fallback fails too
    }
}
