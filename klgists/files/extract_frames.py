import logging
import warnings
from os.path import dirname
from typing import Optional
from klgists.common import pjoin, pexists
from klgists.files.wrap_cmd_call import wrap_cmd_call


def extract_frames(video_path: str, output_frames_dir: str, notification_path: Optional[str]=None, quality: int=0) -> None:
	"""Use ffmpeg to read a video file and extract the frames.
	Requires 'ffmpeg' to be on the command line.
	The resulting JPEG frames will be named in the format '%06d.jpg'.
	Uses notification_path to indicate whether the extraction completed;
	this will be named video_path'/.finished-extraction' if None.
	Will warn and write over the output dir if it exists but no file at notification_path exists.
	Quality must be between 0 and 31, where 0 is the highest.
	"""
	if notification_path is None: notification_path = pjoin(dirname(video_path), ".finished-extraction")

	if pexists(notification_path) and pexists(output_frames_dir):
		logging.info("Frames directory {} is already complete; skipping.".format(output_frames_dir))
	else:

		if pexists(output_frames_dir):
			warnings.warn("Frames directory {} already exists but is incomplete. Extracting frames...".format(output_frames_dir))
		else:
			logging.info("Extracting frames into {}".format(output_frames_dir))

		if not pexists(video_path):
			raise ValueError('Cannot extract frames: video.avi does not exist')

		wrap_cmd_call([
				'ffmpeg',
				'-i', video_path,
				'-q:v', quality,
				pjoin(output_frames_dir, '%06d.jpg')
		])
		with open(notification_path, 'w'): print('')  # all done
