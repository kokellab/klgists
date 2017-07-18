import os
from klgists.common import pjoin
from subprocess import Popen

def make_video_from_frames(input_dir: str, video_path: str, framerate: str='10/1', ffmpeg_path: str='ffmpeg', input_image_extension: str='.jpg') -> None:
	"""Runs ffmpeg on all selected files in a directory to generates an x264-encoded video in an MP4 container.
	Warnings:
		- Make sure that the frames are sorted in the correct order.
		- Overwrites the output video file without warning.
	video_path: the full path of the video file, which MUST end in .mp4
	framerate: a rational number in the format a/b (ex: 4/5 is 4 frames per every 5 seconds)
	input_image_extension: The extension of the images in the directory to use as input; must start with a dot (.)
	"""
	assert input_image_extension.startswith('.'), "Extension should start with '.'"
	assert video_path.endswith('.mp4'), "Video file path should end with 'mp4'"
	Popen([ffmpeg_path,
			'-r', framerate,
			'-y',                                                        # overwrites
			'-pattern_type', 'glob',
			'-i', pjoin(input_dir, '*' + input_image_extension),
			'-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2',                  # needed because: https://stackoverflow.com/questions/24961127/ffmpeg-create-video-from-images
			'-c:v', 'libx264',
			'-pix_fmt', 'yuv420p',                                       # needed because most video players can only use the 264 pixel format, but it's not default
			video_path])


