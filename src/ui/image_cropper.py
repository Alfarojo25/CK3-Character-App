"""
Image Cropper Dialog
Modal dialog for cropping/repositioning images with zoom selection.
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk


class ImageCropper(tk.Toplevel):
    """Modal dialog for cropping/repositioning images with zoom selection."""
    
    def __init__(self, parent, image_path: str):
        """
        Initialize the image cropper dialog.
        
        Args:
            parent: Parent window
            image_path: Path to the image to crop
        """
        super().__init__(parent)
        self.title("Adjust Image Position")
        self.geometry("700x800")
        self.configure(bg="#2e2e2e")
        self.transient(parent)
        self.grab_set()

        self.result = None
        self.image_path = image_path

        # Load original image
        self.original = Image.open(image_path)
        self.display_size = 600
        self.crop_size = 300

        # Scale image
        self.scale_factor = min(
            self.display_size / self.original.width,
            self.display_size / self.original.height
        )

        # Canvas for image
        self.canvas = tk.Canvas(
            self, width=self.display_size, height=self.display_size,
            bg="#1e1e1e", highlightthickness=2, highlightbackground="#666666"
        )
        self.canvas.pack(pady=10)

        # Initial display
        self._update_display_image()

        # Crop rectangle
        cx = self.display_size // 2
        cy = self.display_size // 2
        self.crop_rect = self.canvas.create_rectangle(
            cx - self.crop_size//2, cy - self.crop_size//2,
            cx + self.crop_size//2, cy + self.crop_size//2,
            outline="red", width=3
        )

        # Instructions
        ttk.Label(
            self, 
            text="Drag the image to reposition, scroll to zoom. Red box shows visible area.",
            background="#2e2e2e", 
            foreground="#dddddd"
        ).pack()

        # Buttons
        btn_frame = tk.Frame(self, bg="#2e2e2e")
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="OK", command=self.ok, width=10).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.cancel, width=10).pack(side="left", padx=5)

        # Bind events
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<MouseWheel>", self.on_zoom)       # Windows/macOS
        self.canvas.bind("<Button-4>", self.on_zoom)         # Linux scroll up
        self.canvas.bind("<Button-5>", self.on_zoom)         # Linux scroll down

        self.drag_start_x = 0
        self.drag_start_y = 0

    def _update_display_image(self):
        """Update the displayed image based on scale factor."""
        disp_w = int(self.original.width * self.scale_factor)
        disp_h = int(self.original.height * self.scale_factor)
        self.display_image = self.original.resize((disp_w, disp_h), Image.Resampling.LANCZOS)
        self.photo = ImageTk.PhotoImage(self.display_image)
        if hasattr(self, 'image_id'):
            self.canvas.delete(self.image_id)
        x = self.display_size // 2
        y = self.display_size // 2
        self.image_id = self.canvas.create_image(x, y, image=self.photo)
        if hasattr(self, 'crop_rect'):
            self.canvas.tag_raise(self.crop_rect)

    def on_press(self, event):
        """Handle mouse press event."""
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def on_drag(self, event):
        """Handle mouse drag event."""
        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y
        self.canvas.move(self.image_id, dx, dy)
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def on_zoom(self, event):
        """Handle mouse scroll zoom event."""
        factor = 1.1 if getattr(event, 'delta', 0) > 0 or getattr(event, 'num', None) == 4 else 0.9
        self.scale_factor *= factor
        
        # Clamp scale_factor
        min_scale = max(
            self.display_size / self.original.width,
            self.display_size / self.original.height
        ) * 0.1
        max_scale = 10.0
        self.scale_factor = max(min_scale, min(self.scale_factor, max_scale))
        
        # Redraw image centered at current canvas coords
        coords = self.canvas.coords(self.image_id)
        self._update_display_image()
        self.canvas.coords(self.image_id, coords)

    def ok(self):
        """Process the crop and close dialog."""
        coords = self.canvas.coords(self.image_id)
        img_x, img_y = coords[0], coords[1]

        # Crop box center
        crop_cx = self.display_size // 2
        crop_cy = self.display_size // 2

        # Calculate offset from image center to crop center
        offset_x = (crop_cx - img_x) / self.scale_factor
        offset_y = (crop_cy - img_y) / self.scale_factor

        # Original crop size
        orig_crop_size = self.crop_size / self.scale_factor

        # Calculate crop box in original image coordinates
        orig_cx = self.original.width / 2 + offset_x
        orig_cy = self.original.height / 2 + offset_y

        left = max(0, orig_cx - orig_crop_size / 2)
        top = max(0, orig_cy - orig_crop_size / 2)
        right = min(self.original.width, orig_cx + orig_crop_size / 2)
        bottom = min(self.original.height, orig_cy + orig_crop_size / 2)

        self.result = (int(left), int(top), int(right), int(bottom))
        self.destroy()

    def cancel(self):
        """Cancel and close dialog."""
        self.result = None
        self.destroy()
