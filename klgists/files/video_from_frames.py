import numpy as np
import logging
import tempfile
import shlex
from typing import Optional

from klgists.common import pjoin
from klgists.files.wrap_cmd_call import wrap_cmd_call


def gen_video(
		video_path: str,
		input_frames_dir: str,
		video_frame_rate: str,
		input_image_extension: str='.jpg',
		encoding: str='libx265',
		crf: int=0
) -> None:
	"""Use ffmpeg to read generate a video from frames.
	Requires 'ffmpeg' to be on the command line.
	The resulting JPEG frames will be named in the format '%06d.jpg'.
	"""
	input_format_str = pjoin(input_frames_dir, "%06d{}".format(input_image_extension))
	wrap_cmd_call([
		'ffmpeg',
		'-f', 'concat',                               # I don't remember why!
		'-r', video_frame_rate,                       # we don't know this because we just have frames
		'-safe','0',                                  # just allow any filename
		'-i', input_format_str,
		'-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2',   # compatibility with some players, including QuickTime
		'-c:v', encoding,
		'-crf', crf,
		'-pix_fmt', 'yuv420p',
		'-y', video_path
	])


def video_from_frames(video_path: str, input_frames_dir: str,
					  video_chunk_dict: Optional[dict] = None, video_frame_rate: Optional[float] = None,
					  input_image_extension: str = '.jpg', video_file_extension: str = '.mkv',
					  encoding: str = 'libx264', crf: Optional[int] = None) -> None:
	"""
	To generate multiple named videos, set video_path as a target directory and supply a dictionary of the form {video_name: (start_ms, end_ms)} as well as the frame rate.
	DEPRECATED: Use gen_video instead.
	"""

	logging.info("Extracting frames from {}".format(input_frames_dir))

	if ((video_chunk_dict is not None) and (video_frame_rate is not None)):
		video_path = {pjoin(video_path, x): (int(np.ceil((video_chunk_dict[x][0] / 1000) * video_frame_rate)),
											 int(np.floor((video_chunk_dict[x][1] / 1000) * video_frame_rate))) for x in
					  video_chunk_dict.keys()}
		for x in video_path:
			with tempfile.NamedTemporaryFile(mode='w') as fp:
				for n in range(video_path[x][0], video_path[x][1]):
					fname = "%06d" % n
					full = pjoin(input_frames_dir, "%s%s" % (fname, input_image_extension))
					fp.write('file %s\n' % full)
				ffmpeg = shlex.split(
					"ffmpeg -f concat -r %s -safe 0 -i %s -vf scale=trunc(iw/2)*2:trunc(ih/2)*2 -c:v %s %s -pix_fmt yuv420p -y %s%s" % (
					video_frame_rate, fp.name, encoding, ("-crf %s" % crf) if crf is not None else '', x,
					video_file_extension))
				wrap_cmd_call(ffmpeg)
	else:
		ffmpeg = shlex.split(
			"ffmpeg -f concat -r %s -safe 0 -i %s -vf scale=trunc(iw/2)*2:trunc(ih/2)*2 -c:v %s %s -pix_fmt yuv420p -y %s%s" % (
			video_frame_rate, pjoin(input_frames_dir, '%06d%s' % input_image_extension), encoding,
			("-crf %s" % crf) if crf is not None else '', x, video_file_extension))
		wrap_cmd_call(ffmpeg)
