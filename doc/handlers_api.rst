Handlers reference
==================

.. py:module:: ratings.handlers

.. py:class:: RatingHandler

    Encapsulates content rating options for a given model.
    
    This class can be subclassed to specify different behaviour and options
    for ratings of a given model, but can also be used directly, just to
    handle default rating for any model. 
    
    The default rating provide only one 1-5 ranged (without decimal places) 
    score for each content object, and allows voting only for authenticated
    users.
    
    The default rating handler uses the project's settings as options: this 
    way you can register not customized rating handlers and then modify
    their options just editing the settings file.
    
    Most common rating needs can be handled by subclassing *RatingHandler* 
    and changing the values of pre-defined attributes. 
    The full range of built-in options is as follows.
    
    
    .. py:attribute:: allow_anonymous 
    
        set to False to allow votes only by authenticated users 
        (default: *False*)
    
    .. py:attribute:: score_range 
        
        a sequence *(min_score, max_score) representing the allowed score range 
        (including extremes) 
        note that the score *0* is reserved for vote deletion
        (default: *(1, 5)*)
    
    .. py:attribute:: score_step
        
        the step allowed in scores (default: *1*)
    
    .. py:attribute:: weight 
        
        this is used while calculating the average score and represents 
        the difficulty for a target object to obtain a higher rating
        (default: *0*)
    
    .. py:attribute:: default_key
        
        default key to use for votes when there is only one vote-per-content 
        (default: *'main'*)
    
    .. py:attribute:: can_delete_vote
    
        set to False if you do not want to allow users to delete a 
        previously saved vote (default: *True*)
    
    .. py:attribute:: can_change_vote 
    
        set to False if you do not want to allow users to change the score of 
        a previously saved vote (default: *True*)
    
    .. py:attribute:: next_querystring_key
    
        querystring key that can contain the url of the redirection performed 
        after voting (default: *'next'*)
    
    .. py:attribute:: votes_per_ip_address 
    
        the number of allowed votes per ip address, only used if anonymous users 
        can vote (default: *0*, means no limit)
    
    .. py:attribute:: form_class
    
        form class that will be used to handle voting 
        (default: *ratings.forms.VoteForm*) 
        this app, out of the box, provides also *SliderVoteForm* and a *StarVoteForm*
        
    .. py:attribute:: cookie_max_age
    
        if anonymous rating is allowed, you can define here the cookie max age
        as a number of seconds (default: one year)
        
    .. py:attribute:: success_messages
    
        this should be a sequence of (vote created, vote changed, vote deleted)
        messages sent (using *django.contrib.messages*) to the 
        user after a successful vote creation, change, deletion 
        (scored without using AJAX)
        if this is None, then no message is sent (default: *None*)
    
        
    For situations where the built-in options listed above are not sufficient, 
    subclasses of *RatingHandler* can also override the methods which 
    actually perform the voting process, and apply any logic they desire.
    
    See the method's docstrings for a description of how each method is
    used during the voting process.
    
    **Methods you may want to override, but not to call directly**

    .. py:method:: get_key(self, request, instance)
    
        Return the ratings key to be used to save the vote if the key
        is not provided by the user (for example with the optional
        argument *using* in templatetags).
        
        Subclasses can return different keys based on the *request* and
        the given target object *instance*.
        
        For example, if you want a different key to be used if the user is
        staff, you can override this method in this way::
        
            def get_key(self, request, instance):
                return 'staff' if request.user.is_superuser else 'normal'

        This method is called only if the user does not provide a rating key.
    
    .. py:method:: allow_key(self, request, instance, key)
    
        This method is called when the user tries to vote using the given
        rating *key* (e.g. when the voting view is called with POST data).
        
        The voting process continues only if this method returns True
        (i.e. a valid key is passed).
        
        For example, if you want to different rating for each target object,
        you can use two forms (each providing a different key, say 'main' and
        'other') and then allow those keys::
        
            def allow_key(self, request, instance, key):
                return key in ('main', 'other')
    
    .. py:method:: allow_vote(self, request, instance, key)
    
        This method can block the voting process if the current user 
        actually is not allowed to vote for the given *instance*

        By default the only check made here is for anonymous users, but this
        method can be subclassed to implement more advanced validations
        by *key* or target object *instance*.
        
        If you want users to vote only active objects, for instance, you can
        write inyour subclas::
        
            def allow_vote(self, request, instance, key):
                allowed = super(MyClass, self).allow_vote(request, instance, key)
                return allowed and instance.is_active
        
        If anonymous votes are allowed, this method checks for ip adresses too.
    
    .. py:method:: get_vote_form_class(self, request)
        
        Return the vote form class that will be used to handle voting.
        This method can be overridden by view-level passed form class.
    
    .. py:method:: get_vote_form_kwargs(self, request, instance, key)
    
        Return the optional kwargs used to instantiate the voting form.
    
    .. py:method:: pre_vote(self, request, vote)
    
        Called just before the vote is saved to the db, this method takes
        the *request* and the unsaved *vote* instance.
        
        The unsaved vote can be a brand new vote instance (without *id*)
        or an existing vote object the user want to change.
        
        Subclasses can use this method to check if the vote can be saved and,
        if necessary, block the voting process returning False.
        
        This method is called by a *signals.vote_will_be_saved* listener
        always attached to the handler.
        It's up to the developer if override this method or just connect
        another listener to the signal: the voting process is killed if 
        just one receiver returns False.
    
    .. py:method:: vote(self, request, vote)
    
        Save the vote to the database.
        Must return True if the *vote* was created, False otherwise.
        
        By default this method just does *vote.save()* and recalculates
        the related score (average, total, number of votes).
    
    .. py:method:: post_vote(self, request, vote, created)
    
        Called just after the vote is saved to the db.
        
        This method is called by a *signals.vote_was_saved* listener
        always attached to the handler.
    
    .. py:method:: pre_delete(self, request, vote)
    
        Called just before the vote is deleted from the db, this method takes
        the *request* and the *vote* instance.
        
        Subclasses can use this method to check if the vote can be deleted and,
        if necessary, block the vote deletion process returning False.
        
        This method is called by a *signals.vote_will_be_deleted* listener
        always attached to the handler.
        It's up to the developer if override this method or just connect
        another listener to the signal: the voting deletion process is killed 
        if just one receiver returns False.
    
    .. py:method:: delete(self, request, vote)
    
        Delete the vote from the database.
        
        By default this method just do *vote.delete()* and recalculates
        the related score (average, total, number of votes).
    
    .. py:method:: post_delete(self, request, vote)
    
        Called just after the vote is deleted to from db.
        
        This method is called by a *signals.vote_was_deleted* listener
        always attached to the handler.
    
    .. py:method:: success_response(self, request, vote)
    
        Callback used by the voting views, called when the user successfully
        voted. Must return a Django http response (usually a redirect, or
        some json if the request is ajax).
    
    .. py:method:: failure_response(self, request, errors)
    
        Callback used by the voting views, called when vote form did not 
        validate. Must return a Django http response.
        
    **Utility methods you may want to use in your python code**
    
    .. py:method:: has_voted(self, instance, key, user_or_cookies)
    
        Return True if the user related to given *user_or_cookies* has 
        voted the given target object *instance* using the given *key*.
        
        The argument *user_or_cookies* can be a Django User instance
        or a cookie dict (for anonymous votes).
        
        A *ValueError* is raised if you give cookies but anonymous votes 
        are not allowed by the handler.
    
    .. py:method:: get_vote(self, instance, key, user_or_cookies)
    
        Return the vote instance created by the user related to given 
        *user_or_cookies* for the target object *instance* using 
        the given *key*.
        
        The argument *user_or_cookies* can be a Django User instance
        or a cookie dict (for anonymous votes).
        
        Return None if the vote does not exists.
        
        A *ValueError* is raised if you give cookies but anonymous votes 
        are not allowed by the handler.
    
    .. py:method:: get_votes_for(self, instance, **kwargs)
    
        Return all votes given to *instance* and filtered by any given *kwargs*.
        All the content objects related to returned votes are evaluated
        together with votes.
        
    .. py:method:: get_votes_by(self, user, **kwargs)
    
        Return all votes assigned by *user* to model instances handled
        by this handler, and filtered by any given *kwargs*.
        All the content objects related to returned votes are evaluated
        together with votes.
    
    .. py:method:: get_score(self, instance, key)
    
        Return the score for the target object *instance* and the given *key*.
        Return None if the target object does not have a score.
    
    .. py:method:: annotate_scores(self, queryset, key, **kwargs)
    
        Annotate the *queryset* with scores using the given *key* and *kwargs*.
        
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
        
        This is basically a wrapper around *ratings.model.annotate_scores*.
    
    .. py:method:: annotate_votes(self, queryset, key, user, score='score')
    
        Annotate the *queryset* with votes given by the passed *user* using the 
        given *key*.
        
        The score itself will be present in the attribute named *score* of 
        each instance of the returned queryset.

        Usage example::

            for article in annotate_votes(Article.objects.all(), 'main', myuser, 
                score='myscore'):
                print 'your vote:', article.myscore
        
        This is basically a wrapper around *ratings.model.annotate_votes*.
        For anonymous voters this functionality is unavailable.
        
        
