import re

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
    Return (as a template variable in the context) a form object that can be 
    used in the template to add, change or delete a vote for the 
    specified target object.
    Usage:
    
    .. code-block:: html+django
    
        {% get_rating_form for *target object* [using *key*] as *var name* %}
        
    Example:
    
        .. code-block:: html+django
    
        {% get_rating_form for object as rating_form %} # key here is 'main'
        {% get_rating_form for target_object using 'mykey' as rating_form %}
        
    The key can also be passed as a template variable (without quotes).
        
    If you do not specify the key, then the key is taken using the registered
    handler for the model of given *object*.
        
    Having the form object, it is quite easy to display the form, e.g.:
    
    .. code-block:: html+django
        
        <form action="{% url ratings_vote %}" method="post">
            {% csrf_token %}
            {{ rating_form }}
            <p><input type="submit" value="Vote &rarr;"></p>
        </form>
        
    If the target object's model is not handled, then the template variable 
    will not be present in the context.
    """
    return RatingFormNode(*_parse(token))

class RatingFormNode(object):
    def __init__(self, target_object, key, varname):
        self.target_object = template.Variable(target_object)
        # key
        self.key_variable = None
        if key is None:
            self.key = None
        elif key[0] in ('"', "'") and key[-1] == key[0]:
            self.key = key[1:-1]
        else:
            self.key_variable = template.Variable(key)
        # varname
        self.varname = varname
        
    def render(self, context):
        target_object = self.target_object.resolve(context)
        # validating given args
        handler = handlers.ratings.get_handler(type(target_object))
        request = context.get('request')
        if handler and request:
            # getting the rating key
            if self.key_variable:
                key = self.key_variable.resolve(context)
            elif self.key is None:
                key = handler.get_key(request, target_object)
            else:
                key = self.key            
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
    Return (as a template variable in the context) a score object 
    representing the score given to the specified target object.
    Usage:
    
    .. code-block:: html+django
    
        {% get_rating_score for *target object* [using *key*] as *var name* %}
        
    Example:
    
    .. code-block:: html+django
    
        {% get_rating_score for object as score %}
        {% get_rating_score for target_object using 'mykey' as score %}
        
    The key can also be passed as a template variable (without quotes).
    
    If you do not specify the key, then the key is taken using the registered
    handler for the model of given *object*.
    
    Having the score model instance you can display score info, as follows:
    
    .. code-block:: html+django
    
        Average score: {{ score.average }}
        Number of votes: {{ score.num_votes }}
    
    If the target object's model is not handled, then the template variable 
    will not be present in the context.
    """
    return RatingScoreNode(*_parse(token))
    
class RatingScoreNode(object):
    def __init__(self, target_object, key, varname):
        self.target_object = template.Variable(target_object)
        # key
        self.key_variable = None
        if key is None:
            self.key = None
        elif key[0] in ('"', "'") and key[-1] == key[0]:
            self.key = key[1:-1]
        else:
            self.key_variable = template.Variable(key)
        # varname
        self.varname = varname
        
    def render(self, context):
        target_object = self.target_object.resolve(context)
        # validating given args
        handler = handlers.ratings.get_handler(type(target_object))
        request = context.get('request')
        if handler and request:
            # getting the rating key
            if self.key_variable:
                key = self.key_variable.resolve(context)
            elif self.key is None:
                key = handler.get_key(request, target_object)
            else:
                key = self.key            
            # getting the score
            context[self.varname] = handler.get_score(target_object, key)
        return u''
        

GET_RATING_VOTE_PATTERN = r"""
    ^ # begin of line
    for\s+(?P<target_object>[\w.]+) # target object
    (\s+by\s+(?P<user>[\w.]+))? # user
    (\s+using\s+(?P<key>[\w'"]+))? # key
    \s+as\s+(?P<varname>\w+) # varname
    $ # end of line
"""
GET_RATING_VOTE_EXPRESSION = re.compile(GET_RATING_VOTE_PATTERN, re.VERBOSE)
        
