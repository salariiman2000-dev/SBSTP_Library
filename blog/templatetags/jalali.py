import datetime

import jdatetime

from django import template
from django.utils import timezone


register = template.Library()


@register.filter
def jalali_date(value, fmt="%Y/%m/%d"):
    """
    تبدیل تاریخ میلادی به تاریخ شمسی برای استفاده در Template.
    """

    if not value:
        return ""

    try:
        if isinstance(value, datetime.datetime):

            if timezone.is_aware(value):
                value = timezone.localtime(value)

            jalali = jdatetime.datetime.fromgregorian(
                datetime=value
            )

            return jalali.strftime(fmt)

        if isinstance(value, datetime.date):

            jalali = jdatetime.date.fromgregorian(
                date=value
            )

            return jalali.strftime(fmt)

    except Exception:
        return ""

    return ""