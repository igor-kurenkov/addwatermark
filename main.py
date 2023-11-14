import os
import time
import logging
import subprocess
import shutil

os.environ["IMAGEMAGICK_BINARY"] = "C:\\Program Files\\ImageMagick-7.1.1-Q16-HDRI\\magick.exe"

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Specify the directory to watch
watchfolder = "C:\\Users\\Lee\\Pictures\\_Neuronaut_video_addwatermark"

# Specify the output directory
outfolder = "C:\\Users\\Lee\\Pictures\\_Neuronaut_video_watermarked"

# Specify the watermark image path
watermark_image_path = "C:\\Users\\Lee\\Pictures\\_LOGO\\watermark.png"

# Specify the scale for the watermark
watermark_scale = 0.3  # 10% of the lowest video dimension

# Specify the watermark transparency
watermark_transparency = 0.4

def add_watermark(watchfolder, filename, watermark_transparency):
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

        # Create the watermark image
        watermark_image = watermark_image_path
        # subprocess.run(["magick", "-size", "320x240", "-pointsize", str(watermark_font_size),
        #                 "-gravity", "center", f"-annotate", "+0+0", watermark_text, watermark_image])

        # Add the watermark to the video
        out_video_path = os.path.join(outfolder, filename)
        out_video_path = out_video_path.split('.')[0] + "_watermarked.mp4"
        subprocess.run(["ffmpeg", "-i", video_path, "-i", watermark_image,
                        "-filter_complex", f"[1:v]scale=iw*{watermark_scale}:ih*{watermark_scale},colorchannelmixer=aa={watermark_transparency}[logo];[0:v][logo]overlay=W-w-300:H-h-50:format=auto[out]",
                        "-map", "[out]", "-map", "0:a?", "-c:v", "libx264", "-c:a", "copy", out_video_path])
        try:
            # Check if the file exists
            if not os.path.isfile(out_video_path):
                logging.debug(f"File {out_video_path} does not exist.")
                return

        except Exception as e:
            logging.error(f"file doesn\'t exist: {0}: {str(e)}".format(out_video_path))

        print('video done. ' + out_video_path)

        # Move the original video file to the output folder
        shutil.move(video_path, outfolder)

    except Exception as e:
        logging.error(f"An error occurred while adding watermark to {video_path}: {str(e)}")

# Watch the directory for new video files
while True:
    for filename in os.listdir(watchfolder):
        if filename.endswith(".mp4") or filename.endswith(".avi"):  # Add more video formats if needed
            video_path = os.path.join(watchfolder, filename)
            add_watermark(watchfolder, filename, watermark_transparency)

    # Wait for a while before checking for new files again
    time.sleep(30)

# ffmpeg command fpr CLI
# ffmpeg -i 2.mp4 -i watermark.png -filter_complex "[1:v]scale=iw*0.4:ih*0.4,colorchannelmixer=aa=0.5[logo];[0:v][logo]overlay=W-w-50:H-h-50:format=auto[out]" -map "[out]" -map "0:a?" -c:v "libx264" -c:a "copy" 3.mp4