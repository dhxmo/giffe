import asyncio
import os
import random
import uuid
from lxml.html import fromstring
from itertools import cycle

import boto3
import cv2
import numpy as np
import requests
from botocore.exceptions import NoCredentialsError
from moviepy.video.io.VideoFileClip import VideoFileClip
from playwright.async_api import async_playwright
from quart import request

from .config import Config
from .utils import logging

s3 = boto3.client('s3',
                  aws_access_key_id=Config.s3_giffe_access_key,
                  aws_secret_access_key=Config.s3_secret_access_key)


def get_proxies():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:10]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
    return proxies


proxies = get_proxies()
proxy_pool = cycle(proxies)


async def giffer(url):
    # viewports and stuff
    width = 500
    height = 500
    scroll_down_pixels = 400

    if 'twitter.com' in url:
        scroll_down_pixels = 500
    elif 'instagram.com' in url:
        scroll_down_pixels = 600
    elif 'youtube.com' in url:
        scroll_down_pixels = 700

    # Define the output video file path
    unique_id = str(uuid.uuid4())
    output_video_path = f'outputs/{unique_id}.avi'

    # capture video and create gif
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True,
                                          args=[
                                              '--no-sandbox',
                                              '--disable-extensions',
                                              '--disable-dev-shm-usage',
                                              '--ignore-certificate-errors',  # Ignore SSL certificate errors
                                              '--disable-web-security',
                                              # Disable web security, can help bypass CORS issues
                                              '--allow-running-insecure-content',  # Allow running insecure content
                                              '--disable-infobars'
                                          ])
        agent_list = [
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
            "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:24.0) Gecko/20100101 Firefox/24.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/91.0.4472.114 "
            "Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 "
            "Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 "
            "Safari/537.36"
        ]
        user_agent = random.choice(agent_list)

        proxy = next(proxy_pool)

        context = await browser.new_context(
            user_agent=user_agent,
            extra_http_headers={'Accept-Language': 'en-US,en;q=0.9'},
            proxy={"server": proxy}
        )

        page = await context.new_page()
        await page.set_viewport_size({'width': width, 'height': height})

        if 'instagram.com' in url:
            login_url = 'https://www.instagram.com/accounts/login/'
            page = await sign_in_to_instagram(page, login_url)

        logging.info("final session:: %s", await page.context.storage_state())

        res = await page.goto(url)
        logging.info("res:: %s", res)

        await simulate_random_mouse_movements(page)

        try:
            # Add random delays between actions
            await random_delay()

            # define video codec etc.
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            fps = 30

            # Create a VideoWriter object to save the video
            out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

            # Define the number of frames to scroll down and then back up
            num_frames = 50  # Adjust this number for the desired smoothness

            # Scroll smoothly from top to 400 pixels down
            for i in range(num_frames):
                if 'twitter.com' in url or 'instagram.com' in url:
                    close_button_clicked = await check_and_click_close_button(page, url)
                else:
                    close_button_clicked = False

                scroll_position = (i * scroll_down_pixels) // num_frames
                await page.add_style_tag(content='body::-webkit-scrollbar { width: 0 !important; }')
                await page.evaluate(f'window.scrollTo(0, {scroll_position})')
                # await asyncio.sleep(slow_frame_delay)  # Adjust the sleep time for the frame rate

                # Capture a screenshot only if the close button was not clicked
                if not close_button_clicked:
                    screenshot = await page.screenshot(type='jpeg')
                    frame = np.frombuffer(screenshot, dtype=np.uint8)
                    frame = cv2.imdecode(frame, 1)
                    out.write(frame)

            # Scroll smoothly from 400 pixels back to the top
            for i in range(num_frames):
                if 'twitter.com' in url or 'instagram.com' in url:
                    close_button_clicked = await check_and_click_close_button(page, url)
                else:
                    close_button_clicked = False

                scroll_position = scroll_down_pixels - (i * scroll_down_pixels) // num_frames
                await page.add_style_tag(content='body::-webkit-scrollbar { width: 0 !important; }')
                await page.evaluate(f'window.scrollTo(0, {scroll_position})')

                # Capture a screenshot only if the close button was not clicked
                if not close_button_clicked:
                    screenshot = await page.screenshot(type='jpeg')
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
            video_clip = video_clip.fl_image(twitter_crop_frame)
        elif 'instagram.com' in url:
            video_clip = video_clip.fl_image(instagram_crop_frame)
        elif 'youtube.com' in url:
            video_clip = video_clip.fl_image(youtube_crop_frame)

        video_clip.write_gif(output_gif_path, opt='wu')

        # Close the video clips
        video_clip.close()

    # Upload the GIF to S3
    s3_key = f'gifs/{unique_id}.gif'  # Specify your desired S3 key

    try:
        s3.upload_file(f'outputs/{unique_id}.gif', Config.s3_bucket_name, s3_key)
        s3_url = f'https://{Config.s3_bucket_name}.s3.amazonaws.com/{s3_key}'

        if os.path.exists(output_video_path):
            os.remove(output_video_path)

        if os.path.exists(output_gif_path):
            os.remove(output_gif_path)

        share_btn_url = get_share_button(url)

        embed_code = f'''<div style="text-align: center; position: relative;"><img src={s3_url} alt="GIF" style="width: 400px; height: 400px; border-radius: 10px; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);" /> <a href={url} target="_blank"> <img src={share_btn_url} alt="Share" style="position: absolute; width: 100px; height: 100px; top: 50%; left: 50%; transform: translate(-50%, -50%);" /> </a> </div>'''

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
    return frame[:-75, 75:]


