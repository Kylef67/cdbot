import cv2
import numpy as np
import time
from PIL import ImageGrab
import pyautogui
import random

window_name = 'Call of Dragons'
global_debug = True
global_time_delay = (1, 2)

# Helpers

async def create_window(window_name):
    """
    Creates a window with the specified name and moves it to the right side of the screen.
    """
    if global_debug:
        cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
        cv2.moveWindow(window_name, 1024, 0)


async def find_image_in_window(image_name, window_name, debug=False, threshold=0.9, timeout=5):
    # Load the image that you want to detect
    image = cv2.imread(image_name)
    log(f"Finding image {image_name}")

    # Take a screenshot of the window
    screenshot = np.array(ImageGrab.grab(bbox=(0, 0, 1024, 768)))
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

    # Set the start time for the timeout
    start_time = time.monotonic()

    # Try to find the image within the screenshot
    while True:
        result = cv2.matchTemplate(screenshot, image, cv2.TM_CCOEFF_NORMED)

        # Check if the threshold has been exceeded
        locations = np.where(result >= threshold)
        if locations[0].size > 0:
            # Loop through all the locations where the image was found and draw a green rectangle around each one
            for pt in zip(*locations[::-1]):
                cv2.rectangle(screenshot, pt, (pt[0] + image.shape[1], pt[1] + image.shape[0]), (0, 255, 0), 2)

            if debug:
                # Show the screenshot with the green rectangle around the found image
                cv2.imshow(window_name, screenshot)
                cv2.waitKey(1)

            # Return the center of the found image
            x = int(locations[1][0] + image.shape[1] / 2)
            y = int(locations[0][0] + image.shape[0] / 2)
            log(f"Image found at {x},{y}")
            return x, y

        if debug:
            # Show the screenshot without the green rectangle
            cv2.imshow(window_name, screenshot)
            cv2.waitKey(1)

        # Check if the timeout has been exceeded
        if time.monotonic() - start_time > timeout:
            break

        # Take a new screenshot and try again
        screenshot = np.array(ImageGrab.grab(bbox=(0, 0, 1024, 768)))
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

    # Return None if the image is not found within the timeout period
    log(f"Image not found {image_name}")
    return None


async def click_images_in_sequence(images, window_name, confidence=0.8, timeout=30):
    start_time = time.time()
    for image in images:
        offset_x, offset_y = 0, 0
        if isinstance(image, list):
            image_path, offset_x, offset_y = image[0], image[1], image[2]
        else:
             image_path = image
        target = await find_image_in_window(image_path, window_name, global_debug, confidence)
        while target is None and time.time() - start_time < timeout:
            await asyncio.sleep(0.5)
            target = await find_image_in_window(image_path, window_name, global_debug, confidence)
        if target is None:
            print(f"Failed to find {image_path} within {timeout} seconds.")
            await reset()
            break
        await click(x=target[0] + offset_x, y=target[1] + offset_y)
        await asyncio.sleep(0.5)

async def click(x, y):
    await asyncio.sleep(0.5)
    log(f"Clicking {x}, {y}")
    pyautogui.mouseDown(x,y)
    await asyncio.sleep(0.5)
    pyautogui.mouseUp(x,y)

async def press(key):
    await asyncio.sleep(0.5)
    log(f"Pressing {key}")
    pyautogui.keyDown(key)
    await asyncio.sleep(0.5)
    pyautogui.keyUp(key)


def log(msg):
    if global_debug:
        print(msg)

# Functions
async def reset():
    while True:
        coordinates = await find_image_in_window('city.PNG', window_name, global_debug)
        if coordinates is not None:
            break
        await press('esc')
        await press('space')

async def alliance():
    alliance = await find_image_in_window('alliance-help.PNG', window_name, global_debug)

    if alliance is not None:
        await click(x=alliance[0], y=alliance[1])
     
async def scout():
    await click_images_in_sequence(["scout-city.PNG", "scout-available-explore.PNG", "scout-explore.PNG", "scout-march.PNG"], window_name, 0.9, 5)


async def supplies():
    time.sleep(2)
    found = await find_image_in_window('supplies-nearby.PNG', window_name, global_debug)

    if found is not None:
        await click(x=found[0], y=found[1])
        time.sleep(2)
        await click(512, 400)

async def trail_elks():
    await click_images_in_sequence(["elk-building.PNG", "elk-train.PNG", "train-button.PNG"], window_name, 0.9, 5)

async def train_treant():
    await click_images_in_sequence(["treant-building.PNG", "treant-train.PNG", "train-button.PNG"], window_name, 0.9, 5)

async def train_archer():
    await click_images_in_sequence(["archer-building.PNG", "archer-train.PNG", "train-button.PNG"], window_name, 0.9, 5)

async def train_magic():
    await click_images_in_sequence(["magic-building.PNG", "magic-train.PNG", "train-button.PNG"], window_name, 0.9, 5)

async def train_flying():
    await click_images_in_sequence(["fly-building.PNG", "fly-train.PNG", "train-button.PNG"], window_name, 0.9, 5)
    
async def main():
    time.sleep(2)
    await create_window(window_name)


    await reset()
 
    while True:

        await alliance()
        #await scout()
        await trail_elks()
        await train_treant()
        await train_archer()
        await train_magic()
        await train_flying()
        #await supplies()

        #await reset()

        #time.sleep(1)
        # Exit if 'q' is pressed
        if cv2.waitKey(1) == ord('q'):
            break

    # Close the window
    cv2.destroyWindow(window_name)


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
