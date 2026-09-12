import cv2
import numpy as np
from tkinter import Tk, filedialog, Label, Button, Scale, HORIZONTAL, Frame, Scrollbar, Canvas, Entry
from PIL import Image, ImageTk  # Ensure PIL is imported

# Initialize main application window
root = Tk()
root.title("Photoshop Sederhana")
root.geometry("1000x800")  # Set the window size
root.resizable(True, True)  # Make the window resizable

# Global variables
img = None
img_display = None
img_original = None
undo_stack = []
original_file_path = None

# Helper functions
def display_image(img):
    im = Image.fromarray(img)
    imgtk = ImageTk.PhotoImage(image=im)
    label.imgtk = imgtk
    label.configure(image=imgtk)

def save_state():
    global undo_stack, img_display
    if img_display is not None:
        undo_stack.append(img_display.copy())

def open_image():
    global img, img_display, img_original, original_file_path
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.png *.bmp")])
    
    if file_path:
        original_file_path  = file_path
        img = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
        if img.shape[2] == 4:  # Check if the image has an alpha channel
            img_display = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
        else:
            img_display = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_original = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        save_state()
        display_image(img_display)
        # Ensure the control panel stays on the left
        controls_frame.lift()

def save_image():
    global img_display
    file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Files", "*.png")])
    if file_path:
        # Save with alpha channel if available
        if img_display.shape[2] == 4:  # RGBA
            cv2.imwrite(file_path, cv2.cvtColor(img_display, cv2.COLOR_RGBA2BGRA))
        else:  # RGB
            cv2.imwrite(file_path, cv2.cvtColor(img_display, cv2.COLOR_RGB2BGR))

def undo():
    global undo_stack, img_display
    if undo_stack:
        img_display = undo_stack.pop()
        display_image(img_display)
        
        
def reset_image():
    global img, img_display, img_original, undo_stack, original_file_pathfile_path
    if original_file_path:
        img = cv2.imread(original_file_path, cv2.IMREAD_UNCHANGED)
        if img is not None:
            if img.shape[2] == 4:  # Check if the image has an alpha channel
                img_display = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
            else:
                img_display = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_original = img_display.copy()  # Simpan gambar asli
            undo_stack.clear()  # Bersihkan tumpukan undo
            display_image(img_original)  # Tampilkan gambar asli
            reset_sliders()
        else:
            print("Failed to load the image.")
    else:
        print("Original file path is not set.")

def apply_changes():
    global img, img_display, img_original
    img = img_display.copy()
    img_original = img_display.copy()
    reset_sliders()

def reset_sliders():
    brightness_scale.set(0)
    contrast_scale.set(1.0)
    rotation_scale.set(0)
    scale_slider.set(1.0)
    blur_scale.set(0)

def to_grayscale():
    global img_display
    save_state()
    img_gray = cv2.cvtColor(img_display, cv2.COLOR_RGB2GRAY)
    img_display = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2RGB)
    display_image(img_display)

def to_binary():
    global img_display
    save_state()
    img_gray = cv2.cvtColor(img_display, cv2.COLOR_RGB2GRAY)
    _, img_bin = cv2.threshold(img_gray, 128, 255, cv2.THRESH_BINARY)
    img_display = cv2.cvtColor(img_bin, cv2.COLOR_GRAY2RGB)
    display_image(img_display)

def adjust_brightness(value):
    global img_display, img_original
    save_state()
    temp_img = cv2.convertScaleAbs(img_original, alpha=1, beta=int(value))
    img_display = temp_img
    display_image(img_display)

def adjust_contrast(value):
    global img_display, img_original
    save_state()
    temp_img = cv2.convertScaleAbs(img_original, alpha=float(value), beta=0)
    img_display = temp_img
    display_image(img_display)

def rotate_image(angle):
    global img_original, img_display
    save_state()
    h, w = img_original.shape[:2]
    center = (w // 2, h // 2)
    matrix = cv2.getRotationMatrix2D(center, int(angle), 1.0)
    cos = np.abs(matrix[0, 0])
    sin = np.abs(matrix[0, 1])
    new_w = int((h * sin) + (w * cos))
    new_h = int((h * cos) + (w * sin))
    matrix[0, 2] += (new_w / 2) - center[0]
    matrix[1, 2] += (new_h / 2) - center[1]

    if img_original.shape[2] == 4:  # RGBA
        temp_img = cv2.warpAffine(
            img_original, matrix, (new_w, new_h), borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0)
        )
    else:  # RGB
        temp_img = cv2.warpAffine(
            img_original, matrix, (new_w, new_h), borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255)
        )

    # Ensure image has alpha channel
    if img_original.shape[2] == 3:  # RGB
        b, g, r = cv2.split(img_original)
        alpha = np.ones(b.shape, dtype=b.dtype) * 255
        img_original = cv2.merge((b, g, r, alpha))

    # Perform rotation with transparency
    temp_img = cv2.warpAffine(
        img_original, matrix, (new_w, new_h), borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0)
    )

    img_display = temp_img
    display_image(img_display)