def instagram_crop_frame(frame):
    return frame[60:, :]


def youtube_crop_frame(frame):
    return frame[60:, :]


def get_share_button(url):
    share_button_map = {
        "twitter.com": "https://giffe.s3.ap-south-1.amazonaws.com/share_buttons/twiiter.svg",
        "instagram.com": "https://giffe.s3.ap-south-1.amazonaws.com/share_buttons/instagram.svg",
        "youtube.com": "https://giffe.s3.ap-south-1.amazonaws.com/share_buttons/youtube.svg",
        "misc": "https://giffe.s3.ap-south-1.amazonaws.com/share_buttons/misc_share.svg"
    }

    if 'twitter.com' in url:
        return share_button_map["twitter.com"]
    elif 'instagram.com' in url:
        return share_button_map["instagram.com"]
    elif 'youtube.com' in url:
        return share_button_map["youtube.com"]
    else:
        return share_button_map["misc"]


# Define a function to check if the close button is present and click it
async def check_and_click_close_button(page, url):
    if await page.query_selector('[aria-label="Close"]'):
        try:
            # Find and click the element with aria-label "Close" if it exists
            await page.click('[aria-label="Close"]')
            # Set the flag to True when the close button is clicked
            return True
        except Exception as e:
            print(f"Error clicking the close button for url {url}: {e}")


async def random_delay():
    min_delay = 1  # Minimum delay in seconds
    max_delay = 5  # Maximum delay in seconds
    delay = random.uniform(min_delay, max_delay)
    await asyncio.sleep(delay)


async def sign_in_to_instagram(page, url):
    await check_and_click_close_button(page, url)
    # Replace these placeholders with your actual Instagram username and password
    instagram_username = Config.insta_username
    instagram_password = Config.insta_password

    logging.info("initial session:: %s", await page.context.storage_state())

    await simulate_random_mouse_movements(page)

    # Navigate to the Instagram login page
    await page.goto('https://www.instagram.com/accounts/login/')

    await simulate_random_mouse_movements(page)

    # Wait for the username input field to appear and type your username
    await page.wait_for_selector('input[name="username"]')
    await page.type('input[name="username"]', instagram_username)

    await simulate_random_mouse_movements(page)

    # Wait for the password input field to appear and type your password
    await page.wait_for_selector('input[name="password"]')
    await page.type('input[name="password"]', instagram_password)

    await simulate_random_mouse_movements(page)

    # Click the "Log In" button to submit the form
    await page.click('button[type="submit"]')

    await simulate_random_mouse_movements(page)

    # capture the storage state (cookies) after logging in
    await page.context.storage_state()

    return page


async def simulate_random_mouse_movements(page):
    # Define the range for random x and y coordinates
    x_min, x_max = 100, 500
    y_min, y_max = 100, 500

    # Generate random x and y coordinates within the defined range
    x_coordinate = random.randint(x_min, x_max)
    y_coordinate = random.randint(y_min, y_max)

    # Move the mouse cursor to the random coordinates
    await page.mouse.move(x_coordinate, y_coordinate)

    # You can add delays and perform additional random movements
    await random_delay()

    # Move the mouse to another random position
    x_coordinate = random.randint(x_min, x_max)
    y_coordinate = random.randint(y_min, y_max)
    await page.mouse.move(x_coordinate, y_coordinate)
