// Function to animate counting up numbers
function animateCounting(targetElement, startValue, endValue, duration) {
    let current = startValue;
    const step = Math.ceil((endValue - startValue) / (duration / 10));
  
    function updateCount() {
      current += step;
      if (current <= endValue) {
        targetElement.textContent = current;
        setTimeout(updateCount, 10);
      } else {
        targetElement.textContent = endValue;
      }
    }
  
    updateCount();
  }
  
  // Start the animations when the page loads
  window.addEventListener("load", () => {
    const discoveredCountElement = document.getElementById("discoveredCount");
    const recommendedCountElement = document.getElementById("recommendedCount");
  
    // Replace these numbers with your actual data
    const totalDiscovered = 250;
    const totalRecommended = 432;
  
    animateCounting(discoveredCountElement, 0, totalDiscovered, 2000);
    animateCounting(recommendedCountElement, 0, totalRecommended, 2000);
  });
  