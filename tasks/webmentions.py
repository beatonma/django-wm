from celery import shared_task
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from django.conf import settings
import requests
import re

from contact.tasks import send_notification
from main.models import WebPost
from mentions.models import Webmention, HCard

from celery.utils.log import get_task_logger


log = get_task_logger(__name__)


@shared_task
def process_outgoing_webmention():
    # TODO
    pass


@shared_task
def process_incoming_webmention(http_post, client_ip):
    log.info('Processing webmention "{}"'.format(http_post))

    # Source and target have already been verified
    # as valid addresses before this method is called
    source = http_post['source']
    target = http_post['target']

    wm = Webmention.create(source, target)
    wm.sent_by = client_ip

    def report_error(error_message):
        message = '{} [\'{}\' -> \'{}\']'.format(error_message, source, target)
        log.error(message)
        wm.notes = message
        wm.save()
        send_notification(
            'Webmention error',
            message,
            'django,error,beatonma.org')

    # Verify that the target page exists on this server
    try:
        t_parsed = urlparse(target)
        domain = t_parsed.netloc
        if domain not in settings.ALLOWED_HOSTS:
            report_error(
                'The target domain does not appear to belong to this server')
            return
        path = t_parsed.path
        match = re.match('/a/([^/]+)', path)
        if match:
            slug = match.group(1)
            post = WebPost.objects.get(slug=slug)
            if post:
                wm.target_slug = slug
            else:
                report_error('Slug "{}" not found'.format(slug))
                return
        else:
            # If article is not found, try and find the page via a
            # normal http request
            response = requests.get(target)
            if response.status_code >= 300:
                report_error('Target returned status code \'{}\''
                             .format(response.status_code))
                return
    except Exception as e:
        report_error('Error getting target post: {}'.format(e))
        return

    # Verify that the source page exists and really contains a link
    # to the target
    try:
        response = requests.get(source)
        content_type = response.headers['content-type']

        if response.status_code >= 300:
            report_error('Source returned status code \'{}\''
                         .format(response.status_code))
            return

        if 'text/html' in content_type:
            log.debug('source is an html document')
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a', href=target)
            if links:
                log.debug('Target found: {}'.format(links))
            else:
                report_error('Target not found in source document')
                return

            hcard_element = soup.find(class_='h-card')
            if hcard_element:
                hcard = HCard.from_soup(soup)
                if hcard:
                    log.debug('{}'.format(hcard))
                    wm.hcard_homepage = hcard.homepage or None
                    hcard.save()
                else:
                    log.warn('Could not construct an hcard from source page')

        else:
            report_error('Unrecognised source content type: "{}"'
                         .format(content_type))
            return
    except Exception as e:
        report_error('Failed to retrieve source url for webmention: {}'
                     .format(e))
        return

    wm.validated = True
    wm.save()

    send_notification('Webmention', '{}'.format(wm),
                      'beatonma.org,important,webmention')
