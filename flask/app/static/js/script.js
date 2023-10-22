const urlInput = document.getElementById("urlInput");
const submitButton = document.getElementById("submitButton");

const loader = document.getElementById("loader");

const imageContainer = document.getElementById("imageContainer");
const uploadedImage = document.getElementById("uploadedImage");

const embedContainer = document.getElementById('embedContainer');
const embedCodeContainer = document.getElementById("embedCodeContainer")
const embedCode = document.getElementById("embedCode");

const copyToClipboard = document.getElementById('copyToClipboard');
const copyToClipboardSpan = document.getElementById('copyToClipboardSpan');

const notification = document.getElementById("notification");
const notificationText = document.getElementById("notification-text");

submitButton.addEventListener("click", async () => {
    showLoader();
    const url = urlInput.value;

    // reset clipboard
    copyToClipboard.style.display = 'inline';
    copyToClipboardSpan.style.display = 'none';

    // Check if the URL is valid
    if (isValidUrl(url)) {
        // Send a query to the Flask endpoint
        const response = await fetch(`/generate_gif?url=${url}`);

        if (response.ok) {
            const data = await response.json();
            uploadedImage.src = data.s3_url;
            embedCode.innerText = data.embed_code;

            showEmbedContainer();
        } else {
            // If there's an error, show a custom notification
            showNotification("Error: Unable to fetch data from the server");
            // If there's an error, hide the loader (spinner)
            loader.style.display = "none";
        }
    } else {
         // Show a custom notification for an invalid URL
        showNotification("Please enter a valid URL");
        loader.style.display = "none";
    }
});

copyToClipboard.addEventListener('click', () => {
    const codeToCopy = embedCode.innerText;
    navigator.clipboard.writeText(codeToCopy);
    copyToClipboard.style.display = 'none';
    copyToClipboardSpan.style.display = 'inline';
});

function showEmbedContainer() {
    loader.style.display = "none";
    imageContainer.style.display = "block";
    embedContainer.style.display = 'block';
}

function showLoader() {
    loader.style.display = "block";
    imageContainer.style.display = "none";
    embedContainer.style.display = "none";
}

function isValidUrl(inputUrl) {
    try {
        console.log("trying to return true")
        new URL(inputUrl);
        return true;
    } catch {
        console.log("returning false")
        return false;
    }
}

// Function to show the custom notification
function showNotification(message) {
    notificationText.innerText = message;
    notification.classList.add("show");

    // Automatically hide the notification after a few seconds (adjust as needed)
    setTimeout(() => {
        notification.classList.remove("show");
    }, 3000); // Hide after 5 seconds
}