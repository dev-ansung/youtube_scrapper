# YouTube Scrapper

A simple command-line tool to scrape YouTube video information and transcripts using `yt-dlp`.

## Requirements

- Python 3.14+
- [uv](https://github.com/astral-sh/uv)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)

## Setup

### Installation (Recommended)

```bash
uv tool install git+https://github.com/dev-ansung/youtube_scrapper
```

### Single Use (No Installation)

```bash
uvx --from git+https://github.com/dev-ansung/youtube_scrapper youtube-scrapper channel <channel_url_or_handle>
```

```bash
uvx --from git+https://github.com/dev-ansung/youtube_scrapper youtube-scrapper transcript <video_url_or_id>
```

```bash
uvx --from git+https://github.com/dev-ansung/youtube_scrapper youtube-scrapper search <search_query>
```

## Usage

### uv run youtube-scrapper --help

```bash
usage: youtube-scrapper [-h] [-v] {channel,transcript,search} ...

Extract YouTube channel videos as JSON.

positional arguments:
  {channel,transcript,search}
    channel             List videos from a YouTube channel as JSON.
    transcript          Print a video transcript as plain text.
    search              Search YouTube videos by query and return results as
                        JSON.

options:
  -h, --help            show this help message and exit
  -v, --verbose         Show yt-dlp extraction output.

```

### uv run youtube-scrapper channel --help

```text
usage: youtube-scrapper channel [-h] [--limit LIMIT] [--raw] channel_target

positional arguments:
  channel_target  YouTube channel URL or handle.

options:
  -h, --help      show this help message and exit
  --limit LIMIT   Limit the number of channel videos returned.
  --raw           Print full JSON entries payload instead of compact JSON
                  output.Default fields in compact output: title, duration,
                  id, url.

```

### uv run youtube-scrapper search --help

```bash
usage: youtube-scrapper search [-h] [--raw] search_query [search_query ...]

positional arguments:
  search_query  Search query text.

options:
  -h, --help    show this help message and exit
  --raw         Print full JSON entries payload instead of compact JSON
                output.

```

### uv run youtube-scrapper transcript --help

```bash
usage: youtube-scrapper transcript [-h] [--raw] video_target

positional arguments:
  video_target  YouTube video URL or video id.

options:
  -h, --help    show this help message and exit
  --raw         Print raw VTT subtitle content instead of cleaned transcript
                text.

```

## License

MIT
