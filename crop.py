#crops video
import os
import subprocess
from tkinter import Tk
from tkinter.filedialog import askdirectory

def get_video_size(file_path):
    """Get the size of the video file in MB."""
    return os.path.getsize(file_path) / (1024 * 1024)

def crop_video(input_file, max_size_mb=8):
    """
    Crop a video into smaller sections if its size exceeds the specified maximum size (in MB).
    Each section is saved as a separate file, and no part is deleted.
    """
    # Get the original size of the video
    original_size = get_video_size(input_file)
    print(f"Original video size: {original_size:.2f} MB")

    if original_size <= max_size_mb:
        print("Video is already under the size limit. No cropping needed.")
        return

    # Get the duration of the video
    duration = float(subprocess.check_output(
        f'ffprobe -i "{input_file}" -show_entries format=duration -v quiet -of csv="p=0"',
        shell=True
    ).decode().strip())
    print(f"Video duration: {duration:.2f} seconds")

    # Calculate the number of sections needed
    num_sections = int(original_size / max_size_mb) + 1  # Number of sections required
    section_duration = duration / num_sections  # Duration of each section

    print(f"Cropping video into {num_sections} sections, each ~{section_duration:.2f} seconds long.")

    # Create cropped sections
    for i in range(num_sections):
        start_time = i * section_duration
        output_file = f"{os.path.splitext(input_file)[0]}_part{i + 1}.mp4"

        # Use ffmpeg to crop the video into sections
        command = [
            'ffmpeg',
            '-i', input_file,               # Input file
            '-ss', str(start_time),         # Start time for cropping
            '-t', str(section_duration),    # Duration of the section
            '-c:v', 'libx264',              # Video codec
            '-c:a', 'aac',                  # Audio codec
            output_file                     # Output file
        ]

        try:
            subprocess.run(command, check=True)
            print(f"Section {i + 1} created: {output_file}")
        except subprocess.CalledProcessError as e:
            print(f"Error during cropping section {i + 1}: {e}")
            return

    print("All sections have been created successfully.")

def main():
    # Hide the root Tkinter window
    Tk().withdraw()

    # Open a dialog box to select the folder containing the video
    folder_path = askdirectory(title="Select Folder Containing Video")
    if not folder_path:
        print("No folder selected. Exiting...")
        return

    # List all files in the selected folder
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

    # Filter for video files (you can add more extensions if needed)
    video_extensions = ['.mp4', '.mkv', '.avi', '.mov']
    video_files = [f for f in files if os.path.splitext(f)[1].lower() in video_extensions]

    if not video_files:
        print("No video files found in the selected folder. Exiting...")
        return

    print(f"Found {len(video_files)} video file(s):")
    for i, video in enumerate(video_files, 1):
        print(f"{i}. {video}")

    # Ask the user to select a video file
    try:
        selection = int(input("Enter the number of the video file to process: "))
        if selection < 1 or selection > len(video_files):
            print("Invalid selection. Exiting...")
            return
    except ValueError:
        print("Invalid input. Exiting...")
        return

    selected_video = video_files[selection - 1]
    input_video = os.path.join(folder_path, selected_video)

    # Crop the selected video into sections
    crop_video(input_video, max_size_mb=8)

if __name__ == "__main__":
    main()
