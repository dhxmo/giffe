import asyncio
import multiprocessing

# from flask import request, jsonify
from quart import Quart, request, jsonify
from . import app
from .giffe import giffer


@app.route('/generate_gif')
async def generate_gif():
    print("url")
    url = request.args.get('url')

    # print("Create a multiprocessing Queue to retrieve the result")
    # output_queue = multiprocessing.Queue()
    # print(output_queue)

    # print("Start a separate process to run giffer")
    # process = multiprocessing.Process(target=run_giffer, args=(url, output_queue))
    # process.start()
    # print("waiting for process to finish")
    # process.join()  # Wait for the process to finish

    print("Run the asynchronous giffer function")
    result = await giffer(url)

    # print("Get the result from the queue")
    # result = output_queue.get()

    return jsonify({'output_gif_path': result})