.. py:class:: Ratings

    Registry that stores the handlers for each content type rating system.

    An instance of this class will maintain a list of one or more models 
    registered for being rated, and their associated handler classes.

    To register a model, obtain an instance of *Ratings* (this module exports 
    one as *ratings*), and call its *register* method, passing the model class 
    and a handler class (which should be a subclass of *RatingHandler*). 
    Note that both of these should be the actual classes, not instances 
    of the classes.

    To cease ratings handling for a model, call the *unregister* method,
    passing the model class.

    For convenience, both *register* and *unregister* can also accept a list 
    of model classes in place of a single model; this allows easier 
    registration of multiple models with the same *RatingHandler* class.
    
    .. py:method:: register(self, model_or_iterable, handler_class=None, **kwargs)
    
        Register a model or a list of models for ratings handling, using a 
        particular *handler_class*, e.g.::
        
            from ratings.handlers import ratings, RatingHandler
            # register one model for rating
            ratings.register(Article, RatingHandler)
            # register other two models
            ratings.register([Film, Series], RatingHandler)
        
        If the handler class is not given, the default 
        *ratings.handlers.RatingHandler* class will be used.
        
        If *kwargs* are present, they are used to override the handler
        class attributes (using instance attributes), e.g.::
            
            ratings.register(Article, RatingHandler, 
                score_range=(1, 10), score_step=0.5)

        Raise *AlreadyHandled* if any of the models are already registered.
    
    .. py:method:: unregister(self, model_or_iterable)
    
        Remove a model or a list of models from the list of models that will
        be handled.

        Raise *NotHandled* if any of the models are not currently registered.
    
    .. py:method:: get_handler(self, model_or_instance)
    
        Return the handler for given model or model instance.
        Return None if model is not registered.
    
    .. py:method:: get_votes_by(self, user, **kwargs)
    
        Return all votes assigned by *user* and filtered by any given *kwargs*.
        All the content objects related to returned votes are evaluated
        together with votes.
