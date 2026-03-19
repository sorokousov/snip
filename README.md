# snip

`snip` is a small Python CLI for storing named shell command snippets and running them later by name or by the current list index.

## Features

- add snippets without external dependencies
- list snippets with stable 1-based indices
- show, run, remove, and rename snippets by name or `!index`
- store data as JSON in an XDG-compatible config location
- execute commands via `bash -lc`

## Requirements

- Python 3.10+
- standard library only

## Installation

### Run as a standalone command

To make `snip` available directly in your shell, install the project so the console script is created:

```bash
python -m pip install --user .
```

After that you can run commands like:

```bash
snip list
snip add build docker compose up --build
snip run build
```

If your shell still cannot find `snip`, make sure your user scripts directory is in `PATH` (for example `~/.local/bin` on many Linux systems).

### Development install

For local development you can also use an editable install:

```bash
python -m pip install --user -e .
```

## Storage location

`snip` stores snippets in JSON at one of these paths:

- `$XDG_CONFIG_HOME/snip/snippets.json`, when `XDG_CONFIG_HOME` is set
- `~/.config/snip/snippets.json`, otherwise

The directory and file are created automatically when needed.

## Usage

### Add a snippet

```bash
snip add devserver python manage.py runserver
snip add build docker compose up --build
```

### List snippets

```bash
snip list
```

Example output:

```text
1. devserver: python manage.py runserver
2. build: docker compose up --build
```

### Show a snippet

```bash
snip show devserver
snip show !1
```

### Run a snippet

```bash
snip run build
snip run !2
```

### Remove a snippet

```bash
snip remove devserver
snip remove !1
```

### Rename a snippet

```bash
snip rename build images
snip rename !1 localserver
```

## Development

Run the test suite with:

```bash
python -m unittest discover -s tests -v
```
