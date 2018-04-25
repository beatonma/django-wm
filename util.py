import logging

from importlib import import_module

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from mentions.exceptions import BadConfig, TargetDoesNotExist


log = logging.getLogger(__name__)


def get_model_for_url(target_path):
    """
    Find a match in urlpatterns and return the corresponding model instance.
    """
    target_path = target_path.lstrip('/')  # Remove any leading slashes
    urlconf = import_module(settings.ROOT_URLCONF)
    urlpatterns = urlconf.urlpatterns
    for x in urlpatterns:
        # x may be an instance of either:
        # - django.urls.resolvers.URLResolver
        # - django.urls.resolvers.URLPattern
        try:
            match = x.resolve(target_path)
            if match:
                break
        except:
            pass
    else:
        # No match found
        raise TargetDoesNotExist(
            'Cannot find a matching urlpattern entry for path={}'
            .format(target_path))

    log.info('Found matching urlpattern: {}'.format(match))

    # Dotted path to model class declaration
    model_name = match.kwargs.get('model_name')

    # Required to retrieve the target model instance
    slug = match.kwargs.get('slug')

    if not model_name:
        raise BadConfig(
            'urlpattern must include a kwarg entry called \'model_name\': {}'
            .format(match))
    if not slug:
        raise BadConfig(
            'urlpattern must include a kwarg entry called \'slug\': {}'
            .format(match))

    from django.apps import apps
    model = apps.get_model(model_name)

    try:
        return model.objects.get(slug=slug)
    except ObjectDoesNotExist:
        raise TargetDoesNotExist(
            'Cannot find instance of model=\'{}\' with slug=\'{}\''
            .format(model, slug))
