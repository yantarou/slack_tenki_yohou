# Slack チャンネル 天気予報

This Slack bot sends a channel summary to a specified channel.

## Prerequisites

The project has been developed and tested with Python v3.8.2.

The easiest way to get an adequate Python environment installed is to use `pyenv`:

* https://github.com/pyenv/pyenv
* https://github.com/pyenv/pyenv-installer

The to-be-used version by `pyenv` is tracked in the `.python-version` file.

Once `pyenv` is installed, use the following command to install the needed Python version:

```sh
$ pyenv install 3.8.2
```

Afterwards, install the necessary project dependencies with `pip`:

```sh
$ pip install -r requirements.txt
```

## How to run

Set the bot token via the `SLACK_BOT_TOKEN` environment variable and execute the script with
the command line parameter `--target_channel_id` with the ID of the channel to send the message to.

```sh
$ SLACK_BOT_TOKEN="xoxb-123456789012-123456789012-123456789012345678901234" \
  python slack_post_channel_summary.py --target_channel_id C12345678"
```
