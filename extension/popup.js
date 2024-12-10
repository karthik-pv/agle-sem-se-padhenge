document.addEventListener("DOMContentLoaded", () => {
  const initializeButton = document.getElementById("initializeButton");
  const sendButton = document.getElementById("sendButton");
  const inputBox = document.getElementById("inputBox");
  const responseContainer = document.getElementById("responseContainer");
  const responseText = document.getElementById("responseText");
  const prevButton = document.getElementById("prevButton");
  const nextButton = document.getElementById("nextButton");

  let pageNumbers = []; // Array to hold page numbers
  let currentPageIndex = -1; // Current page index

  function disableAllElements() {
    initializeButton.disabled = true;
    sendButton.disabled = true;
    inputBox.disabled = true;
    prevButton.disabled = true; // Disable Prev button
    nextButton.disabled = true; // Disable Next button
  }

  function enableAllElements() {
    initializeButton.disabled = false;
    sendButton.disabled = false;
    inputBox.disabled = false;
    prevButton.disabled = false; // Enable Prev button
    nextButton.disabled = false; // Enable Next button
  }

  // Disable all elements initially
  disableAllElements();

  // Check if the current tab is a PDF and enable the initialize button
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    const currentTab = tabs[0];

    if (currentTab.url && currentTab.url.startsWith("file:///")) {
      initializeButton.disabled = false;

      // Check if already initialized using localStorage
      if (localStorage.getItem("isInitialized") === "true") {
        enableAllElements();
      }
    }
  });

  // Event listener for the initialize button
  initializeButton.addEventListener("click", async () => {
    try {
      console.log("Initialization started");
      chrome.tabs.query({ active: true, currentWindow: true }, async (tabs) => {
        const currentTab = tabs[0];
        const activeTabUrl = currentTab.url;

        // Send a request to your server to initialize
        const response = await fetch("http://localhost:5000/pdf_setup", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ file_url: activeTabUrl }),
        });

        if (response.status === 200) {
          const data = await response.json();
          console.log("Initialization successful:", data);

          // Set the initialization status in localStorage
          localStorage.setItem("isInitialized", "true");

          // Store page numbers and set the current page index
          pageNumbers = data.page_numbers || []; // Assuming the response contains page numbers
          currentPageIndex = 0; // Start at the first page
          // Enable all elements after successful initialization
          enableAllElements();
          alert("Initialization complete! You can now use all features.");
        } else {
          alert("Connection error. Please check your server and try again.");
        }
      });
    } catch (error) {
      console.error("Initialization failed", error);
      alert("Initialization failed. Please try again.");
    }
  });

  function navigateToPage(currentTabUrl, pageNumber) {
    console.log(`Requested page number: ${pageNumber}`);

    const baseUrl = currentTabUrl.split("#")[0];
    const newUrl = `${baseUrl}#page=${pageNumber}`;

    console.log(`Constructed URL: ${newUrl}`);

    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs[0]) {
        chrome.tabs.update(tabs[0].id, { url: newUrl }, () => {
          setTimeout(() => {
            chrome.tabs.reload(tabs[0].id);
          }, 100);
        });
      }
    });
  }

  sendButton.addEventListener("click", async () => {
    const inputText = inputBox.value;

    if (!sendButton.disabled) {
      const requestBody = {
        query: inputText,
      };

      try {
        const response = await fetch("http://localhost:5000/query", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(requestBody),
        });

        if (response.status === 200) {
          const responseData = await response.json();
          responseText.textContent =
            responseData.message || "No response message received.";
          responseContainer.style.display = "block";

          if (
            responseData.page_numbers &&
            responseData.page_numbers.length > 0
          ) {
            pageNumbers = [...new Set(responseData.page_numbers)].sort(
              (a, b) => a - b
            );
            currentPageIndex = 0;
            const firstPage = pageNumbers[currentPageIndex]; // Get the first page number
            chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
              const currentTabUrl = tabs[0].url; // Get the current tab URL
              navigateToPage(currentTabUrl, firstPage);
            });
          }
        } else {
          alert("Error in response. Please try again.");
        }
      } catch (error) {
        console.error("Failed to send the query:", error);
        alert("Failed to send the query. Please try again.");
      }
    } else {
      alert("Please initialize the extension first.");
    }
  });

  // Event listener for the Prev button
  prevButton.addEventListener("click", () => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (currentPageIndex > 0) {
        currentPageIndex--; // Decrement the page index
        const currentTabUrl = tabs[0].url;
        navigateToPage(currentTabUrl, pageNumbers[currentPageIndex]); // Navigate to the previous page
      } else {
        alert("You are already on the first page.");
      }
    });
  });

  // Event listener for the Next button
  nextButton.addEventListener("click", () => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (currentPageIndex < pageNumbers.length - 1) {
        currentPageIndex++; // Increment the page index
        const currentTabUrl = tabs[0].url;
        navigateToPage(currentTabUrl, pageNumbers[currentPageIndex]); // Navigate to the next page
      } else {
        alert("You are already on the last page.");
      }
    });
  });

  // Listen for tab removal to reset initialization status
  chrome.tabs.onRemoved.addListener((tabId, removeInfo) => {
    localStorage.setItem("isInitialized", "false");
  });
});
