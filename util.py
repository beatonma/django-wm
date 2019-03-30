import logging

from importlib import import_module

from django.apps import apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.flatpages.views import flatpage

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
                if match.func != flatpage:
                    break
        except:
            pass
    else:
        # No match found
        raise TargetDoesNotExist(
            f'Cannot find a matching urlpattern entry for path={target_path}')

    log.debug(f'Found matching urlpattern: {match}')

    # Dotted path to model class declaration
    model_name = match.kwargs.get('model_name')

    # Required to retrieve the target model instance
    slug = match.kwargs.get('slug')

    if not model_name:
        raise BadConfig(
            'urlpattern must include a kwarg entry called \'model_name\': '
            f'{match}')
    if not slug:
        raise BadConfig(
            f'urlpattern must include a kwarg entry called \'slug\': {match}')

    try:
        model = apps.get_model(model_name)
    except LookupError:
        raise BadConfig(
            f'Cannot find model `{model_name}` - check your urlpattern!')

    try:
        return model.objects.get(slug=slug)
    except ObjectDoesNotExist:
        raise TargetDoesNotExist(
            f'Cannot find instance of model=\'{model}\' with slug=\'{slug}\'')
