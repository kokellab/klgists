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


__all__ = ['gen_video']
