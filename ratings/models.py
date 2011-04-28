from django.db import models, transaction, IntegrityError
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.functional import memoize
from django.contrib.auth.models import User

class Score(models.Model):
    """
    A score for a content object.
    """
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    
    key = models.CharField(max_length=16)
    
    average = models.FloatField(default=0)
    total = models.IntegerField(default=0)
    num_votes = models.PositiveIntegerField(default=0)
        
    class Meta:
        unique_together = ('content_type', 'object_id', 'key')

    def __unicode__(self):
        return u'Score for %s' % self.content_object
        
        
class Vote(models.Model):
    """
    A single vote relating a content object.
    """
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    
    key = models.CharField(max_length=16)
    score = models.IntegerField()

    user = models.ForeignKey(User, blank=True, null=True, related_name='votes')
    ip_address = models.IPAddressField()
    cookie = models.CharField(max_length=32, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('content_type', 'object_id', 'key', 
            'user', 'ip_address', 'cookie')

    def __unicode__(self):
        return u'Vote %d to %s by %s' % (self.score, self.content_object,
            self.user or self.ip_address)


def _get_content(instance_or_content):
    """
    Given a model instance or a sequence *(content_type, object_id)*
    return a tuple *(content_type, object_id)*.
    """
    try:
        object_id = instance_or_content.pk
    except AttributeError:
        return instance_or_content
    else:
        return ContentType.objects.get_for_model(instance_or_content), object_id
        
_get_score_for_cache, _get_vote_for_cache = {}, {}
   
def get_score_for(instance_or_content, key):
    """
    Return the score instance for the target object *instance_or_content*
    and the given *key*.
    Return None if a score is not found.
    The argument *instance_or_content* can be a model instance or 
    a sequence *(content_type, object_id)*.
    """
    content_type, object_id = _get_content(instance_or_content)
    try:
        return instance.rankings_scores.get(key=key)
    except instance.ranking_scores.model.DoesNotExist:
        return None
        
def get_vote_for(instance_or_content, key, user):
    """
    Return the vote instance created by *user* for the target object 
    *instance_or_content* and the given *key*.
    The argument *instance_or_content* can be a model instance or 
    a sequence *(content_type, object_id)*.
    """
    content_type, object_id = _get_content(instance_or_content)
    try:
        return instance.rankings_scores.get(key=key)
    except instance.ranking_scores.model.DoesNotExist:
        return None

get_score_for = memoize(get_score_for, _get_score_for_cache, 2)
get_vote_for = memoize(get_vote_for, _get_vote_for_cache, 3)

def upsert_score(instance_or_content, key):
    """
    Update or create current score values (average score, total score and 
    number of votes) for target object *instance_or_content* and 
    the given *key*. 
    The argument *instance_or_content* can be a model instance or 
    a sequence *(content_type, object_id)*.
    Return a sequence *score, created*.
    """
    content_type, object_id = _get_content(instance_or_content)
    lookups = {
        'content_type': content_type,
        'object_id': object_id,
        'key': key,
    }
    data = Vote.objects.filter(**lookups).aggregate(total=models.Sum('score'), 
        average=models.Avg('score'), num_votes=models.Count('id'))
    score, created = Score.objects.get_or_create(**lookups)
    for k, v in data.items():
        setattr(score, k, v)
    score.save()
    return score, created

def upsert_vote(instance_or_content, key, score, **kwargs):
    """
    Update or create a vote instance described by *key*, *score*, other 
    *kwargs* and *instance_or_content*, that can be a model instance or 
    a sequence *(content_type, object_id)*.
    Return a sequence *vote, created*.
    """
    content_type, object_id = _get_content(instance_or_content)
    lookups = {
        'content_type': content_type,
        'object_id': object_id,
        'key': key,
    }
    lookups.update(kwargs)
    try:
        vote = Vote.objects.get(**lookups)
    except Vote.DoesNotExist:
        try:
            vote = Vote(**lookups)
            vote.score = score
            sid = transaction.savepoint(using=Vote.objects.db)
            vote.save(force_insert=True, using=Vote.objects.db)
            transaction.savepoint_commit(sid, using=Vote.objects.db)
            return vote, True
        except IntegrityError, e:
            transaction.savepoint_rollback(sid, using=Vote.objects.db)
            try:
                vote = Vote.objects.get(**lookups)
            except Vote.DoesNotExist:
                raise e
    vote.score = score
    vote.save()
    return vote, False
    

class RatedModel(models.Model):
    """
    Mixin for votables models.
    """
    ranking_scores = generic.GenericRelation(Score)
    ranking_votes = generic.GenericRelation(Vote)
    
    class Meta:
        abstract = True 
        
    def get_score(self, key):
        """
        Return the score for the current model instance and score *key*.
        Useful attrs:
            - self.get_score(mykey).average
            - self.get_score(mykey).total
            - self.get_score(mykey).num_votes
        If score does not exist, return None.
        """
        return score_for(self, key)
