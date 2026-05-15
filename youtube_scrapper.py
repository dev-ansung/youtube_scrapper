import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import sys
import tempfile
from typing import Any, cast

import webvtt
import yt_dlp


@dataclass
class VideoInfo:
    data: dict[str, Any]

    @classmethod
    def from_video(cls, video: dict[str, Any]) -> 'VideoInfo':
        return cls(data=dict(video))

    def to_dict(self) -> dict[str, Any]:
        return dict(self.data)
    
    @staticmethod
    def get_essential_fields() -> list[str]:
        return ['title', 'duration', 'id', 'url']

    def _normalized_url(self) -> Any:
        direct_url = self.data.get('url')
        if isinstance(direct_url, str) and direct_url.startswith(('http://', 'https://')):
            return direct_url

        webpage_url = self.data.get('webpage_url')
        if isinstance(webpage_url, str) and webpage_url.startswith(('http://', 'https://')):
            return webpage_url

        video_id = self.data.get('id')
        if isinstance(video_id, str) and video_id:
            return f'https://www.youtube.com/watch?v={video_id}'

        return direct_url

    def to_compact_dict(self) -> dict[str, Any]:
        compact = {field: self.data.get(field) for field in self.get_essential_fields()}
        compact['url'] = self._normalized_url()
        return compact


@dataclass
class TranscriptResult:
    video_target: str
    text: str

    def to_text(self) -> str:
        return self.text


class YoutubeScrapper:
    def __init__(self, verbose=False):
        self.verbose = verbose

    def _apply_verbosity(self, options):
        if not self.verbose:
            options['no_warnings'] = True
            options['quiet'] = True
        return options

    @staticmethod
    def normalize_channel_target(channel_target):
        if channel_target.startswith(('http://', 'https://')):
            return channel_target

        handle = channel_target.lstrip('@')
        return f'https://www.youtube.com/@{handle}/videos'

    @staticmethod
    def normalize_video_target(video_target):
        if video_target.startswith(('http://', 'https://')):
            return video_target

        return f'https://www.youtube.com/watch?v={video_target}'

    @staticmethod
    def _clean_vtt_text(subtitle_file):
        cleaned_lines: list[str] = []
        previous_line = None

        for caption in webvtt.read(str(subtitle_file)):
            for raw_line in caption.text.splitlines():
                line = raw_line.strip()

                if not line:
                    continue

                # Deduplicate only adjacent overlap from caption boundaries.
                if line == previous_line:
                    continue

                cleaned_lines.append(line)
                previous_line = line

        return '\n'.join(cleaned_lines)

    @staticmethod
    def _pick_subtitle_file(directory):
        subtitle_files = sorted(Path(directory).glob('*.vtt'))
        if not subtitle_files:
            raise RuntimeError('No subtitles were downloaded for this video.')

        def subtitle_priority(path):
            name = path.name.lower()
            return (
                0 if '.en.' in name else 1,
                0 if '.orig.' not in name else 1,
                name,
            )

        return sorted(subtitle_files, key=subtitle_priority)[0]

    @staticmethod
    def _videos_from_result(result):
        videos: list[VideoInfo] = []
        entries = result.get('entries')

        if isinstance(entries, list):
            for video in entries:
                if isinstance(video, dict):
                    videos.append(VideoInfo.from_video(cast(dict[str, Any], video)))

        return videos

    def get_channel_videos(self, channel_target, limit=20):
        channel_url = self.normalize_channel_target(channel_target)

        # Configure options to only extract info without downloading.
        ydl_opts: dict[str, Any] = self._apply_verbosity({
            'extract_flat': True,
            'force_generic_extractor': False,
        })

        if limit is not None:
            if limit < 1:
                raise ValueError('limit must be greater than 0')
            ydl_opts['playlistend'] = limit

        with yt_dlp.YoutubeDL(cast(Any, ydl_opts)) as ydl:
            result = cast(dict[str, Any], ydl.extract_info(channel_url, download=False))

        return self._videos_from_result(result)

    def search_videos(self, search_query, limit=20):
        query = f'ytsearch{limit}:{search_query}'

        ydl_opts: dict[str, Any] = self._apply_verbosity({
            'extract_flat': True,
            'force_generic_extractor': False,
        })

        with yt_dlp.YoutubeDL(cast(Any, ydl_opts)) as ydl:
            result = cast(dict[str, Any], ydl.extract_info(query, download=False))

        return self._videos_from_result(result)

    def get_transcript(self, video_target, raw=False):
        normalized_target = self.normalize_video_target(video_target)

        ydl_opts: dict[str, Any] = self._apply_verbosity({
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitlesformat': 'vtt',
        })

        with tempfile.TemporaryDirectory() as temp_dir:
            ydl_opts['outtmpl'] = str(Path(temp_dir) / '%(id)s.%(ext)s')

            with yt_dlp.YoutubeDL(cast(Any, ydl_opts)) as ydl:
                ydl.download([normalized_target])

            subtitle_file = self._pick_subtitle_file(temp_dir)

            if raw:
                transcript_text = subtitle_file.read_text(encoding='utf-8')
            else:
                transcript_text = self._clean_vtt_text(subtitle_file)

        if not transcript_text:
            raise RuntimeError('Subtitle file was downloaded, but no transcript text could be extracted.')

        return TranscriptResult(video_target=normalized_target, text=transcript_text)


