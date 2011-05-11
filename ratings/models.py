import string

from django.db import models, transaction, IntegrityError
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.functional import memoize
from django.utils.datastructures import SortedDict
from django.contrib.auth.models import User

# MODELS

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
        
    def get_votes(self):
        """
        Return all the related votes (same *content_object* and *key*).
        """
        return Vote.objects.filter(content_type=self.content_type,
            object_id=self.object_id, key=self.key)
    
    def recalculate(self, weight=0, commit=True):
        """
        Recalculate the score using all the related votes, and updating
        average score, total score and number of votes.
        
        The optional argument *weight* is used to calculate the average
        score: an higher value means a lot of votes are needed to increase
        the average score of the target object.
        
        If the optional argument *commit* is False then the object
        is not saved.
        """
        data = self.get_votes().aggregate(total=models.Sum('score'), 
            num_votes=models.Count('id'))
        self.total = data['total']
        self.num_votes = data['num_votes']
        self.average = self.total / (self.num_votes + weight)
        if commit:
            self.save()
        
        
class Vote(models.Model):
    """
    A single vote relating a content object.
    """
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    
    key = models.CharField(max_length=16)
    score = models.FloatField()

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
            
    def get_score(self):
        """
        Return the score related to current *content_object* and *key*.
        Return None if score does not exist.
        """
        if not hasattr(self, '_score_cache'):
            try:
                self._score_cache = Score.objects.get(key=self.key, 
                    content_type=self.content_type, object_id=self.object_id)
            except Score.DoesNotExist:
                self._score_cache = None
        return self._score_cache
        

# GETTING SCORES AND VOTES

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
        return Score.objects.get(content_type=content_type,
            object_id=object_id, key=key)
    except Score.DoesNotExist:
        return None
        
def get_vote_for(instance_or_content, key, 
    user=None, ip_address=None, cookies=None):
    """
    Return the vote instance created by *user* for the target object 
    *instance_or_content* and the given *key*.
    Return None if a vote is not found.
    
    The argument *instance_or_content* can be a model instance or 
    a sequence *(content_type, object_id)*.
    """
    # TODO: manage anonymous votes
    content_type, object_id = _get_content(instance_or_content)
    try:
        return Vote.objects.get(content_type=content_type,
            object_id=object_id, key=key, user=user)
    except Vote.DoesNotExist:
        return None

get_score_for = memoize(get_score_for, _get_score_for_cache, 2)
get_vote_for = memoize(get_vote_for, _get_vote_for_cache, 5)


# ADDING OR CHANGING SCORES AND VOTES

def upsert_score(instance_or_content, key, weight=0):
    """
    Update or create current score values (average score, total score and 
    number of votes) for target object *instance_or_content* and 
    the given *key*. 
    
    The argument *instance_or_content* can be a model instance or 
    a sequence *(content_type, object_id)*.
    
    You can use the optional argument *weight* to make more difficult
    for a target object to obtain a higher rating.
    
    Return a sequence *score, created*.
    """
    content_type, object_id = _get_content(instance_or_content)
    score, created = Score.objects.get_or_create(content_type=content_type,
        object_id=object_id, key=key)
    score.recalculate(weight=weight)
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
    

# DELETING SCORES AND VOTES

def delete_scores_for(instance_or_content):
    """
    Delete all score objects related to *instance_or_content*, that can be 
    a model instance or a sequence *(content_type, object_id)*.
    """
    content_type, object_id = _get_content(instance_or_content)
    Score.objects.filter(content_type=content_type, object_id=object_id).delete()
    
def delete_votes_for(instance_or_content):
    """
    Delete all vote objects related to *instance_or_content*, that can be 
    a model instance or a sequence *(content_type, object_id)*.
    """
    content_type, object_id = _get_content(instance_or_content)
    Vote.objects.filter(content_type=content_type, object_id=object_id).delete()

# BULK SELECT QUERIES
    
def annotate_score(queryset_or_model, key, **kwargs):
    """
    Annotate scores in *queryset_or_model*, in order to retreive from
    the database all score values in bulk.

    The first argument *queryset_or_model* must be, of course, a queryset
    or a Django model object. The argument *key* is the score key.
    
    In *kwargs* it is possible to specify the values to retreive mapped 
    to field names (it is up to you to avoid name clashes).
    You can annotate the number of votes (*num_votes*), the average score
    (*average*) and the total sum of all votes (*total*).
    
    For example, the following call::
    
        annotate_score(Article.objects.all(), 'main',
            average='average', num_votes='num_votes')
        
    Will return a queryset of article and each article will have two new
    attached fields *average* and *num_votes*.
    
    Of course it is possible to sort the queryset by a score value, e.g.::
    
        for article in annotate_score(Article, 'by_staff', 
            staff_avg='average', staff_num_votes='num_votes'
            ).order_by('-staff_avg', '-staff_num_votes'):
            print 'staff num votes:', article.staff_num_votes
            print 'staff average:', article.staff_avg
    """
    # getting the queryset
    if isinstance(queryset_or_model, models.base.ModelBase):
        queryset = queryset_or_model.objects.all()
    else:
        queryset = queryset_or_model
    # annotations are done only if fields are requested
    if kwargs:
        # preparing arguments for *extra* query
        select = SortedDict() # not really needed (see below)
        select_params = []
        opts = queryset.model._meta
        content_type = ContentType.objects.get_for_model(queryset.model)
        mapping = {
            'score_table': Score._meta.db_table,
            'model_table': opts.db_table,
            'model_pk_name': opts.pk.name,
            'content_type_id': content_type.pk,
            'key': key,
        }
        # building base query
        template = """
        SELECT ${field_name} FROM ${score_table} WHERE 
        ${score_table}.object_id = ${model_table}.${model_pk_name} AND 
        ${score_table}.content_type_id = ${content_type_id} AND
        ${score_table}.key = %s
        """
        template = string.Template(template).safe_substitute(mapping)
        # building one query for each requested field
        for alias, field_name in kwargs.items():
            query = string.Template(template).substitute(
                {'field_name': field_name})
            select[alias] = query
            # and that's why SortedDict are not really needed
            select_params.append(key) 
        return queryset.extra(select=select, select_params=select_params)
    return queryset
    
def annotate_votes(queryset_or_model, key, 
    user=None, ip_address=None, cookies=None):
    """
    Annotate votes in *queryset_or_model*, in order to retreive from
    the database all vote values in bulk.
    """
    # TODO
    pass
    

# ABSTACT MODELS
    
class RatedModel(models.Model):
    """
    Mixin for votable models.
    """
    rating_scores = generic.GenericRelation(Score)
    rating_votes = generic.GenericRelation(Vote)
    
    class Meta:
        abstract = True 
        
    def get_score(self, key):
        """
        Return the score for the current model instance and *key*.
        Useful attrs:
            - self.get_score(mykey).average
            - self.get_score(mykey).total
            - self.get_score(mykey).num_votes
        If score does not exist, return None.
        """
        return get_score_for(self, key)
