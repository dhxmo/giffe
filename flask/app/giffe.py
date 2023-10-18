import asyncio
import os
import uuid

import boto3
import cv2
import numpy as np
from botocore.exceptions import NoCredentialsError
from moviepy.video.io.VideoFileClip import VideoFileClip
from pyppeteer import launch

from .config import Config

s3 = boto3.client('s3',
                  aws_access_key_id=Config.s3_giffe_access_key,
                  aws_secret_access_key=Config.s3_secret_access_key)


async def giffer(url):
    unique_id = str(uuid.uuid4())

    browser = await launch(headless=True,
                           ignoreHTTPSErrors=True,  # Ignore HTTPS-related errors
                           args=[
                               '--no-sandbox',
                               '--disable-extensions',
                               '--disable-dev-shm-usage',
                               '--ignore-certificate-errors',  # Ignore SSL certificate errors
                               '--disable-web-security',  # Disable web security, can help bypass CORS issues
                               '--allow-running-insecure-content',  # Allow running insecure content
                               '--disable-infobars'
                           ])
    page = await browser.newPage()

    try:
        # Set the user agent to mimic Google Chrome
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'
        await page.setUserAgent(userAgent=user_agent)
        # Set the Accept-Language header to match the website's locale
        await page.setExtraHTTPHeaders({'Accept-Language': 'en-US,en;q=0.9'})

        width = 500
        height = 500
        await page.setViewport({'width': width, 'height': height})  # Set viewport to HD resolution (1920x1080)
        await page.goto(url)

        # Add another delay before continuing
        await asyncio.sleep(3)

        # Define the output video file path
        output_video_path = f'outputs/{unique_id}.avi'

        # define video codec etc.
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        fps = 26
        frame_delay = 5/fps

        # Create a VideoWriter object to save the video
        out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

        # Get the initial height of the page
        total_height = await page.evaluate('document.body.scrollHeight')

        # Define the number of frames to scroll from top to middle and middle to bottom
        num_frames = 20

        # Scroll smoothly from top to middle
        for i in range(num_frames):
            scroll_position = i * total_height // num_frames
            await page.addStyleTag({'content': 'body::-webkit-scrollbar { width: 0 !important; }'})
            await page.evaluate(f'window.scrollTo(0, {scroll_position})')
            await asyncio.sleep(frame_delay)  # Adjust the sleep time for the frame rate

            # Capture a screenshot and write it to the video
            screenshot = await page.screenshot({'type': 'jpeg'})
            frame = np.frombuffer(screenshot, dtype=np.uint8)
            frame = cv2.imdecode(frame, 1)
            out.write(frame)

        # Scroll smoothly from middle to bottom
        for i in range(num_frames):
            scroll_position = total_height - (i * total_height // num_frames)
            await page.addStyleTag({'content': 'body::-webkit-scrollbar { width: 0 !important; }'})
            await page.evaluate(f'window.scrollTo(0, {scroll_position})')
            await asyncio.sleep(frame_delay)  # Adjust the sleep time for the frame rate

            # Capture a screenshot and write it to the video
            screenshot = await page.screenshot({'type': 'jpeg'})
            frame = np.frombuffer(screenshot, dtype=np.uint8)
            frame = cv2.imdecode(frame, 1)
            out.write(frame)

        # release VideoWriter
        out.release()
    finally:
        await browser.close()

    video_clip = VideoFileClip(output_video_path)
    output_gif_path = f'outputs/{unique_id}.gif'

    if 'twitter.com' in url:
        # Apply the crop_frame function to all frames in the video
        cropped_clip = video_clip.fl_image(twitter_crop_frame)

        # Write the cropped video as a GIF
        cropped_clip.write_gif(output_gif_path, opt='wu')
        cropped_clip.close()
    else:
        video_clip.write_gif(output_gif_path, opt='wu')

    # Close the video clips
    video_clip.close()

    videoClip = VideoFileClip(output_video_path)
    videoClip.write_gif(output_gif_path)

    # Upload the GIF to S3
    s3_key = f'gifs/{unique_id}.gif'  # Specify your desired S3 key

    try:
        s3.upload_file(f'outputs/{unique_id}.gif', Config.s3_bucket_name, s3_key)
        s3_url = f'https://{Config.s3_bucket_name}.s3.amazonaws.com/{s3_key}'

        if os.path.exists(output_video_path):
            os.remove(output_video_path)

        if os.path.exists(output_gif_path):
            os.remove(output_gif_path)

        embed_code = f'''<div id="image-container" style="display: inline-block; border-radius: 10px; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1); width:"><img id="image" alt="GIF" /><div style="position: absolute; top: 10px; right: 10px; background: white; padding: 5px; border-radius: 50%; box-shadow: 0px 0px 5px rgba(0, 0, 0, 0.2;"><button onclick="window.open('{url}', '_blank');">Share</button></div></div><script>var img = document.getElementById('image');img.src = '{s3_url}';</script>'''

        return {
            "s3_url": s3_url,
            "embed_code": embed_code
        }
    except NoCredentialsError:
        return {
            'statusCode': 500,
            'body': 'AWS credentials not found'
        }


# Function to crop the frame by removing 75 pixels from left and bottom boundaries
def twitter_crop_frame(frame):
    # Crop 100 pixels from all boundaries
    return frame[:-75, 75:]
