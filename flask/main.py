import uuid
import os
import io
import time
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import numpy as np
import base64 


def giffer(url):
    unique_id = str(uuid.uuid4())
    print("unique_id", unique_id)

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--headless")
    options.add_argument("--window-size=400,400")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--user-data-dir=/tmp/user-data')
    options.add_argument('--hide-scrollbars')
    options.add_argument('--enable-logging')
    options.add_argument('--log-level=0')
    options.add_argument('--v=99')
    options.add_argument('--single-process')
    options.add_argument('--data-path=/tmp/data-path')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--homedir=/tmp')
    options.add_argument('--disk-cache-dir=/tmp/cache-dir')
    options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    
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