@register.tag
def get_rating_vote(parser, token):
    """
    Return (as a template variable in the context) a vote object 
    representing the vote given to the specified target object by
    the specified user.
    Usage:
    
    .. code-block:: html+django
    
        {% get_rating_vote for *target object* [by *user*] [using *key*] as *var name* %}
        
    Example:
    
    .. code-block:: html+django
    
        {% get_rating_vote for object as vote %}
        {% get_rating_vote for target_object using 'mykey' as vote %}
        {% get_rating_vote for target_object by myuser using 'mykey' as vote %}
        
    The key can also be passed as a template variable (without quotes).
    
    If you do not specify the key, then the key is taken using the registered
    handler for the model of given *object*.
    
    If you do not specify the user, then the vote given by the user of 
    current request will be returned.
    
    Having the vote model instance you can display vote info, as follows:
    
    .. code-block:: html+django
    
        Vote: {{ vote.score }}
        Ip Address: {{ vote.ip_address }}
    
    If the target object's model is not handled, or the given user did not
    vote for that object, then the template variable will not be present 
    in the context.
    """
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        error = u"%r tag requires arguments" % token.contents.split()[0]
        raise template.TemplateSyntaxError, error
    # args validation
    match = GET_RATING_VOTE_EXPRESSION.match(arg)
    if not match:
        error = u"%r tag has invalid arguments" % tag_name
        raise template.TemplateSyntaxError, error
    return RatingVoteNode(**match.groupdict())
    
class RatingVoteNode(object):
    def __init__(self, target_object, user, key, varname):
        self.target_object = template.Variable(target_object)
        self.user_variable = template.Variable(user) if user else None
        # key
        self.key_variable = None
        if key is None:
            self.key = None
        elif key[0] in ('"', "'") and key[-1] == key[0]:
            self.key = key[1:-1]
        else:
            self.key_variable = template.Variable(key)
        # varname
        self.varname = varname
        
    def render(self, context):
        target_object = self.target_object.resolve(context)
        # validating given args
        handler = handlers.ratings.get_handler(type(target_object))
        request = context.get('request')
        if handler and request:
            # getting user
            if self.user_variable is None:
                user = request.user
            else:
                user = self.user_variable.resolve(context)
            # getting the rating key
            if self.key_variable:
                key = self.key_variable.resolve(context)
            elif self.key is None:
                key = handler.get_key(request, target_object)
            else:
                key = self.key            
            # getting the score
            context[self.varname] = handler.get_vote(target_object, key, 
                request=request, user=user)
        return u''
    
    
ANNOTATE_SCORES_PATTERN = r"""
    ^ # begin of line
    (?P<fields>[\w=,.'"]+) # fields mapping
    \s+in\s+(?P<queryset>\w+) # queryset
    \s+using\s+(?P<key>[\w'"]+) # key
    (\s+ordering\s+by\s+(?P<order_by>[\w\-'"]+))? # order
    (\s+as\s+(?P<varname>\w+))? # varname
    $ # end of line
"""
ANNOTATE_SCORES_EXPRESSION = re.compile(ANNOTATE_SCORES_PATTERN, re.VERBOSE)
 
