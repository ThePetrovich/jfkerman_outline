from django.utils.translation import gettext, ngettext
from django import template
from django.utils import formats
from django.utils.encoding import force_str
from django.utils.html import avoid_wrapping

register = template.Library()

@register.filter(is_safe=True)
def datalimitbytes(bytes_):
    """
    Format the value like a 'human-readable' file size (i.e. 13 KB, 4.1 MB,
    102 bytes, etc.).
    """
    try:
        bytes_ = int(bytes_)
    except (TypeError, ValueError, UnicodeDecodeError):
        value = ngettext("%(size)d", "%(size)d", 0) % {"size": 0}
        return avoid_wrapping(value)

    def filesize_number_format(value):
        return formats.number_format(round(value, 1), 1)

    KB = 1 << 10
    MB = 1 << 20
    GB = 1 << 30
    TB = 1 << 40
    PB = 1 << 50

    negative = bytes_ < 0
    if negative:
        bytes_ = -bytes_  # Allow formatting of negative numbers.

    if bytes_ < KB:
        value = ngettext("%(size)d", "%(size)d", bytes_) % {"size": bytes_}
    elif bytes_ < MB:
        value = gettext("%s") % filesize_number_format(bytes_ / KB)
    elif bytes_ < GB:
        value = gettext("%s") % filesize_number_format(bytes_ / MB)
    elif bytes_ < TB:
        value = gettext("%s") % filesize_number_format(bytes_ / GB)
    elif bytes_ < PB:
        value = gettext("%s") % filesize_number_format(bytes_ / TB)
    else:
        value = gettext("%s") % filesize_number_format(bytes_ / PB)

    if negative:
        value = "-%s" % value
    return avoid_wrapping(value)

@register.filter(is_safe=True)
def datalimitmb(bytes_):
    """
    Format the value like a 'human-readable' file size (i.e. 13 KB, 4.1 MB,
    102 bytes, etc.).
    """
    try:
        bytes_ = int(bytes_)
    except (TypeError, ValueError, UnicodeDecodeError):
        value = gettext("%(size)d MB") % {"size": 0}
        return avoid_wrapping(value)

    def filesize_number_format(value):
        return formats.number_format(round(value, 1), 1)

    MB = 1
    GB = 1 << 10
    TB = 1 << 20
    PB = 1 << 30

    negative = bytes_ < 0
    if negative:
        bytes_ = -bytes_  # Allow formatting of negative numbers.

    if bytes_ < GB:
        value = gettext("%s MB") % filesize_number_format(bytes_ / MB)
    elif bytes_ < TB:
        value = gettext("%s GB") % filesize_number_format(bytes_ / GB)
    elif bytes_ < PB:
        value = gettext("%s TB") % filesize_number_format(bytes_ / TB)
    else:
        value = gettext("%s PB") % filesize_number_format(bytes_ / PB)

    if negative:
        value = "-%s" % value
    return avoid_wrapping(value)