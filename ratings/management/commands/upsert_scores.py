from django.core.management.base import NoArgsCommand

from ratings import models

class Command(NoArgsCommand):
    help = "Create or update all scores, based on existing votes."

    def handle_noargs(self, **options):
        contents = set()
        for vote in models.Vote.objects.all():
            content = (vote.content_type, vote.object_id)
            if content not in contents:
                models.upsert_score(content, vote.key)
                contents.add(content)
