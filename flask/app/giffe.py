import asyncio
import os
import uuid

import boto3
import cv2
import numpy as np
from moviepy.video.io.VideoFileClip import VideoFileClip
from pyppeteer import launch

# s3_giffe_access_key = os.environ['s3_giffe_access_key']
# s3_secret_access_key = os.environ['s3_secret_access_key']
# s3_bucket_name = os.environ['s3_bucket_name']
#
# s3 = boto3.client('s3',
#                   aws_access_key_id=s3_giffe_access_key,
#                   aws_secret_access_key=s3_secret_access_key)


# def giffer(url):
#     unique_id = str(uuid.uuid4())
#
#     options = Options()
#     # options.add_argument("--headless")
#     options.add_argument("--window-size=400,400")
#     options.add_argument("--hide-scrollbars")
#
#     driver = webdriver.Chrome(options=options)
#     driver.get(url)
#
#     # Define the output video file path
#     output_video_path = f'outputs/{unique_id}.avi'
#
#     # Define the codec and frames per second
#     fourcc = cv2.VideoWriter_fourcc(*'XVID')
#     fps = 30
#
#     # Create a VideoWriter object to save the video
#     out = cv2.VideoWriter(output_video_path, fourcc, fps, (400, 400))
#
#     # Get the initial height of the page
#     total_height = driver.execute_script("return document.body.scrollHeight")
#
#     # Define how much to scroll in each step
#     scroll_step = 400
#
#     # Scroll to the middle
#     for i in range(total_height // scroll_step // 4):
#         driver.execute_script(f"window.scrollTo(0, {i * scroll_step})")
#         time.sleep(0.6)  # Adjust the sleep time for the desired speed
#
#         # Capture a screenshot and write it to the video
#         screenshot = driver.get_screenshot_as_base64()
#         out.write(cv2.imdecode(np.frombuffer(base64.b64decode(screenshot), np.uint8), 1))
#
#     # Scroll back to the top
#     for i in reversed(range(total_height // scroll_step // 4)):
#         driver.execute_script(f"window.scrollTo(0, {i * scroll_step})")
#         time.sleep(0.3)  # Adjust the sleep time for the desired speed
#
#         # Capture a screenshot and write it to the video
#         screenshot = driver.get_screenshot_as_base64()
#         out.write(cv2.imdecode(np.frombuffer(base64.b64decode(screenshot), np.uint8), 1))
#
#     # Scroll to the bottom
#     for i in range(total_height // scroll_step // 4, total_height // scroll_step):
#         driver.execute_script(f"window.scrollTo(0, {i * scroll_step})")
#         time.sleep(1.6)  # Adjust the sleep time for the desired speed
#
#         # Capture a screenshot and write it to the video
#         screenshot = driver.get_screenshot_as_base64()
#         out.write(cv2.imdecode(np.frombuffer(base64.b64decode(screenshot), np.uint8), 1))
#
#     # Release the VideoWriter and close the browser
#     out.release()
#     driver.quit()
#
#     output_gif_path = f'outputs/{unique_id}.gif'
#     videoClip = VideoFileClip(output_video_path)
#     videoClip.write_gif(output_gif_path)
#
#     # Upload the GIF to S3
#     s3_key = f'gifs/{unique_id}.gif'  # Specify your desired S3 key
#
#     try:
#         s3.upload_file(f'outputs/{unique_id}.gif', s3_bucket_name, s3_key)
#         s3_url = f'https://{s3_bucket_name}.s3.amazonaws.com/{s3_key}'
#
#         # Delete the local .avi and .gif files
#         local_video_path = f'outputs/{unique_id}.avi'
#         local_gif_path = f'outputs/{unique_id}.gif'
#
#         if os.path.exists(local_video_path):
#             os.remove(local_video_path)
#
#         if os.path.exists(local_gif_path):
#             os.remove(local_gif_path)
#
#         embed_code = f'''<div style="position: relative; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1); border-radius: 10px;"><img src="{s3_url}" alt="GIF" /> <div style="position: absolute; top: 10px; right: 10px; background: white; padding: 5px; border-radius: 50%; box-shadow: 0px 0px 5px rgba(0, 0, 0, 0.2);"> <button onclick="window.open('{url}', '_blank');">Share</button></div></div>'''
#
#         return {
#             "s3_url": s3_url,
#             "embed_code": embed_code
#         }
#     except NoCredentialsError:
#         return {
#             'statusCode': 500,
#             'body': 'AWS credentials not found'
#         }

# async def run_giffer(url):
#     await giffer(url, output_queue)


async def giffer(url):
    unique_id = str(uuid.uuid4())

    print("Launch a headless Chromium browser")
    browser = await launch(headless=True)
    page = await browser.newPage()
    await page.setViewport({'width': 400, 'height': 400})
    await page.goto(url)

    # Define the output video file path
    output_video_path = f'outputs/{unique_id}.avi'

    print("Define the codec and frames per second")
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    fps = 24

    # Create a VideoWriter object to save the video
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (400, 400))

    # Get the initial height of the page
    total_height = await page.evaluate('document.body.scrollHeight')

    # Define how much to scroll in each step
    scroll_step = 400

    print("Scroll to the middle")
    for i in range(total_height // scroll_step // 4):
        await page.evaluate(f'window.scrollTo(0, {i * scroll_step})')
        await asyncio.sleep(2.6)  # Adjust the sleep time for the desired speed

        # Capture a screenshot and write it to the video
        screenshot = await page.screenshot()
        image_np = cv2.imdecode(np.frombuffer(screenshot, np.uint8), 1)
        out.write(image_np)

    print("Scroll back to the top")
    for i in reversed(range(total_height // scroll_step // 4)):
        await page.evaluate(f'window.scrollTo(0, {i * scroll_step})')
        await asyncio.sleep(0.3)  # Adjust the sleep time for the desired speed

        # Capture a screenshot and write it to the video
        screenshot = await page.screenshot()
        image_np = cv2.imdecode(np.frombuffer(screenshot, np.uint8), 1)
        out.write(image_np)

    print("Scroll to the bottom")
    for i in range(total_height // scroll_step // 4, total_height // scroll_step):
        await page.evaluate(f'window.scrollTo(0, {i * scroll_step})')
        await asyncio.sleep(3.0)  # Adjust the sleep time for the desired speed

        # Capture a screenshot and write it to the video
        screenshot = await page.screenshot()
        image_np = cv2.imdecode(np.frombuffer(screenshot, np.uint8), 1)
        out.write(image_np)

    print("Release the VideoWriter and close the browser")
    out.release()
    await browser.close()

    print("Convert the video to GIF")
    video_clip = VideoFileClip(output_video_path)
    output_gif_path = f'outputs/{unique_id}.gif'
    video_clip.write_gif(output_gif_path)

    return output_gif_path
