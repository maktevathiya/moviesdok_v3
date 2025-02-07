

document.addEventListener("DOMContentLoaded", () => {
    // Select all carousels on the page
    const carousels = document.querySelectorAll(".carousel-container-scroll");
  
    carousels.forEach((carousel) => {
      const scrollContainer = carousel.querySelector(".overflow-x-auto");
      const leftButton = carousel.querySelector(".scroll-left");
      const rightButton = carousel.querySelector(".scroll-right");
      const items = carousel.querySelectorAll(".overflow-x-auto > li");
  
      const calculateScrollDistance = () => {
        const containerWidth = scrollContainer.offsetWidth; // Width of the visible container
        let totalWidth = 0;
        let visibleItems = 0;
  
        // Calculate the width of fully visible items
        for (const item of items) {
          const itemWidth = item.offsetWidth + 20; // Including spacing
          if (totalWidth + itemWidth <= containerWidth) {
            totalWidth += itemWidth;
            visibleItems++;
          } else {
            break;
          }
        }
  
        return totalWidth; // Scroll by the total width of fully visible items
      };
  
      // Function to scroll left
      const scrollLeft = () => {
        const scrollDistance = calculateScrollDistance();
        scrollContainer.scrollBy({
          left: -scrollDistance, // Scroll left by visible item width
          behavior: "smooth",
        });
      };
  
      // Function to scroll right
      const scrollRight = () => {
        const scrollDistance = calculateScrollDistance();
        scrollContainer.scrollBy({
          left: scrollDistance, // Scroll right by visible item width
          behavior: "smooth",
        });
      };
  
      // Add event listeners to buttons
      leftButton.addEventListener("click", scrollLeft);
      rightButton.addEventListener("click", scrollRight);
    });
  });
  
  
  
  
  document.addEventListener('DOMContentLoaded', () => {
    // Listen for clicks on all buttons with the class 'open-modal'
    document.querySelectorAll('.info-modal-button').forEach(button => {
      button.addEventListener('click', () => {
        // Clear the existing modal content
        document.getElementById('info-modal-title').textContent = '';
        document.getElementById('info-modal-genre').textContent = '';
        document.getElementById('info-modal-release-date').textContent = '';
        document.getElementById('info-modal-description').textContent = '';
  
        // Extract data attributes directly from the button
        const title = button.dataset.title;
        const genre = button.dataset.genre;
        const releaseDate = button.dataset.releaseDate;
        const description = button.dataset.description;
  
        // Inject the new data into the modal
        document.getElementById('info-modal-title').textContent = title;
        document.getElementById('info-modal-genre').textContent = genre;
        document.getElementById('info-modal-release-date').textContent = releaseDate;
        document.getElementById('info-modal-description').textContent = description;
      });
    });
  });
  
  
  document.addEventListener('DOMContentLoaded', function () {
    // Get the iframe element inside the modal
    const iframe = document.querySelector('#trailer-modal iframe');
  
    // Add event listener to buttons that should set the trailer source
    const trailerButtons = document.querySelectorAll('[data-trailer]');
  
    trailerButtons.forEach(button => {
      button.addEventListener('click', function () {
        // Get the trailer key from the button's data attribute
        const trailerKey = button.getAttribute('data-trailer');
        
        // Set the iframe source with the trailer key (YouTube embed URL)
        iframe.src = `https://www.youtube.com/embed/${trailerKey}`;
      });
    });
  
    // Add event listener to the close button of the modal
    const closeButton = document.querySelector('[data-drawer-hide="trailer-modal"]');
    closeButton.addEventListener('click', function () {
      // Clear the iframe source to stop the video
      iframe.src = '';
    });
  });
  function calculateMargin(width) {
    const margin = 0.001406 * Math.pow(width, 1.791); // Exponential formula
    return margin / 2; // Half for each side
  }
  
  // Example usage
  const width = window.innerWidth; // Dynamically get the current width
  const margin = calculateMargin(width); // Calculate margin
  
  // Apply to an element dynamically
  const element = document.getElementById("person-container");
  element.style.marginLeft = `${margin}px`;
  element.style.marginRight = `${margin}px`;
  
  window.onload = () => {
    const descriptionContainers = document.querySelectorAll(".description-container");
  
    if (!descriptionContainers.length) return; // Ensure at least one description exists
  
    const checkOverflow = (container, button) => {
        if (container.scrollHeight > container.offsetHeight) {
            container.classList.add("hide-last-word");
            button.classList.remove("hidden");
        } else {
            container.classList.remove("hide-last-word");
            button.classList.add("hidden");
        }
    };
  
    descriptionContainers.forEach(container => {
        const wrapper = container.closest(".description-wrapper"); // Find the closest wrapper
        if (!wrapper) return; // Ensure the container is inside a wrapper
  
        const moreButton = wrapper.querySelector(".more-button"); // Get the button inside the same wrapper
  
        if (!moreButton) return; // Ensure button exists inside this wrapper
  
        checkOverflow(container, moreButton); // Initial check
        window.addEventListener('resize', () => checkOverflow(container, moreButton)); // Recheck on resize
    });
  };
  
  
  document.querySelectorAll('.video-thumbnail').forEach(img => {
      img.onload = function () {
          if (img.naturalWidth === 120 && img.naturalHeight === 90) {
              const fallbackSrc = img.getAttribute('data-fallback-src');
              img.src = fallbackSrc;
          }
      };
  });
  