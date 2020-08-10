from django import template

register = template.Library()


@register.inclusion_tag('snippets/avatar.html')
def avatar(owner):
    ret = {
        "owner": owner,
        "owner_kind": owner.__class__.__name__
    }
    ret = owner.get_avatar_context(ret)
    ret["avatar"] = owner.asset_by_tag(ret["tag"])
    return ret
