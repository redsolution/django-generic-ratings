from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.db.models import get_model
from django import http

from ratings import handlers, signals

def vote(request, extra_context=None, form_class=None):
    """
    Vote view: this view is available only if request's method is POST.
    """
    if request.method == 'POST':
        
        # first superficial post data validation
        content_type = request.POST.get('content_type')
        object_pk = request.POST.get('object_pk')
        if content_type is None or object_pk is None:
            # no content type an object id, no party
            return http.HttpResponseBadRequest('Missing required fields.')
        
        # getting current model and rating handler
        model = get_model(*content_type.split('.'))
        handler = handlers.ratings.get_handler(model)
        if handler is None:
            # bad or unregistered content type, bad request
            return http.HttpResponseBadRequest('Bad or unregistered content type.')
        
        # current target object getting voted
        try:
            target_object = model.objects.get(pk=object_pk)
        except model.DoesNotExist:
            return http.HttpResponseBadRequest('Invalid target object.')
        
        # getting the ratings key
        key = handler.get_key(request, target_object)
        
        # getting the form
        form_class = form_class or handler.get_vote_form_class(requests)
        form = form_class(target_object, key, data=request.POST, 
            **handler.get_vote_form_kwargs(request))
        
        if form.is_valid():
        
            # getting unsaved vote
            vote = form.get_vote(request)
        
            # pre-vote signal: listeners can stop the vote process
            # note: one listener is always called: *handler.allow_vote*
            # handler can disallow the vote
            responses = signals.content_will_be_voted.send(
                sender=vote.__class__, 
                vote=vote, request=request)
        
            # if one of the listeners reurns False then voting must be killed
            for receiver, response in responses:
                if response == False:
                    return http.HttpResponseBadRequest(
                        'Listener %r killed the voting process' % 
                        receiver.__name__)
        
            # actually save the vote
            handler.vote(request, vote)
        
            # post-vote signal
            # note: one listener is always called: *handler.post_vote*
            signals.content_was_voted.send(sender=vote.__class__, 
                vote=vote, request=request)
        
            # redirect
            # TODO
            
        # form is not valid: must handle errors
        # TODO
        
    # only answer POST requests
    return http.HttpResponseForbidden('Forbidden.')
        
