#!/usr/bin/env python
# coding: utf-8

# Python imports
import argparse
import datetime
import logging
import os
import sys

# External library imports
import jinja2
import pytz
import slack

# Local project imports
from channel_info import ChannelInfo

#
# Used Slack API methods:
# https://api.slack.com/methods/chat.postMessage
# https://api.slack.com/methods/conversations.history
#
# Necessary bot scopes:
# https://api.slack.com/scopes/chat:write
# https://api.slack.com/scopes/channels:history
#


def main(argv):
    # Parse command line
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--target_channel_id", dest="target_channel_id", required=True, help="channel to post the message to"
    )
    parser.add_argument("--time_zone", dest="time_zone", default="Asia/Tokyo", help="time zone")
    parser.add_argument("-q", "--quiet", action="store_true", help="only log errors")
    parser.add_argument("-v", "--verbose", action="store_true", help="increase output verbosity")
    args = parser.parse_args()

    # Create a logger
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')
    logger = logging.getLogger(__name__)
    if args.quiet:
        logger.setLevel(logging.ERROR)
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Create Slack web client
    try:
        slack_client = slack.WebClient(token=os.environ['SLACK_BOT_TOKEN'])
    except KeyError:
        logger.error("Failed to initialize the Slack client.")
        logger.error("Has the SLACK_BOT_TOKEN environment variable been set?")
        raise

    # List of processed Slack channels
    channel_list = list()

    try:
        # Get all public Slack channels
        conversations_list_req = slack_client.conversations_list()
        channels = conversations_list_req['channels']

        # Process all channels
        for channel in channels:
            logger.debug("Processing channel: '%s'" % channel)

            # Skip archived channels
            if channel['is_archived']:
                logger.debug("Skipping archived channel: '%s'" % channel)
                continue

            # Determine last update
            last_update = None

            # Get last 10 messages
            try:
                conversations_history_req = slack_client.conversations_history(
                    channel=channel['id'],
                    inclusive=1,
                    limit=10
                )
                messages = conversations_history_req['messages']

                for message in messages:
                    logger.debug("Checking message: %s" % message)

                    # Skip message with "subtype"
                    if 'subtype' in message:
                        continue

                    # Get message timestamp
                    last_update = datetime.datetime.fromtimestamp(
                        float(message['ts']),
                        tz=pytz.timezone(args.time_zone)
                    )
                    logger.debug("Last update: %s" % last_update)
                    break
            except slack.errors.SlackApiError as e:
                assert e.response["ok"] is False
                assert e.response["error"]
                logger.error(
                    "Failed to process conversation history for channel '%s': %s" %
                    (channel['name'], e.response['error'])
                )

            # Append channel to list
            logger.info("Appending channel to list: %s" % channel)
            channel_info = ChannelInfo(channel, last_update, args.time_zone)
            channel_list.append(channel_info)

    except slack.errors.SlackApiError as e:
        assert e.response["ok"] is False
        assert e.response["error"]
        logger.error(f"Failed to process channel list: {e.response['error']}")
        raise

    # Sort the channel list alphabetically by name
    channel_list.sort(key=lambda x: x.name)

    # Load and render the Jinja template
    jinja_loader = jinja2.FileSystemLoader(".")
    jinja_env = jinja2.Environment(loader=jinja_loader)
    jinja_template = jinja_env.get_template("message_template.jinja")
    jinja_rendered_template = jinja_template.render(channels=channel_list)
    logger.debug("Jinja rendered template:")
    logger.debug("-----")
    logger.debug(jinja_rendered_template)
    logger.debug("-----")

    # Post message to target channel
    try:
        slack_client.chat_postMessage(
            channel=args.target_channel_id,
            text="チャンネル 天気予報",
            blocks=jinja_rendered_template
        )
    except slack.errors.SlackApiError as e:
        assert e.response["ok"] is False
        assert e.response["error"]
        logger.error(f"Failed to post message: {e.response['error']}")
        raise


if __name__ == "__main__":
    try:
        main(sys.argv)
    except:
        sys.exit(-1)
