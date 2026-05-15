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
uvx --from git+https://github.com/dev-ansung/youtube_scrapper youtube-scrapper [COMMAND]
```

## Usage

### Get all videos from a channel

```bash
youtube-scrapper channel "https://www.youtube.com/@firebase"
```

Sample output:
```json
[
	{
		"title": "How to Use Firebase with Flutter",
		"duration": 623.0,
		"id": "AbCdEf12345",
		"url": "https://www.youtube.com/watch?v=AbCdEf12345"
	},
	{
		"title": "Firebase Studio Overview",
		"duration": 512.0,
		"id": "XyZ98765432",
		"url": "https://www.youtube.com/watch?v=XyZ98765432"
	}
]
```

### Search videos

```bash
youtube-scrapper search "firebase auth"
```

Sample output:
```json
[
	{
		"title": "Firebase Authentication in 10 Minutes",
		"duration": 601.0,
		"id": "Qwerty12345",
		"url": "https://www.youtube.com/watch?v=Qwerty12345"
	}
]
```

### Get transcript from a video

```bash
youtube-scrapper transcript "https://www.youtube.com/watch?v=7xWaijDmKDY"
```

Sample output:
```text
Welcome back.
In this video, we are going to build authentication with Firebase.
First, create your project and enable sign-in providers.
Then connect your app using the Firebase SDK.
```

### Get transcript as raw VTT

```bash
youtube-scrapper transcript --raw "https://www.youtube.com/watch?v=7xWaijDmKDY"
```

Sample output:
```text
WEBVTT

00:00:00.000 --> 00:00:02.200
Welcome back.

00:00:02.200 --> 00:00:06.000
In this video, we are going to build authentication with Firebase.
```

## License

MIT