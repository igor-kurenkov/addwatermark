import os
import time
import logging
import subprocess
import shutil
import ffmpeg
from moviepy.editor import *

os.environ["IMAGEMAGICK_BINARY"] = "C:\\Program Files\\ImageMagick-7.1.1-Q16-HDRI\\magick.exe"

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Specify the directory to watch
watchfolder = "C:\\Users\\Lee\\Pictures\\_Neuronaut_video_addwatermark"

# Specify the dummy audio path
dummy_audio = "C:\\Users\\Lee\\Pictures\\watermark_bot_files\\_Neuronaut_video_watermarked\\dummy_audio.mp3"

# Specify the output directory
outfolder = "C:\\Users\\Lee\\Pictures\\_Neuronaut_video_watermarked"

# Specify the watermark image path
watermark_image_path = "C:\\Users\\Lee\\Pictures\\_LOGO\\watermark.png"

# Specify the ending image path
ending_image_path = "C:\\Users\\Lee\\Pictures\\_LOGO\\neuronaut.png"

# Specify the ending image duration
ending_length = 3

# Specify the scale for the watermark
watermark_scale = 0.3  # 10% of the lowest video dimension

# Specify the watermark transparency
watermark_transparency = 0.4


def convert_gif_to_mp4(gif_path, mp4_path):
    subprocess.run(["ffmpeg", "-i", gif_path, "-movflags", "faststart", "-pix_fmt", "yuv420p", "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2", mp4_path])

def concatenate_videos(out_video_path, ending_video_path, final_video_path):
    # Load the videos
    video1 = VideoFileClip(out_video_path)
    video2 = VideoFileClip(ending_video_path)

    # Determine the lowest dimension of video1
    new_size = min(video1.w, video1.h)

    # Resize the ending
    video2 = video2.resize((new_size, new_size))

    # Check if the first video has audio
    if video1.audio is not None:
        # If the first video has audio, use it in the concatenation
        audio1 = video1.audio
        audio2 = AudioFileClip(ending_video_path)
        final_audio = CompositeAudioClip([audio1, audio2])
    else:
        # If the first video does not have audio, use a silent audio clip
        final_audio = AudioFileClip(dummy_audio)

    # Concatenate the videos
    final_video = concatenate_videoclips([video1, video2])

    # Set the final audio
    final_video.audio = final_audio

    # Write the final video to a file
    final_video.write_videofile(final_video_path)

def add_watermark(watchfolder, filename, watermark_transparency, ending_image_path, ending_length):

    video_path = os.path.join(watchfolder, filename)
    try:
        # Check if the file exists
        if not os.path.isfile(video_path):
            logging.debug(f"File {video_path} does not exist.")
            return

        # Check if the file is open
        try:
            with open(video_path, 'r') as f:
                pass
        except IOError:
            logging.debug(f"File {video_path} is open.")
            return

        # If the file is a GIF, convert it to MP4
        if filename.endswith(".gif"):
            mp4_path = video_path.split('.')[0] + ".mp4"
            convert_gif_to_mp4(video_path, mp4_path)
            shutil.move(video_path, outfolder)
            video_path = mp4_path

        # Create the watermark image
        watermark_image = watermark_image_path

        # Add the watermark to the video
        out_video_path = os.path.join(outfolder, filename)
        out_video_path = out_video_path.split('.')[0] + "_watermarked.mp4"
        subprocess.run(["ffmpeg", "-i", video_path, "-i", watermark_image,
                        "-filter_complex",
                        f"[1:v]scale=iw*{watermark_scale}:ih*{watermark_scale},colorchannelmixer=aa={watermark_transparency}[logo];[0:v][logo]overlay=W-w-150:H-h-150:format=auto[out]",
                        "-map", "[out]", "-map", "0:a?", "-c:v", "libx264", "-profile:v", "high", "-level", "4.0",
                        "-pix_fmt", "yuv420p", "-c:a", "copy", out_video_path])
        try:
            # Check if the file exists
            if not os.path.isfile(out_video_path):
                logging.debug(f"File {out_video_path} does not exist.")
                return

        except Exception as e:
            logging.error(f"file doesn\'t exist: {0}: {str(e)}".format(out_video_path))

        # Get the dimensions of the output video
        probe = ffmpeg.probe(out_video_path)
        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        width = int(video_stream['width'])
        height = int(video_stream['height'])

        # # Create a video from the ending image
        ending_video_path = "C:\\Users\\Lee\\Pictures\\watermark_bot_files\\ending.mp4"
        # subprocess.run(
        #     ["ffmpeg", "-loop", "1", "-i", ending_image_path, "-f", "lavfi", "-i", "anullsrc", "-c:v", "libx264", "-t",
        #      str(ending_length), "-pix_fmt",
        #      "yuv420p", "-vf", f"scale={width}:{height}", "-c:a", "aac", "-shortest", ending_video_path])

        # Concatenate the watermarked video and the ending video
        final_video_path = out_video_path.split('.')[0] + "_final.mp4"
        # concatenate_videos(out_video_path, ending_video_path, final_video_path)

        print('video done. ' + final_video_path)

        # Move the original video file to the output folder
        shutil.move(video_path, outfolder)

        # # delete ending.mp4
        # if os.path.isfile(ending_video_path):
        #     os.remove(ending_video_path)
        # else:
        #     print(f"Error: {file_path} not a valid filename")

    except Exception as e:
        logging.error(f"An error occurred while adding watermark to {video_path}: {str(e)}")

# Watch the directory for new video files
while True:
    for filename in os.listdir(watchfolder):
        if filename.endswith(".mp4") or filename.endswith(".MP4") or filename.endswith(".avi") or filename.endswith(".gif"):  # Add more video formats if needed
            video_path = os.path.join(watchfolder, filename)
            add_watermark(watchfolder, filename, watermark_transparency, ending_image_path, ending_length)

    # Wait for a while before checking for new files again
    time.sleep(30)