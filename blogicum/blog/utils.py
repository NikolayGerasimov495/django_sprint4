from django.db import models
from django.db.models import Count
from django.utils import timezone


class PublishedPostQuerySet(models.QuerySet):
    """Менеджер публикации"""

    def published_filter(self):
        return self.filter(is_published=True,
                           category__is_published=True,
                           pub_date__lte=timezone.now())

    def published_count_order(self):
        return (self.annotate(comment_count=Count("comment"))
                .order_by("-pub_date"))
