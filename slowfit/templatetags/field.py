from django import template
from django.db.models import Model
from django.db.models import fields

register = template.Library()


@register.inclusion_tag('snippets/field.html')
def field(obj: Model, name: str, mode: str, **attrs):
    fld = obj._meta.get_field(name)
    if isinstance(fld, (fields.IntegerField, fields.FloatField, fields.SmallIntegerField,
                        fields.PositiveIntegerField, fields.PositiveSmallIntegerField)):
        inputtype = "number"
    elif isinstance(fld, fields.URLField):
        inputtype = "url"
    else:
        inputtype = "text"

    ret = {
        "object": obj,
        "field": fld,
        "name": name,
        "value": getattr(obj, name),
        "type": fld.__class__.__name__,
        "mode": mode,
        "inputtype": inputtype,
        "attrs": attrs,
    }
    return ret
