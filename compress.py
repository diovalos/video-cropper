#tries to compess videos using ffmpeg
import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

def get_video_size(file_path):
    """Get the size of the video file in MB."""
    return os.path.getsize(file_path) / (1024 * 1024)

def compress_video(input_path, output_path, target_size_mb=8):
    """Compress a video to under the target size using ffmpeg."""
    # Check if the input file exists
    if not os.path.exists(input_path):
        messagebox.showerror("Error", f"The file {input_path} does not exist.")
        return

    # Get the size of the input video in MB
    input_size_mb = get_video_size(input_path)
    print(f"Input video size: {input_size_mb:.2f} MB")

    # If the video is already under the target size, no need to compress
    if input_size_mb <= target_size_mb:
        messagebox.showinfo("Info", "The video is already under the target size. No compression needed.")
        return

    # Calculate the target bitrate (in kbps) to achieve the desired file size
    # Formula: target_bitrate = (target_size_mb * 8192) / duration_in_seconds
    # First, get the duration of the video using ffprobe
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", input_path
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        duration = float(result.stdout.strip())
    except Exception as e:
        messagebox.showerror("Error", f"Error getting video duration: {e}")
        return

    target_bitrate = (target_size_mb * 8192) / duration  # 8192 kbps = 1 MB/s

    # Compress the video using ffmpeg
    try:
        subprocess.run(
            [
                "ffmpeg", "-i", input_path, "-b:v", f"{target_bitrate:.2f}k",
                "-c:v", "libx264", "-crf", "23", "-preset", "medium",
                "-c:a", "aac", "-b:a", "128k", output_path
            ],
            check=True,
        )
        print(f"Video compressed successfully: {output_path}")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Error compressing video: {e}")
        return

    # Replace the original video with the compressed video
    try:
        os.remove(input_path)  # Delete the original video
        os.rename(output_path, input_path)  # Rename the compressed video to the original name
        messagebox.showinfo("Success", f"Video compressed and replaced: {input_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Error replacing the original video: {e}")
        return

def select_folder():
    """Open a dialog box to select a folder and process videos."""
    folder_path = filedialog.askdirectory(title="Select Folder Containing Video")
    if not folder_path:
        messagebox.showwarning("Warning", "No folder selected. Exiting.")
        return

    # Find video files in the selected folder
    video_files = [f for f in os.listdir(folder_path) if f.endswith((".mp4", ".mkv", ".avi", ".mov"))]
    if not video_files:
        messagebox.showinfo("Info", "No video files found in the selected folder.")
        return

    # Process each video file
    for video_file in video_files:
        input_path = os.path.join(folder_path, video_file)
        temp_output_path = os.path.join(folder_path, f"temp_compressed_{video_file}")
        compress_video(input_path, temp_output_path)

if __name__ == "__main__":
    # Create a GUI window
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    # Open the folder selection dialog
    select_folder()

    # Close the GUI
    root.destroy()
