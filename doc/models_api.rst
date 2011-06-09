Models reference
================

Base models
~~~~~~~~~~~

.. py:module:: ratings.models

.. py:class:: Score(models.Model)

    A score for a content object.
    
    Fields: *content_type*, *object_id*, *content_object*, *key*, 
    *average*, *total*, *num_votes*.
    
    Manager: ``ratings.managers.RatingsManager``
    
    .. py:method:: get_votes(self)
    
        Return all the related votes (same *content_object* and *key*).
    
    .. py:method:: recalculate(self, weight=0, commit=True)
    
        Recalculate the score using all the related votes, and updating
        average score, total score and number of votes.
        
        The optional argument *weight* is used to calculate the average
        score: an higher value means a lot of votes are needed to increase
        the average score of the target object.
        
        If the optional argument *commit* is False then the object
        is not saved.
    

.. py:class:: Vote(models.Model)

    A single vote relating a content object.
    
    Fields: *content_type*, *object_id*, *content_object*, *key*, 
    *score*, *user*, *ip_address*, *cookie*, *created_at*, *modified_at*.
    
    Manager: ``ratings.managers.RatingsManager``
    
    .. py:method:: get_score(self)
    
        Return the score related to current *content_object* and *key*.
        Return None if score does not exist.
    
    .. py:method:: by_anonymous(self)
    
        Return True if this vote is given by an anonymous user.
    

Adding or changing scores and votes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. py:function:: upsert_score(instance_or_content, key, weight=0)

    Update or create current score values (average score, total score and 
    number of votes) for target object *instance_or_content* and 
    the given *key*. 
    
    The argument *instance_or_content* can be a model instance or 
    a sequence *(content_type, object_id)*.
    
    You can use the optional argument *weight* to make more difficult
    for a target object to obtain a higher rating.
    
    Return a sequence *score, created*.


Deleting scores and votes
~~~~~~~~~~~~~~~~~~~~~~~~~

.. py:function:: delete_scores_for(instance_or_content)

    Delete all score objects related to *instance_or_content*, that can be 
    a model instance or a sequence *(content_type, object_id)*.

.. py:function:: delete_votes_for(instance_or_content)
    
    Delete all vote objects related to *instance_or_content*, that can be 
    a model instance or a sequence *(content_type, object_id)*.


In bulk selections
~~~~~~~~~~~~~~~~~~

.. py:function:: annotate_scores(queryset_or_model, key, **kwargs)

    Annotate *queryset_or_model* with scores, in order to retreive from
    the database all score values in bulk.

    The first argument *queryset_or_model* must be, of course, a queryset
    or a Django model object. The argument *key* is the score key.
    
    In *kwargs* it is possible to specify the values to retreive mapped 
    to field names (it is up to you to avoid name clashes).
    You can annotate the queryset with the number of votes (*num_votes*), 
    the average score (*average*) and the total sum of all votes (*total*).
    
    For example, the following call::
    
        annotate_scores(Article.objects.all(), 'main',
            average='average', num_votes='num_votes')
        
    Will return a queryset of article and each article will have two new
    attached fields *average* and *num_votes*.
    
    Of course it is possible to sort the queryset by a score value, e.g.::
    
        for article in annotate_scores(Article, 'by_staff', 
            staff_avg='average', staff_num_votes='num_votes'
            ).order_by('-staff_avg', '-staff_num_votes'):
            print 'staff num votes:', article.staff_num_votes
            print 'staff average:', article.staff_avg

.. py:function:: annotate_votes(queryset_or_model, key, user, score='score')

    Annotate *queryset_or_model* with votes, in order to retreive from
    the database all vote values in bulk.
    
    The first argument *queryset_or_model* must be, of course, a queryset
    or a Django model object. The argument *key* is the score key.
    
    The votes are filtered using given *user*. For anonymous voters this
    functionality is unavailable.
    
    The score itself will be present in the attribute named *score* of 
    each instance of the returned queryset.
    
    Usage example::
    
        for article in annotate_votes(Article.objects.all(), 'main', myuser, 
            score='myscore'):
            print 'your vote:', article.myscore


Abstract models
~~~~~~~~~~~~~~~

.. py:class:: RatedModel(models.Model)

    Mixin for votable models.
    
    .. py:method:: get_score(self, key)
    
        Return the score for the current model instance and *key*.
        Useful attrs:
        
            - self.get_score(mykey).average
            - self.get_score(mykey).total
            - self.get_score(mykey).num_votes
        
        If score does not exist, return None.


Managers
~~~~~~~~

.. py:module:: ratings.managers

.. py:class:: RatingsManager(models.Manager)

    Manager used by *Score* and *Vote* models.
    
    .. py:method:: get_for(self, content_object, key, **kwargs)
    
        Return the instance related to *content_object* and matching *kwargs*. 
        Return None if a vote is not found.
    
    .. py:method:: filter_for(self, content_object_or_model, **kwargs)
    
        Return all the instances related to *content_object_or_model* and 
        matching *kwargs*. The argument *content_object_or_model* can be
        both a model instance or a model class.
    
    .. py:method:: filter_with_contents(self, **kwargs)
    
        Return all instances retreiving content objects in bulk in order
        to minimize db queries, e.g. to get all objects voted by a user::
        
            for vote in Vote.objects.filter_with_contents(user=myuser):
                vote.content_object # this does not hit the db
    