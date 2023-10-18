const urlInput = document.getElementById("urlInput");
const submitButton = document.getElementById("submitButton");
const loader = document.getElementById("loader");
const imageContainer = document.getElementById("imageContainer");
const uploadedImage = document.getElementById("uploadedImage");
const shareButton = document.getElementById("shareButton");
const displayText = document.getElementById("displayText");
const embedCode = document.getElementById("embedCode");
const embedCodeContainer = document.getElementById("embedCodeContainer")


submitButton.addEventListener("click", async () => {
    loader.style.display = "block";
    imageContainer.style.display = "none";
    embedCodeContainer.style.display = "none";

    const url = urlInput.value;

    // Send a query to the Flask endpoint
    const response = await fetch(`/generate_gif?url=${url}`);

    if (response.ok) {
        const data = await response.json();
        uploadedImage.src = data.s3_url;
        embedCode.innerText = data.embed_code;

        imageContainer.style.display = "block";
        embedCodeContainer.style.display = "block";
        loader.style.display = "none";
    } else {
        // If there's an error, hide the loader (spinner)
        loader.style.display = "none";
    }
});