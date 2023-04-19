import cv2
import numpy as np
import time
from PIL import ImageGrab
import pyautogui

window_name = 'Call of Dragons'
global_debug = False

async def create_window(window_name):
    """
    Creates a window with the specified name and moves it to the right side of the screen.
    """
    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
    cv2.moveWindow(window_name, 1024, 0)


async def find_image_in_window(image_name, window_name, debug=False, threshold=0.9):
    # Load the image that you want to detect
    image = cv2.imread(image_name)

    # Take a screenshot of the window
    screenshot = np.array(ImageGrab.grab(bbox=(0, 0, 1024, 768)))
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

    # Try to find the image within the screenshot
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
        return x, y

    if debug:
        # Show the screenshot without the green rectangle
        cv2.imshow(window_name, screenshot)
        cv2.waitKey(1)

    # Return None if the image is not found
    return None


async def reset():
    while True:
        
        coordinates = await find_image_in_window('city.PNG', window_name, global_debug)
        if coordinates is not None:
            break
        pyautogui.press('space')
        time.sleep(1)

async def alliance():
    alliance = await find_image_in_window('alliance-help.PNG', window_name, global_debug)

    if alliance is not None:
        pyautogui.click(x=alliance[0], y=alliance[1])
        time.sleep(1)
        await reset()
     
async def scout():
    scout = await find_image_in_window('scout-city.PNG', window_name, global_debug)

    if scout is not None:
        pyautogui.click(x=scout[0], y=scout[1])
        time.sleep(2)
        available = await find_image_in_window('scout-available-explore.PNG', window_name, global_debug)

        if available is not None:
            await click_images_in_sequence(["scout-available-explore.PNG", "scout-explore.PNG", "scout-march.PNG"], window_name, 0.7)
            await reset()
            time.sleep(1)
        else:
            time.sleep(1)
            pyautogui.press('esc')
            await reset() 
        time.sleep(1)  

async def click_images_in_sequence(images, window_name, confidence=0.8, timeout=30):
    start_time = time.time()
    for image in  images:
        target = await find_image_in_window(image, window_name, global_debug, confidence)
        while target is None and time.time() - start_time < timeout:
            await asyncio.sleep(0.5)
            target = await find_image_in_window(image, window_name, global_debug, confidence)
        if target is None:
            print(f"Failed to find {image} within {timeout} seconds.")
            break
        pyautogui.click(x=target[0], y=target[1])
        await asyncio.sleep(0.5)

async def main():
    await create_window(window_name)

    while True:

        await alliance()
        await scout()

        time.sleep(1)
        # Exit if 'q' is pressed
        if cv2.waitKey(1) == ord('q'):
            break

    # Close the window
    cv2.destroyWindow(window_name)


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
