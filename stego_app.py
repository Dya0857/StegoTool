from tkinterdnd2 import TkinterDnD, DND_FILES
import tkinter as tk
from tkinter import filedialog, messagebox
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import os


# Constants
DELIMITER = "#####"
DEBUG_MODE = True  # Toggle for binary printing

# ---------------------- ENCODING FUNCTION ----------------------
def encode_image(image_path, text_input=None, file_input=None):
    try:
        img = Image.open(image_path)
        img = img.convert("RGB")
        pixels = img.load()

        # Prepare the data to embed
        if text_input:
            data = text_input + DELIMITER
        else:
            with open(file_input, "r", encoding="utf-8") as f:
                data = f.read() + DELIMITER

        # Convert data to binary
        bits = ''.join(format(ord(char), '08b') for char in data)

        # Debug: Print binary representation
        if DEBUG_MODE:
            if len(bits) <= 256:
                print(f"[DEBUG] Full binary: {bits}")
            else:
                print(f"[DEBUG] Binary (first 256 bits): {bits[:256]}...")
            print(f"[DEBUG] Total bits: {len(bits)}")

        # Calculate available capacity
        capacity_bits = img.size[0] * img.size[1] * 3
        print(f"[INFO] Image capacity: {capacity_bits} bits (~{capacity_bits // 8} bytes)")
        required_bits = len(bits)
        print(f"[INFO] Data size to embed: {required_bits} bits (~{required_bits // 8} bytes)")

        if required_bits > capacity_bits:
            messagebox.showerror("Error", "File too large for the selected image!")
            print("[ERROR] Embedding aborted: Not enough capacity.")
            return

        # Embed the data into the image
        bit_index = 0
        for y in range(img.size[1]):
            for x in range(img.size[0]):
                if bit_index < required_bits:
                    r, g, b = pixels[x, y]
                    r = (r & ~1) | int(bits[bit_index]) if bit_index < required_bits else r
                    bit_index += 1
                    g = (g & ~1) | int(bits[bit_index]) if bit_index < required_bits else g
                    bit_index += 1
                    b = (b & ~1) | int(bits[bit_index]) if bit_index < required_bits else b
                    bit_index += 1
                    pixels[x, y] = (r, g, b)

        # Save the new image
        output_path = os.path.splitext(image_path)[0] + "_encoded.png"
        img.save(output_path)
        messagebox.showinfo("Success", f"Data embedded successfully!\nSaved as {output_path}")
        print(f"[INFO] Embedding completed. File saved: {output_path}")
        reset_fields()
    except Exception as e:
        messagebox.showerror("Error", str(e))
        print(f"[ERROR] {e}")

# ---------------------- DECODING FUNCTION ----------------------
def decode_image(image_path):
    try:
        img = Image.open(image_path)
        img = img.convert("RGB")
        pixels = img.load()

        bits = ""
        for y in range(img.size[1]):
            for x in range(img.size[0]):
                r, g, b = pixels[x, y]
                bits += str(r & 1)
                bits += str(g & 1)
                bits += str(b & 1)

        # Convert binary to text
        decoded_data = ""
        for i in range(0, len(bits), 8):
            byte = bits[i:i + 8]
            decoded_data += chr(int(byte, 2))
            if decoded_data.endswith(DELIMITER):
                decoded_data = decoded_data.replace(DELIMITER, "")
                break

        if decoded_data:
            # Save decoded text to file
            output_file = "decoded_text.txt"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(decoded_data)
            messagebox.showinfo("Success", f"Data extracted!\nSaved in {output_file}")
            print(f"[INFO] Data extracted: {decoded_data[:100]}...")
        else:
            messagebox.showwarning("Warning", "No hidden data found!")
            print("[INFO] No hidden data detected.")
        reset_fields()
    except Exception as e:
        messagebox.showerror("Error", str(e))
        print(f"[ERROR] {e}")

# ---------------------- GUI HANDLERS ----------------------
def select_image():
    filename = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.bmp;*.jpg;*.jpeg")])
    if filename:
        image_entry.delete(0, tk.END)
        image_entry.insert(0, filename)

def select_file():
    filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if filename:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, filename)

def reset_fields():
    image_entry.delete(0, tk.END)
    text_entry.delete("1.0", tk.END)
    file_entry.delete(0, tk.END)

def drag_and_drop(event):
    dropped_file = event.data.strip("{}")  # Remove curly braces
    if dropped_file.lower().endswith((".png", ".bmp")):
        image_entry.delete(0, tk.END)
        image_entry.insert(0, dropped_file)
    elif dropped_file.lower().endswith(".txt"):
        file_entry.delete(0, tk.END)
        file_entry.insert(0, dropped_file)

# ---------------------- GUI ----------------------
root = TkinterDnD.Tk()
root.title("Steganography Tool")
root.geometry("500x400")

# Image selection
tk.Label(root, text="Image:").pack()
image_entry = tk.Entry(root, width=50)
image_entry.pack()
image_entry.drop_target_register('DND_Files')
image_entry.dnd_bind('<<Drop>>', drag_and_drop)
tk.Button(root, text="Browse Image", command=select_image).pack()

# Text input
tk.Label(root, text="Text to hide:").pack()
text_entry = tk.Text(root, height=4, width=50)
text_entry.pack()

# File selection
tk.Label(root, text="OR select text file:").pack()
file_entry = tk.Entry(root, width=50)
file_entry.pack()
file_entry.drop_target_register('DND_Files')
file_entry.dnd_bind('<<Drop>>', drag_and_drop)
tk.Button(root, text="Browse File", command=select_file).pack()

# Buttons
tk.Button(root, text="Encode", command=lambda: encode_image(
    image_entry.get(), text_entry.get("1.0", tk.END).strip(), file_entry.get() if file_entry.get() else None)).pack(pady=10)

tk.Button(root, text="Decode", command=lambda: decode_image(image_entry.get())).pack(pady=10)

root.mainloop()
