from typing import Callable

from mentions import contract
from mentions.helpers.types import ModelClass
from mentions.helpers.util import get_dotted_model_name

MENTIONS_KWARGS = "_mentions_kwargs"


def annotate_viewfunc(
    view_func: Callable,
    model_class: ModelClass,
    lookup: dict,
) -> Callable:
    setattr(
        view_func,
        MENTIONS_KWARGS,
        {
            contract.URLPATTERNS_MODEL_NAME: get_dotted_model_name(model_class),
            **lookup,
        },
    )
    return view_func


def get_annotation_from_viewfunc(view_func: Callable) -> dict:
    return getattr(view_func, MENTIONS_KWARGS, {})