def build_parser():
    parser = argparse.ArgumentParser(
        prog='youtube-scrapper',
        description='Extract YouTube channel videos as JSON.',
    )
    subparsers = parser.add_subparsers(dest='command', required=True)
    parser.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        help='Show yt-dlp extraction output.',
    )

    channel_parser = subparsers.add_parser(
        'channel',
        help='List videos from a YouTube channel as JSON.',
    )
    channel_parser.add_argument(
        'channel_target',
        help='YouTube channel URL or handle.',
    )
    channel_parser.add_argument(
        '--limit',
        type=int,
        default=20,
        help='Limit the number of channel videos returned.',
    )
    channel_parser.add_argument(
        '--raw',
        action='store_true',
        help='Print full JSON entries payload instead of compact JSON output.'
             f'Default fields in compact output: {", ".join(VideoInfo.get_essential_fields())}.',
    )

    transcript_parser = subparsers.add_parser(
        'transcript',
        help='Print a video transcript as plain text.',
    )
    transcript_parser.add_argument(
        'video_target',
        help='YouTube video URL or video id.',
    )
    transcript_parser.add_argument(
        '--raw',
        action='store_true',
        help='Print raw VTT subtitle content instead of cleaned transcript text.',
    )

    search_parser = subparsers.add_parser(
        'search',
        help='Search YouTube videos by query and return results as JSON.',
    )
    search_parser.add_argument(
        'search_query',
        nargs='+',
        help='Search query text.',
    )
    search_parser.add_argument(
        '--raw',
        action='store_true',
        help='Print full JSON entries payload instead of compact JSON output.',
    )

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    scrapper = YoutubeScrapper(verbose=args.verbose)

    if args.command == 'channel':
        try:
            videos = scrapper.get_channel_videos(args.channel_target, limit=args.limit)

            if args.raw:
                print(json.dumps([video.to_dict() for video in videos], ensure_ascii=False, indent=2))
            else:
                print(json.dumps([video.to_compact_dict() for video in videos], ensure_ascii=False, indent=2))

            return 0
        except Exception as exc:
            print(f'Error: {exc}', file=sys.stderr)
            return 1

    if args.command == 'transcript':
        try:
            transcript = scrapper.get_transcript(args.video_target, raw=args.raw)
            print(transcript.to_text())
            return 0
        except Exception as exc:
            print(f'Error: {exc}', file=sys.stderr)
            return 1

    if args.command == 'search':
        try:
            query = ' '.join(args.search_query).strip()
            videos = scrapper.search_videos(query)

            if args.raw:
                print(json.dumps([video.to_dict() for video in videos], ensure_ascii=False, indent=2))
            else:
                print(json.dumps([video.to_compact_dict() for video in videos], ensure_ascii=False, indent=2))

            return 0
        except Exception as exc:
            print(f'Error: {exc}', file=sys.stderr)
            return 1

    parser.error('Unknown command')
    return 1

if __name__ == "__main__":
    raise SystemExit(main())