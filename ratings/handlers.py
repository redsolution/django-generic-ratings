from django.db.models.base import ModelBase

from ratings import models, forms, exceptions

class RatingHandler(object):
    """
    Encapsulates content rating options for a given model.
    
    This class can be subclassed to specify different behaviour and options
    for ratings of a given model, but can also be used directly, just to
    handle default rating for any model. 
    
    The default rating provide only one 0-10 ranged (without decimal places) 
    score for each content object, and allows voting only for authenticated
    users.
    
    # TODO: descriptions of all attributes and methods
    """
    use_cookies = False
    score_range = range(0, 11)
    vote_decimals = 0
    default_key = 'main'
    
    def __init__(self, model):
        self.model = model
            
    def get_key(self, request, instance):
        """
        Return the ratings key to be used to save the vote.

        Subclasses of this handler can define multiple keys to be used
        depending on given *request* or, more probably, on the given
        *instance* (the target object being voted).
        """
        return default_key
    
    # voting
        
    def get_vote_form_class(self, request):
        """
        Return the vote form class that will be used to handle voting.
        
        This method can be overridden by view-level passed form class.
        """
        return forms.VoteForm
        
    def get_vote_form_kwargs(self, request):
        """
        Return the optional kwargs used to instantiate the voting form.
        """
        return {'score_range': self.score_range}
            
    def allow_vote(self, request, vote):
        return True
        
    def vote(self, request, vote):
        pass
        
    def post_vote(self, request, vote):
        pass
        
    # deleting vote
    
    def get_vote_form_class(self, request):
        """
        Return the vote form class that will be used to handle voting.
        
        This method can be overridden by view-level passed form class.
        """
        return forms.VoteForm
        
    def allow_delete_vote(self, request, vote):
        return True
        
    def delete_vote(self, request, vote):
        pass
        
    def post_delete_vote(self, request, vote):
        pass
    
    # utils
            
    def has_voted(self, request, instance, key):
        pass
                
    def score_for(self, instance, key):
        pass
        
    def get_vote_by(self, request, instance, key):
        pass
        
        
class Ratings(object):
    """
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
    """
    def __init__(self):
        self._registry = {}
        self.connect()

    def connect(self):
        """
        Pre and post vote signals.
        """
        signals.content_will_be_voted.connect(self.pre_vote, sender=models.Vote)
        signals.content_was_voted.connect(self.post_vote, sender=models.Vote)

    def register(self, model_or_iterable, handler_class):
        """
        Register a model or a list of models for ratings handling, using a 
        particular *handler_class*.

        Raise *AlreadyHandled* if any of the models are already registered.
        """
        if isinstance(model_or_iterable, ModelBase):
            model_or_iterable = [model_or_iterable]
        for model in model_or_iterable:
            if model in self._registry:
                raise exceptions.AlreadyHandled(
                    "The model '%s' is already being handled" % 
                    model._meta.module_name)
            self._registry[model] = handler_class(model)

    def unregister(self, model_or_iterable):
        """
        Remove a model or a list of models from the list of models that will
        be handled.

        Raise *NotHandled* if any of the models are not currently registered.
        """
        if isinstance(model_or_iterable, ModelBase):
            model_or_iterable = [model_or_iterable]
        for model in model_or_iterable:
            if model not in self._registry:
                raise exceptions.NotHandled(
                    "The model '%s' is not currently being handled" % 
                    model._meta.module_name)
            del self._registry[model]
            
    def get_handler(self, model):
        """
        Return the handler for *model* 
        Return None if model is unregistered.
        """
        return self._registry[model] if model in self._registry else None

    def pre_vote(self, sender, vote, request, **kwargs):
        """
        Apply any necessary pre-save ratings steps to new votes.
        """
        model = vote.content_type.model_class()
        if model not in self._registry:
            return False
        return self._registry[model].allow_vote(request, vote)

    def post_vote(self, sender, vote, request, **kwargs):
        """
        Apply any necessary post-save ratings steps to new votes.
        """
        model = vote.content_type.model_class()
        if model not in self._registry:
            return
        return self._registry[model].post_vote(request, vote)


# import this instance in your code to use in registering models for ratings
ratings = Ratings()
