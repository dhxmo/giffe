import uuid
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import cv2
from moviepy.editor import VideoFileClip
import numpy as np
import base64

unique_id = str(uuid.uuid4())

options = Options()
options.add_argument("--headless")
options.add_argument("--window-size=400,400")

driver = webdriver.Chrome(options=options)
driver.get('https://roadmap.sh/backend')

# Define the output video file path
output_video_path = f'outputs/{unique_id}.avi'

# Define the codec and frames per second
fourcc = cv2.VideoWriter_fourcc(*'XVID')
fps = 30

# Create a VideoWriter object to save the video
out = cv2.VideoWriter(output_video_path, fourcc, fps, (400, 400))

# Get the initial height of the page
total_height = driver.execute_script("return document.body.scrollHeight")

# Define how much to scroll in each step
scroll_step = 400

# Scroll to the middle
for i in range(total_height // scroll_step // 2):
    driver.execute_script(f"window.scrollTo(0, {i * scroll_step})")
    time.sleep(0.3)  # Adjust the sleep time for the desired speed

    # Capture a screenshot and write it to the video
    screenshot = driver.get_screenshot_as_base64()
    out.write(cv2.imdecode(np.frombuffer(base64.b64decode(screenshot), np.uint8), 1))

# Scroll back to the top
for i in reversed(range(total_height // scroll_step // 2)):
    driver.execute_script(f"window.scrollTo(0, {i * scroll_step})")
    time.sleep(0.3)  # Adjust the sleep time for the desired speed

    # Capture a screenshot and write it to the video
    screenshot = driver.get_screenshot_as_base64()
    out.write(cv2.imdecode(np.frombuffer(base64.b64decode(screenshot), np.uint8), 1))

# Scroll to the bottom
for i in range(total_height // scroll_step // 2, total_height // scroll_step):
    driver.execute_script(f"window.scrollTo(0, {i * scroll_step})")
    time.sleep(0.3)  # Adjust the sleep time for the desired speed

    # Capture a screenshot and write it to the video
    screenshot = driver.get_screenshot_as_base64()
    out.write(cv2.imdecode(np.frombuffer(base64.b64decode(screenshot), np.uint8), 1))


# Release the VideoWriter and close the browser
out.release()
driver.quit()

output_gif_path = f'outputs/{unique_id}.gif'
videoClip = VideoFileClip(output_video_path)
videoClip.write_gif(output_gif_path)
