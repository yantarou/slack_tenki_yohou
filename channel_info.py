import datetime
import json
import pytz


class ChannelInfo:
    id = None
    name = None
    created = None
    is_archived = None
    num_members = None
    topic = None
    purpose = None

    last_update = None
    icon = None

    def __init__(self, channel, last_update, time_zone):
        self.id = channel['id']
        self.name = channel['name']
        self.created = channel['created']
        self.is_archived = channel['is_archived']
        self.num_members = channel['num_members']
        self.last_update = last_update
        self.icon = ":slack:"

        if channel['purpose']['value']:
            self.purpose = json.dumps(
                channel['purpose']['value'],
                ensure_ascii=False
            ).strip('"')
        else:
            self.purpose = "未設定"

        if channel['topic']['value']:
            self.topic = json.dumps(
                channel['topic']['value'],
                ensure_ascii=False
            ).strip('"')
        else:
            self.topic = "未設定"

        # Set icon based on last update
        if last_update is not None:
            message_age = datetime.datetime.now(tz=pytz.timezone(time_zone)) - last_update
            self.last_update = "%s (%d 日前)" % (last_update.strftime('%Y-%m-%d'), message_age.days)
            if message_age.days < 10:
                self.icon = ":sunny:"
            elif message_age.days < 20:
                self.icon = ":sun_small_cloud:"
            elif message_age.days < 30:
                self.icon = ":sun_behind_cloud:"
            elif message_age.days < 45:
                self.icon = ":cloud:"
            elif message_age.days < 60:
                self.icon = ":rain_cloud:"
            else:
                self.icon = ":thunder_cloud_and_rain:"
        else:
            self.last_update = "不明"
            self.icon = ":question:"

        # Set icon based on channel age
        channel_age = datetime.datetime.now() - datetime.datetime.fromtimestamp(self.created)
        if channel_age.days < 14:
            self.icon = ":sunrise_over_mountains:"
