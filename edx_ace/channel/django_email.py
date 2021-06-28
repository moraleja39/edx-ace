"""
:mod:`edx_ace.channel.django_email` implements a Django `send_mail()` email
delivery channel for ACE.
"""
import logging
from smtplib import SMTPException

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from edx_ace.channel import Channel
from edx_ace.channel.mixins import EmailChannelMixin
from edx_ace.errors import FatalChannelDeliveryError

LOG = logging.getLogger(__name__)

DEFAULT_TEMPLATE = """\
<!DOCTYPE html>
<html>
    <head>
        {head_html}
    </head>
    <body>
        {body_html}
    </body>
</html>
"""

TEMPLATE = getattr(settings, "ACE_DJANGO_TEMPLATE", DEFAULT_TEMPLATE)


class DjangoEmailChannel(EmailChannelMixin, Channel):
    """
    A `send_mail()` channel for edX ACE.

    This is both useful for providing an alternative to Sailthru and to debug ACE mail by
    inspecting `django.core.mail.outbox`.



    Example:

        Sample settings::

            .. settings_start
            EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
            EMAIL_HOST = 'localhost'
            DEFAULT_FROM_EMAIL = 'hello@example.org'

            ACE_CHANNEL_DEFAULT_EMAIL = 'sailthru_email'
            ACE_CHANNEL_TRANSACTIONAL_EMAIL = 'django_email'

            ACE_ENABLED_CHANNELS = [
                'sailthru_email',
                'django_email',
            ]
            .. settings_end
    """

    @classmethod
    def enabled(cls):
        """
        Returns: True always!
        """
        return True

    def deliver(self, message, rendered_message):
        subject = self.get_subject(rendered_message)
        from_name = re.sub('\\s+', ' ', rendered_message.from_name, re.UNICODE).strip()
        from_address = self.get_from_address(message)
        reply_to = message.options.get('reply_to', None)

        rendered_template = self.make_simple_html_template(rendered_message.head_html, rendered_message.body_html)
        try:
            mail = EmailMultiAlternatives(
                subject=subject,
                body=rendered_message.body,
                from_email="{from_name} <{from_address}>".format(
                    from_name=from_name,
                    from_address=from_address
                ),
                to=[message.recipient.email_address],
                reply_to=reply_to,
            )

            mail.attach_alternative(rendered_template, 'text/html')
            mail.send()
        except SMTPException as e:
            LOG.exception(e)
            raise FatalChannelDeliveryError('An SMTP error occurred (and logged) from Django send_email()') from e