def flip_image(direction):
    global img_display
    save_state()
    if direction == "horizontal":
        img_display = cv2.flip(img_display, 1)
    elif direction == "vertical":
        img_display = cv2.flip(img_display, 0)
    display_image(img_display)

def adjust_sharpen():
    global img_display, img_original
    save_state()
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    temp_img = cv2.filter2D(img_original, -1, kernel)
    img_display = temp_img
    display_image(img_display)

def adjust_blur(value):
    global img_display, img_original
    save_state()
    value = int(value)
    if value == 0:
        img_display = img_original
        display_image(img_display)
    else:
        temp_img = cv2.GaussianBlur(img_original, (5, 5), value)
        img_display = temp_img
    display_image(img_display)

def scale_image(scale_factor):
    global img_original, img_display
    save_state()
    scale_factor = float(scale_factor)

    if img_original is not None: 
        h, w = img_original.shape[:2]
        new_w, new_h = int(w * scale_factor), int(h * scale_factor)

        if new_w > 0 and new_h > 0:
            try:
                scaled_img = cv2.resize(img_original, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
                img_display = scaled_img # Convert to RGB
                display_image(img_display)
            except Exception as e:
                print(f"Error during scaling: {e}")
        else:
            print("Error: Image dimensions too small after scaling.")
    else:
        print("Error: No image to resize.")

def convert_to_rgb():
    global img_display
    img_display = cv2.cvtColor(img_display, cv2.COLOR_BGR2RGB)
    display_image(img_display)

# GUI Layout
main_frame = Frame(root)
main_frame.pack(fill="both", expand=True)

# Controls area with scrollbar
controls_frame = Frame(main_frame, bg="lightgray", width=200)
controls_frame.pack_propagate(False)  # Prevent the frame from resizing to fit its content
controls_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ns")

canvas_controls = Canvas(controls_frame, width=200)
scrollbar_controls = Scrollbar(controls_frame, orient="vertical", command=canvas_controls.yview)
scrollable_frame_controls = Frame(canvas_controls)

scrollable_frame_controls.bind(
    "<Configure>",
    lambda e: canvas_controls.configure(
        scrollregion=canvas_controls.bbox("all")
    )
)

canvas_controls.create_window((0, 0), window=scrollable_frame_controls, anchor="nw")
canvas_controls.configure(yscrollcommand=scrollbar_controls.set)

canvas_controls.pack(side="left", fill="both", expand=True)
scrollbar_controls.pack(side="right", fill="y")

# Image display area with scrollbars
image_frame = Frame(main_frame, bg="gray")
image_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

canvas_image = Canvas(image_frame, bg="gray")
scrollbar_image_y = Scrollbar(image_frame, orient="vertical", command=canvas_image.yview)
scrollbar_image_x = Scrollbar(image_frame, orient="horizontal", command=canvas_image.xview)

canvas_image.configure(yscrollcommand=scrollbar_image_y.set, xscrollcommand=scrollbar_image_x.set)

canvas_image.pack(side="left", fill="both", expand=True)
# scrollbar_image_y.pack(side="right", fill="y")
# scrollbar_image_x.pack(side="bottom", fill="x")

label = Label(canvas_image)
label.pack()

# Load and resize arrow icons
arrow_left_img = Image.open(("assets/panah_63398.png")).resize((24, 24), Image.Resampling.LANCZOS)
arrow_left_img = ImageTk.PhotoImage(arrow_left_img)

arrow_up_img = Image.open("assets/pngtree-up-and-down-arrows-png-image_4420668.jpg").resize((24, 24), Image.Resampling.LANCZOS)
arrow_up_img = ImageTk.PhotoImage(arrow_up_img)

btn_flip_h = Button(scrollable_frame_controls, image=arrow_left_img, command=lambda: flip_image("horizontal"))
btn_flip_h.grid(row=0, column=0, padx=2, pady=2)

btn_flip_v = Button(scrollable_frame_controls, image=arrow_up_img, command=lambda: flip_image("vertical"))
btn_flip_v.grid(row=0, column=1, padx=2, pady=2)

# Buttons and controls
btn_open = Button(scrollable_frame_controls, text="Open", command=open_image)
btn_open.grid(row=1, column=0, padx=2, pady=2)

btn_save = Button(scrollable_frame_controls, text="Save", command=save_image)
btn_save.grid(row=1, column=1, padx=2, pady=2)

btn_undo = Button(scrollable_frame_controls, text="Undo", command=undo)
btn_undo.grid(row=2, column=0, padx=2, pady=2)

btn_reset = Button(scrollable_frame_controls, text="Reset to Original", command=reset_image)
btn_reset.grid(row=2, column=1, padx=2, pady=2)

btn_apply = Button(scrollable_frame_controls, text="Apply", command=apply_changes)
btn_apply.grid(row=3, column=0, padx=2, pady=2)

btn_gray = Button(scrollable_frame_controls, text="Grayscale", command=to_grayscale)
btn_gray.grid(row=3, column=1, padx=2, pady=2)

btn_bin = Button(scrollable_frame_controls, text="Binary", command=to_binary)
btn_bin.grid(row=4, column=0, padx=2, pady=2)

btn_convert_rgb = Button(scrollable_frame_controls, text="Convert to RGB", command=convert_to_rgb)
btn_convert_rgb.grid(row=4, column=1, padx=2, pady=2)

# Brightness controls
brightness_label = Label(scrollable_frame_controls, text="Brightness")
brightness_label.grid(row=6, column=0, padx=2, pady=2)
brightness_scale = Scale(scrollable_frame_controls, from_=-100, to=100, orient=HORIZONTAL, command=adjust_brightness)
brightness_scale.grid(row=6, column=1, padx=2, pady=2)
btn_brightness_increase = Button(scrollable_frame_controls, text="+", command=lambda: brightness_scale.set(brightness_scale.get() + 10))
btn_brightness_increase.grid(row=6, column=2, padx=2, pady=2)
btn_brightness_decrease = Button(scrollable_frame_controls, text="-", command=lambda: brightness_scale.set(brightness_scale.get() - 10))
btn_brightness_decrease.grid(row=6, column=3, padx=2, pady=2)

# Contrast controls
contrast_label = Label(scrollable_frame_controls, text="Contrast")
contrast_label.grid(row=7, column=0, padx=2, pady=2)
contrast_scale = Scale(scrollable_frame_controls, from_=0.5, to=3.0, resolution=0.1, orient=HORIZONTAL, command=adjust_contrast)
contrast_scale.set(1.0)  # Set default value to 1
contrast_scale.grid(row=7, column=1, padx=2, pady=2)
btn_contrast_increase = Button(scrollable_frame_controls, text="+", command=lambda: contrast_scale.set(contrast_scale.get() + 0.1))
btn_contrast_increase.grid(row=7, column=2, padx=2, pady=2)
btn_contrast_decrease = Button(scrollable_frame_controls, text="-", command=lambda: contrast_scale.set(contrast_scale.get() - 0.1))
btn_contrast_decrease.grid(row=7, column=3, padx=2, pady=2)

# Rotation controls
rotation_label = Label(scrollable_frame_controls, text="Rotate")
rotation_label.grid(row=8, column=0, padx=2, pady=2)
rotation_scale = Scale(scrollable_frame_controls, from_=-180, to=180, orient=HORIZONTAL, command=rotate_image)
rotation_scale.grid(row=8, column=1, padx=2, pady=2)
btn_rotation_increase = Button(scrollable_frame_controls, text="+", command=lambda: rotation_scale.set(rotation_scale.get() + 10))
btn_rotation_increase.grid(row=8, column=2, padx=2, pady=2)
btn_rotation_decrease = Button(scrollable_frame_controls, text="-", command=lambda: rotation_scale.set(rotation_scale.get() - 10))
btn_rotation_decrease.grid(row=8, column=3, padx=2, pady=2)

# Scale controls
scale_label = Label(scrollable_frame_controls, text="Scale")
scale_label.grid(row=9, column=0, padx=2, pady=2)
scale_slider = Scale(scrollable_frame_controls, from_=0.1, to=2.0, resolution=0.1, orient=HORIZONTAL, command=scale_image)
scale_slider.set(1.0)
scale_slider.grid(row=9, column=1, padx=2, pady=2)
btn_scale_increase = Button(scrollable_frame_controls, text="+", command=lambda: scale_slider.set(scale_slider.get() + 0.1))
btn_scale_increase.grid(row=9, column=2, padx=2, pady=2)
btn_scale_decrease = Button(scrollable_frame_controls, text="-", command=lambda: scale_slider.set(scale_slider.get() - 0.1))
btn_scale_decrease.grid(row=9, column=3, padx=2, pady=2)

# Sharpen controls
sharpen_label = Label(scrollable_frame_controls, text="Sharpen")
sharpen_label.grid(row=10, column=0, padx=2, pady=2)
# sharpen_scale = Scale(scrollable_frame_controls, from_=0, to=10, orient=HORIZONTAL, command=adjust_sharpen)
# sharpen_scale.grid(row=10, column=1, padx=2, pady=2)
btn_sharpen_increase = Button(scrollable_frame_controls, text="Sharpen!!", command=adjust_sharpen)
btn_sharpen_increase.grid(row=10, column=1, padx=2, pady=2)

# Blur controls
blur_label = Label(scrollable_frame_controls, text="Blur")
blur_label.grid(row=11, column=0, padx=2, pady=2)
blur_scale = Scale(scrollable_frame_controls, from_=0, to=10, orient=HORIZONTAL, command=adjust_blur)
blur_scale.grid(row=11, column=1, padx=2, pady=2)
btn_blur_increase = Button(scrollable_frame_controls, text="+", command=lambda: blur_scale.set(blur_scale.get() + 1))
btn_blur_increase.grid(row=11, column=2, padx=2, pady=2)
btn_blur_decrease = Button(scrollable_frame_controls, text="-", command=lambda: blur_scale.set(blur_scale.get() - 1))
btn_blur_decrease.grid(row=11, column=3, padx=2, pady=2)

# Make the grid layout responsive
main_frame.grid_rowconfigure(0, weight=1)
main_frame.grid_columnconfigure(1, weight=1)

# Start application
root.mainloop()