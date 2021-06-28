"""
:mod:`edx_ace.channel.mixins` implements some helper methods for channels
"""
import re

from django.conf import settings

from edx_ace.channel import ChannelType
from edx_ace.errors import FatalChannelDeliveryError


class EmailChannelMixin:
    """
    Adds some common email utility methods to email channels
    """
    channel_type = ChannelType.EMAIL

    @staticmethod
    def get_from_address(message, rendered_message=None):
        """Grabs the from_address from the message with fallback and error handling"""
        default_from_address = getattr(settings, 'DEFAULT_FROM_EMAIL', None)
        from_address = message.options.get('from_address', default_from_address)
        from_name = getattr(rendered_message, 'from_name', None)
        if not from_address:
            raise FatalChannelDeliveryError(
                'from_address must be included in message delivery options or as the DEFAULT_FROM_EMAIL settings'
            )
        if from_name is not None:
            from_name = re.sub('\\s+', ' ', str(from_name), re.UNICODE).strip()
            return "{from_name} <{from_address}>".format(from_name=from_name, from_address=from_address)
        else:
            return from_address

    @staticmethod
    def get_subject(rendered_message):
        # Compress spaces and remove newlines to make it easier to author templates.
        return re.sub('\\s+', ' ', rendered_message.subject, re.UNICODE).strip()

    @staticmethod
    def make_simple_html_template(head_html, body_html):
        return """<!DOCTYPE html>
<html>
  <head>
    {head_html}
  </head>
  <body>
    {body_html}
  </body>
</html>""".format(head_html=head_html, body_html=body_html)
