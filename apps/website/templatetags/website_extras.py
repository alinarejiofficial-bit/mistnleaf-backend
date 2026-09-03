from django import template

from apps.website.content import format_inr as _format_inr

register = template.Library()


@register.filter(name="format_inr")
def format_inr_filter(amount) -> str:
    return _format_inr(amount)
