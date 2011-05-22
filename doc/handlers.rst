Using handlers
==============

As seen in :doc:`getting_started`, a model instance can be voted and can have
an associated score only if its model class is handled. Being handled, for
a model, means it is registered with an handler.

We have seen how to do that::

    from ratings.handlers import ratings
    ratings.register(Film)
    
The handler class is an optional argument of the ``ratings.register`` method,
and, if not provided, the default ``ratings.handlers.RatingHandler`` handler is
used

The previous code can be written::

    from ratings.handlers import ratings, RatingHandler
    ratings.register(Film, RatingHandler)

For convenience, ``ratings.register`` can also accept a list 
of model classes in place of a single model; this allows easier 
registration of multiple models with the same handler class, e.g.::

    from ratings.handlers import ratings, RatingHandler
    ratings.register([Film, Series], RatingHandler)
    
Where should this code live?
You can register handlers anywhere you like. However, you'll need to make sure 
that the module it's in gets imported early on so that the model gets registered 
before any voting is performed or rating is requested. 
This makes your app's *models.py* a good place to put the above code.

The default rating handler provides only one 1-5 ranged (without decimal places) 
score for each content object, and allows voting only for authenticated users.
It also allows user to delete and change their vote.

We can, however, override some options while registering the model. 
For instance, if we want 1-10 ranged votes with a step of 0.5 (half votes), and 
we don't want users to delete their votes, we can give these options as *kwargs*::

    from ratings.handlers import ratings, RatingHandler
    ratings.register(Film, RatingHandler, 
        score_range=(1, 10), score_step=0.5, can_delete_vote=False)
        
The handler manages the voting form too, and, by default the widget used 
to render the score is a simple text input.
If you want to use the more cool star rating widget, you can do::

    from ratings.handlers import ratings
    from ratings.forms import StarVoteForm
    ratings.register(Film, form_class=StarVoteForm)
        
For a list of all available built-in options, see :doc:`handlers_api`.

However, there are situations where the built-in options are not sufficient.

What if, for instance, you want only active objects to be voted for a 
given model?
As in Django own ``contrib.admin.ModelAdmin``, you can write subclasses of 
``RatingHandler`` to override the methods which actually perform the voting 
process, and apply any logic they desire.

Here is an example meeting the staff users needs::

    from ratings.handlers import ratings, RatingHandler
    
    class MyHandler(RatingHandler):
       def allow_vote(self, request, instance, key):
           allowed = super(MyHandler, self).allow_vote(request, instance, key)
           return allowed and instance.is_active
           
    ratings.register(Film, MyHandler)
           
In the above example, the ``allow_vote`` method is called before any voting
attempt, and takes the current *request*, the *instance* being voted and
a *key*.

The *key* is a string representing the type of rating we are giving to an
object. For example, the same film can be associated with multiple types of 
rating (e.g. a score for the photography, one for the direction, one for 
the music, and so on): a user can vote the music or the direction, so the 
*key* can be used to distinguish music from direction. In fact, the *key* can
even be the string ``'music'`` or the string ``'direction'``.

The default *key* is ``'main'``. 
Don't worry: we will talk more about rating keys in :doc:`usage_examples`.


Handlers API
~~~~~~~~~~~~

Handlers are not only used to manage and customize the voting process, but also
grant a simplified access to the underneath Django models api.

First, we have to obtain the handler instance associated with our model::

    from ratings.handlers import ratings
    handler = ratings.get_handler(Film)
    
The method ``ratings.get_handler`` returns None if model is not registered, and 
can take a model instance too::

    from ratings.handlers import ratings
    film = Film.objects.latest()
    handler = ratings.get_handler(film)
    
What we can do with the handler?
For instance, we can get the ``'main'`` score or our *film*::

    score = handler.get_score(film, 'main')
    
    if score:
        print 'Average score:', score.average
        print 'Number of votes:', score.num_votes
        print 'Total score:', score.total
    else:
        print u'Nobody voted %s' % film

Or we can check if current user has voted our *film*::

    voted = handler.has_voted(film, 'main', request.user)
    
See :doc:`handlers_api` for a detailed explanation of other utility methods
of handlers, and of ``ratings.handlers.ratings`` registry too.
And in :doc:`models_api` you will find the lower level Django model's API.

It could be clear now that the rating handler is a layer of abstraction above 
Django models and forms, and handlers are used by templatetags and views too.
This way, building our own handlers means we can customize the behaviour
of the entire application.

Before going to see the :doc:`handlers_api`, maybe it is better to take a look
at some :doc:`usage_examples`.