@register.tag
def annotate_scores(parser, token):
    """
    Use *annotate_scores* when you need to update a queryset in bulk 
    adding score values, e.g:
    
    .. code-block:: html+django
    
        {% annotate_scores myaverage='average' in queryset using 'main' %}
        
    After this call each queryset instance has a *myaverage* attribute
    containing his average score for the key 'main'.
    The score field name and the key can also be passed as 
    template variables, without quotes, e.g.:
    
    .. code-block:: html+django
    
        {% rating_annotate myaverage=average_var in queryset using key_var %}
    
    You can also specify a new context variable for the modified queryset, e.g.:
    
    .. code-block:: html+django
    
        {% rating_annotate myaverage='average' in queryset using 'main' as new_queryset %}
        {% for instance in new_queryset %}
            Average score: {{ instance.myaverage }}
        {% endfor %}
                
    You can annotate different score values at the same time, remembering 
    that accepted values are 'average', 'total' and 'num_votes', e.g.:
    
    .. code-block:: html+django
    
        {% rating_annotate myaverage='average',num_votes='num_votes' in queryset using 'main' %}
        
    Finally, you can also sort the queryset, e.g.:
    
    .. code-block:: html+django
    
        {% rating_annotate myaverage='average' in queryset using 'main' ordering by '-myaverage' %}
        
    The order of arguments is important: the following example shows how
    to use this tempaltetag with all arguments:
    
    .. code-block:: html+django
    
        {% rating_annotate myaverage='average',num_votes='num_votes' in queryset using 'main' ordering by '-myaverage' as new_queryset %}
        
    The following example shows how to display in the template the ten most 
    rated films (and how is possible to order the queryset using multiple fields):
    
    .. code-block:: html+django
        
        {% rating_annotate avg='average',num='num_votes' in films using 'user_votes' ordering by '-avg,-num' as top_rated_films %}
        
    If the queryset's model is not handled, then this templatetag 
    returns the original queryset.
    """
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        error = u"%r tag requires arguments" % token.contents.split()[0]
        raise template.TemplateSyntaxError, error
    # args validation
    match = ANNOTATE_SCORES_EXPRESSION.match(arg)
    if not match:
        error = u"%r tag has invalid arguments" % tag_name
        raise template.TemplateSyntaxError, error
    kwargs = match.groupdict()
    # fields validation
    fields = kwargs.pop('fields')
    try:
        fields_map = dict(i.split("=") for i in fields.split(","))
    except (TypeError, ValueError):
        error = u"%r tag has invalid field arguments" % tag_name
        raise template.TemplateSyntaxError, error
    # to the node
    return AnnotateScoresNode(fields_map, **kwargs)

class AnnotateScoresNode(object):
    def __init__(self, fields_map, queryset, key, order_by, varname):
        # fields
        self.fields_map = {}
        for k, v in fields_map.items():
            data = {'value': None, 'variable': None}
            if v[0] in ('"', "'") and v[-1] == v[0]:
                data['value'] = v[1:-1]
            else:
                data['variable'] = template.Variable(v)
            self.fields_map[k] = data
        # queryset
        self.queryset = template.Variable(queryset)
        # key
        self.key_variable = None
        if key[0] in ('"', "'") and key[-1] == key[0]:
            self.key = key[1:-1]
        else:
            self.key_variable = template.Variable(key)
        # ordering
        self.order_by_variable = None
        if order_by is None:
            self.order_by = None
        elif order_by[0] in ('"', "'") and order_by[-1] == order_by[0]:
            self.order_by = order_by[1:-1]
        else:
            self.order_by = template.Variable(order_by)
        # varname
        self.varname = varname or queryset
        
    def render(self, context):
        # fields
        fields_map = {}
        for k, v in self.fields_map.items():
            if v['variable'] is None:
                fields_map[k] = v['value']
            else:
                fields_map[k] = v['variable'].resolve(context)
        # queryset
        queryset = self.queryset.resolve(context)
        # handler
        handler = handlers.ratings.get_handler(queryset.model)
        # if model is not handled the original queryset is returned
        if handler is not None:
            # key
            if self.key_variable is None:
                key = self.key
            else:
                key = self.key_variable.resolve(context)
            # annotation
            queryset = handler.annotate_scores(queryset, key, **fields_map)
            # ordering
            if self.order_by_variable:
                queryset = queryset.order_by(
                    *self.order_by_variable.resolve(context).split(','))
            elif self.order_by is not None:
                queryset = queryset.order_by(*self.order_by.split(','))
        # returning queryset
        context[self.varname] = queryset
        return u''


# TODO: annotate_user_votes