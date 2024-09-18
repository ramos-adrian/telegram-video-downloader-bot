import re
from uuid import uuid4

from yt_dlp import YoutubeDL


def is_video_url(url):
    pattern = re.compile(
        r'(https?://)?(www\.)?(fb\.watch|youtube\.com|youtu\.?be|facebook\.com|twitter\.com|x\.com|instagram\.com|reddit\.com)/.+')
    return bool(pattern.match(url))


def get_video_info(url):
    with YoutubeDL() as ydl:
        info = ydl.extract_info(url, download=False)
        sanitized_info = ydl.sanitize_info(info)
        return sanitized_info


def get_file_size(sanitized_info):
    if 'filesize_approx' in sanitized_info:
        file_size = sanitized_info['filesize_approx']
        if file_size is None:
            raise Exception('File size not found')
        return file_size
    else:
        raise Exception('File size not found')


def get_duration(sanitized_info):
    if 'duration' in sanitized_info:
        duration = sanitized_info['duration']
        if duration is None:
            raise Exception('Duration not found')
        return duration
    else:
        raise Exception('Duration not found')


def download(url):
    uuid = str(uuid4())

    ydl_opts = {
        'outtmpl': f'/tmp/{uuid}.mp4',
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return uuid
