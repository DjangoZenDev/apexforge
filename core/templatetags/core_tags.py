"""
Custom template tags and filters for ApexForge
"""
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag(takes_context=True)
def lang_url(context, lang_code):
    """
    Return the current page's URL translated to the given language code.

    Two-step process:
    1. Strip any existing /xx/ language prefix to get a neutral path like /medical/.
    2. Call translate_url() with the default language (English) active so that
       resolve() always succeeds regardless of the current request language.
       Without this, switching from e.g. Spanish → German fails because
       resolve('/medical/') with Spanish active expects a /es/ prefix.
    """
    from django.conf import settings
    from django.urls import translate_url
    from django.utils.translation import override as lang_override

    request = context.get("request")
    if not request:
        return "/"

    path = request.path

    # Strip existing /xx/ prefix so we always pass a prefix-free path
    default_lang = getattr(settings, "LANGUAGE_CODE", "en")
    non_default = [l[0] for l in getattr(settings, "LANGUAGES", []) if l[0] != default_lang]
    for lang in non_default:
        pfx = "/" + lang
        if path == pfx:
            path = "/"
            break
        if path.startswith(pfx + "/"):
            path = path[len(pfx):]  # keep leading /
            break

    # Force default (English) active so resolve() works on the prefix-free path,
    # then translate_url internally reverses with the target lang_code.
    with lang_override(default_lang):
        return translate_url(path, lang_code)


@register.filter
def currency(value):
    try:
        return f"€{float(value):,.2f}"
    except (ValueError, TypeError):
        return "€0.00"


@register.filter
def abs_value(value):
    try:
        return abs(float(value))
    except (ValueError, TypeError):
        return 0


@register.filter
def percentage(value, total):
    try:
        if float(total) == 0:
            return "0%"
        return f"{float(value) / float(total) * 100:.1f}%"
    except (ValueError, TypeError, ZeroDivisionError):
        return "0%"


@register.filter
def rating_stars(value):
    try:
        v = int(float(value))
        filled = "★" * v
        empty  = "☆" * (5 - v)
        return mark_safe(
            f'<span class="text-amber-500">{filled}</span>'
            f'<span class="text-gray-300">{empty}</span>'
        )
    except (ValueError, TypeError):
        return mark_safe('<span class="text-gray-300">☆☆☆☆☆</span>')


@register.filter
def role_badge(role):
    colors = {
        "super_admin":  "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
        "club_owner":   "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200",
        "manager":      "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
        "coach":        "bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200",
        "athlete":      "bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200",
        "scout":        "bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200",
        "fan_investor": "bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200",
    }
    label = role.replace("_", " ").title()
    cls = colors.get(role, "bg-gray-100 text-gray-800")
    return mark_safe(f'<span class="px-2 py-0.5 rounded-full text-xs font-medium {cls}">{label}</span>')


@register.filter
def status_badge(status):
    colors = {
        "active":     "bg-emerald-100 text-emerald-800",
        "inactive":   "bg-gray-100 text-gray-600",
        "scheduled":  "bg-blue-100 text-blue-800",
        "completed":  "bg-green-100 text-green-800",
        "cancelled":  "bg-red-100 text-red-800",
        "postponed":  "bg-yellow-100 text-yellow-800",
        "draft":      "bg-gray-100 text-gray-600",
        "published":  "bg-emerald-100 text-emerald-800",
    }
    cls = colors.get(status.lower(), "bg-gray-100 text-gray-600")
    return mark_safe(f'<span class="px-2 py-0.5 rounded-full text-xs font-medium {cls}">{status.replace("_"," ").title()}</span>')


@register.filter
def split(value, sep=","):
    """Split a string by separator. Usage: {{ "a,b,c"|split:"," }}"""
    try:
        return value.split(sep)
    except (AttributeError, TypeError):
        return []


@register.filter
def lookup(obj, key):
    """Dynamic key/attribute lookup. Usage: {{ form|lookup:field_name }}"""
    try:
        return obj[key]
    except (KeyError, TypeError):
        try:
            return getattr(obj, key)
        except AttributeError:
            return ""


@register.simple_tag
def kpi_card_class(trend):
    """Return Tailwind classes for KPI trend arrow."""
    if trend == "up":
        return "text-emerald-600"
    elif trend == "down":
        return "text-red-500"
    return "text-gray-500"


@register.inclusion_tag("partials/kpi_card.html")
def kpi_card(title, value, icon, color="emerald", trend=None, trend_value=None):
    return {
        "title": title, "value": value, "icon": icon,
        "color": color, "trend": trend, "trend_value": trend_value,
    }
