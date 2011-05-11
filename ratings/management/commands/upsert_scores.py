from django.core.management.base import BaseCommand

from ratings import models

class Command(BaseCommand):
    """
    Create or update all scores, based on existing votes.
    """
    option_list = BaseCommand.option_list + (
        make_option('-w', "--weight", 
            action='store', dest='weight', default=0, type='int',
            help=('The weight used to calculate average score.')
        ),
    )
    help = "Create or update all scores, based on existing votes."

    def handle_noargs(self, **options):
        contents = set()
        for vote in models.Vote.objects.all():
            content = (vote.content_type, vote.object_id)
            if content not in contents:
                models.upsert_score(content, vote.key, options['weight'])
                contents.add(content)
