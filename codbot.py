import cv2
import numpy as np
import time
from PIL import ImageGrab
import pyautogui

window_name = 'Call of Dragons'

async def create_window(window_name):
    """
    Creates a window with the specified name and moves it to the right side of the screen.
    """
    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
    cv2.moveWindow(window_name, 1024, 0)


async def find_image_in_window(image_name, window_name, debug=False):
    # Load the image that you want to detect
    image = cv2.imread(image_name)

    # Take a screenshot of the window
    screenshot = np.array(ImageGrab.grab(bbox=(0, 0, 1024, 768)))
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

    # Try to find the image within the screenshot
    result = cv2.matchTemplate(screenshot, image, cv2.TM_CCOEFF_NORMED)

    # Define a threshold to determine if the image is present in the screenshot
    threshold = 0.8

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
        pyautogui.press('space')
        coordinates = await find_image_in_window('city.PNG', window_name, True)
        if coordinates is not None:
            break

async def main():
    await create_window(window_name)

    while True:

        # Find the image and click on it if found
        coordinates = await find_image_in_window('alliance-help.PNG', window_name, True)
        if coordinates is not None:
            pyautogui.click(x=coordinates[0], y=coordinates[1])
            await reset()

        await asyncio.sleep(0.5)

        # Exit if 'q' is pressed
        if cv2.waitKey(1) == ord('q'):
            break

    # Close the window
    cv2.destroyWindow(window_name)


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
