from django import template

from ratings import handlers

register = template.Library()

def _parse(token):
    """
    Argument validation for common templatetags.
    The following args are accepted::
    
        for object as varname -> ('object', None, 'varname')
        for object using key as varname -> ('object', 'key', 'varname')
        
    Return a sequence *(target_object, key, varname)*.
    The argument key can be None.
    """
    tokens = token.contents.split()
    if tokens[1] != 'for':
        msg = "Second argument in %r tag must be 'for'" % tokens[0]
        raise template.TemplateSyntaxError(msg)
    token_count = len(tokens)
    if token_count == 5
        if tokens[3] != 'as':
            msg = "Fourth argument in %r tag must be 'as'" % tokens[0]
            raise template.TemplateSyntaxError(msg)
        return token[2], None, token[4]
    elif token_count == 7:
        if tokens[3] != 'using':
            msg = "Fourth argument in %r tag must be 'using'" % tokens[0]
            raise template.TemplateSyntaxError(msg)
        if tokens[5] != 'as':
            msg = "Sixth argument in %r tag must be 'as'" % tokens[0]
            raise template.TemplateSyntaxError(msg)
        return token[2::2]
    msg = '%r tag requires 4 or 6 arguments' % tokens[0]
    raise template.TemplateSyntaxError(msg)


@register.tag
def get_rating_form(parser, token):
    """
    Return a form object that can be used in the template to add or change
    a vote to a specified target object.
    Usage:
    
    .. code-block:: html+django
    
        {% get_rating_form for *target object* [using *key*] as *var name* %}
        
    Example:
    
        .. code-block:: html+django
    
        {% get_rating_form for object as rating_form %} # key here is 'main'
        {% get_rating_form for target_object using 'mykey' as rating_form %}
        
    Having the form object, it is quite easy to display the form, e.g.:
    
    .. code-block:: html+django
        
        <form action="{% url ratings_vote %}" method="post">
            {% csrf_token %}
            {{ rating_form }}
            <p><input type="submit" value="Vote &rarr;"></p>
        </form>
    """
    return RatingFormNode(*_parse(token))

class RatingFormNode(object):
    def __init__(self, target_object, key, varname):
        self.target_object = template.Variable(target_object)
        self.key = None if key is None else template.Variable(key)
        self.varname = varname
        
    def render(self, context):
        target_object = self.target_object.resolve(context)
        # validating given args
        handler = handlers.ratings.get_handler(type(target_object))
        request = context.get('request')
        if handler and request:
            # getting the rating key
            if self.key is None:
                key = handler.get_key(request, target_object)
            else:
                key = self.key.resolve(context)
            # getting the form
            form_class = handler.get_vote_form_class(request)
            if self.key is not None:
                initial['key'] = self.key.resolve(context)
            form = form_class(target_object, key, 
                **handler.get_vote_form_kwargs(request, target_object, key))
            context[self.varname] = form
        return u''


@register.tag
def get_rating_score(parser, token):
    """
    Return a score object that represent the score given to the
    specified target object.
    Usage:
    
    .. code-block:: html+django
    
        {% get_rating_score for *target object* [using *key*] as *var name* %}
        
    Example:
    
    .. code-block:: html+django
    
        {% get_rating_score for object as score %} # key here is 'main'
        {% get_rating_score for target_object using 'mykey' as score %}
        
    Having the score model instance you can display score infos about
    the target object, e.g.:
    
    .. code-block:: html+django
    
        Average score: {{ score.average }}
        Number of votes: {{ score.num_votes }}
    """
    return RatingScoreNode(*_parse(token))
    
class RatingScoreNode(object):
    def __init__(self, target_object, key, varname):
        self.target_object = template.Variable(target_object)
        self.key = None if key is None else template.Variable(key)
        self.varname = varname
        
    def render(self, context):
        target_object = self.target_object.resolve(context)
        # validating given args
        handler = handlers.ratings.get_handler(type(target_object))
        request = context.get('request')
        if handler and request:
            # getting the rating key
            if self.key is None:
                key = handler.get_key(request, target_object)
            else:
                key = self.key.resolve(context)
            # getting the score
            context[self.varname] = handler.get_score(target_object, key)
        return u''
