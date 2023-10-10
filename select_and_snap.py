import tkinter as tk
import pyautogui
import pytesseract
from PIL import Image, ImageTk
import subprocess
import time

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

global_region = None  # Global variable to store the region of interest

class CaptureScreenshot:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Hide main window

        # Get screen dimensions
        screen_width, screen_height = self.root.winfo_screenwidth(), self.root.winfo_screenheight()

        # Set geometry to cover left half of screen
        self.root.geometry(f"{screen_width // 2}x{screen_height}+0+0")  # width x height + x_offset + y_offset

        self.start_point = None
        self.end_point = None

        self.canvas = tk.Canvas(self.root, cursor="cross", bd=0, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=tk.YES)

        self.refresh_canvas()  # Now it's correctly placed after canvas creation

        self.canvas.create_image(0, 0, image=self.screenshot_img, anchor=tk.NW)
        self.canvas.bind("<ButtonPress-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        self.rect = None


    def on_click(self, event):
        if not self.start_point:
            self.start_point = (event.x, event.y)

    def on_drag(self, event):
        if not self.start_point:
            return
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_point[0], self.start_point[1], event.x, event.y,
                                                 outline="green")

    def on_release(self, event):
        global global_region
        self.end_point = (event.x, event.y)
        x1, y1 = self.start_point
        x2, y2 = self.end_point

        left = min(x1, x2)
        top = min(y1, y2)
        width = abs(x2 - x1)
        height = abs(y2 - y1)

        global_region = (left, top, width, height)
        self.root.quit()

    def capture(self):
        global global_region
        if not global_region:
            self.root.deiconify()
            self.root.mainloop()
            self.root.withdraw()
        return pyautogui.screenshot(region=global_region)

    def refresh_canvas(self):
        self.screenshot_np = pyautogui.screenshot()
        self.screenshot_img = ImageTk.PhotoImage(self.screenshot_np)
        self.canvas.create_image(0, 0, image=self.screenshot_img, anchor=tk.NW)

def save_text_to_notepad(text):
    with open("temp_text.txt", "a") as file:
        file.write(text + '\n')

    subprocess.run(["notepad", "temp_text.txt"])

def capture_and_process():
    global screenshot_captor
    screenshot = screenshot_captor.capture()
    if screenshot:
        text = pytesseract.image_to_string(screenshot)
        if text:
            save_text_to_notepad(text)
            print("Text has been saved to notepad!")
        else:
            print("No text detected.")
    else:
        print("No area selected.")

def main():
    global screenshot_captor
    screenshot_captor = CaptureScreenshot()

    input("Press Enter to start capturing an area. After dragging, release the mouse to process.")

    choice = input("Do you want to run on loop (enter 'loop') or a specific number of times (enter the number): ")

    if choice == 'loop':
        while True:
            screenshot_captor.refresh_canvas()
            capture_and_process()
            time.sleep(2)
    else:
        num_iterations = int(choice)
        for _ in range(num_iterations):
            screenshot_captor.refresh_canvas()
            capture_and_process()
            time.sleep(2)

if __name__ == "__main__":
    main()
