"""
From output YYYYMM.png images assemble and create a timelapse video.
"""
import os
import shutil
import subprocess
import datetime
import tempfile

START_DATETIME = datetime.datetime(2011, 1, 1)

def copy_and_number(directory, ext=".png"):
    files = []
    for f in os.listdir(directory):
        if f.lower().endswith(ext):
            # ignore old entries
            date_portion, file_ext = os.path.splitext(f)
            dt = datetime.datetime.strptime(date_portion, "%Y%m")
            if dt >= START_DATETIME:
                files.append(os.path.join(directory, f))
    # assume files are named as YYYYMM.png
    with tempfile.TemporaryDirectory(prefix="numbered_imgs__") as tmpdirname:
        print("\tcreated temp directory: {}".format(tmpdirname))
        for idx, f in enumerate(sorted(files), 1):
            filename, extension = os.path.splitext(os.path.split(f)[-1])
            numbered_filename = "safecastimg__{:02}{}".format(idx, extension)
            output_filepath = os.path.join(tmpdirname, numbered_filename)
            shutil.copy(f, output_filepath)
            print("Copied ({}) to: {}".format(filename, output_filepath))
        video_filepath = create_video(tmpdirname, outputdir=directory)
        print("Created: {}".format(video_filepath))

def create_video(source_directory, outputdir, filename_format="safecastimg__%02d.png", frames_per_second=2):
    output_filename = "imgvideo.mp4"
    output_filepath = os.path.join(outputdir, output_filename)
    current_directory = os.getcwd()
    os.chdir(source_directory)
    cmd = ("avconv",
           "-r", frames_per_second,
           "-start_number", "1",
           "-i", filename_format,
           "-b:v", "1000k",
           output_filepath)
    subprocess.check_call(cmd)
    # return to working dir
    os.chdir(current_directory)
    return output_filepath


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-i", "--imagedir",
                        dest="imagedir",
                        default=None,
                        required=True,
                        help="Directory containing image files in YYYYMM.png format.")
    args = parser.parse_args()
    copy_and_number(args.imagedir)


