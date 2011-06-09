Templatetags reference
======================

In order to use the following templatetags you must 
``{% load ratings_tags %}`` in your template.


get_rating_form
~~~~~~~~~~~~~~~

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


get_rating_score
~~~~~~~~~~~~~~~~

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


scores_annotate
~~~~~~~~~~~~~~~

Use this templatetag when you need to update a queryset in bulk 
adding score values, e.g:

.. code-block:: html+django

    {% scores_annotate queryset with myaverage='average' using 'main' %}
    
After this call each queryset instance has a *myaverage* attribute
containing his average score for the key 'main'.
The score field name and the key can also be passed as 
template variables, without quotes, e.g.:

.. code-block:: html+django

    {% scores_annotate queryset with myaverage=average_var using key_var %}

You can also specify a new context variable for the modified queryset, e.g.:

.. code-block:: html+django

    {% scores_annotate queryset with myaverage='average' using 'main' as new_queryset %}
    {% for instance in new_queryset %}
        Average score: {{ instance.myaverage }}
    {% endfor %}
            
You can annotate a queryset with different score values at the same time, 
remembering that accepted values are 'average', 'total' and 'num_votes':

.. code-block:: html+django

    {% scores_annotate queryset with myaverage='average',num_votes='num_votes' using 'main' %}
    
Finally, you can also sort the queryset, e.g.:

.. code-block:: html+django

    {% scores_annotate queryset with myaverage='average' using 'main' ordering by '-myaverage' %}
    
The order of arguments is important: the following example shows how
to use this tempaltetag with all arguments:

.. code-block:: html+django

    {% scores_annotate queryset with myaverage='average',num_votes='num_votes' using 'main' ordering by '-myaverage' as new_queryset %}
    
The following example shows how to display in the template the ten most 
rated films (and how is possible to order the queryset using multiple fields):

.. code-block:: html+django
    
    {% scores_annotate films with avg='average',num='num_votes' using 'user_votes' ordering by '-avg,-num' as top_rated_films %}
    {% for film in top_rated_films|slice:":10" %}
        Film: {{ film }} 
        Average score: {{ film.avg }} 
        ({{ film.num }} vote{{ film.num|pluralize }})
    {% endfor %}
    
If the queryset's model is not handled, then this templatetag 
returns the original queryset.


get_rating_vote
~~~~~~~~~~~~~~~

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
current request will be returned. In this case, if user is anonymous
and the rating handler allows anonymous votes, current cookies
are used.

Having the vote model instance you can display vote info, as follows:

.. code-block:: html+django

    Vote: {{ vote.score }}
    Ip Address: {{ vote.ip_address }}

If the target object's model is not handled, or the given user did not
vote for that object, then the template variable will not be present 
in the context.


get_latest_votes_for
~~~~~~~~~~~~~~~~~~~~

Return (as a template variable in the context) the latest vote objects
given to a target object.

Usage:

.. code-block:: html+django

    {% get_latest_votes_for *target object* [using *key*] as *var name* %}
    
Usage example:

.. code-block:: html+django

    {% get_latest_votes_for object as latest_votes %}
    {% get_latest_votes_for content.instance using 'main' as latest_votes %}
    
In the following example we display latest 10 votes given to an *object*
using the 'by_staff' key:

.. code-block:: html+django

    {% get_latest_votes_for object uning 'mystaff' as latest_votes %}
    {% for vote in latest_votes|slice:":10" %}
        Vote by {{ vote.user }}: {{ vote.score }}
    {% endfor %}
    
The key can also be passed as a template variable (without quotes).
    
If you do not specify the key, then all the votes are taken regardless 
what key they have.


get_latest_votes_by
~~~~~~~~~~~~~~~~~~~

Return (as a template variable in the context) the latest vote objects
given by a user.

Usage:

.. code-block:: html+django

    {% get_latest_votes_by *user* [using *key*] as *var name* %}
    
Usage example:

.. code-block:: html+django

    {% get_latest_votes_by user as latest_votes %}
    {% get_latest_votes_for object.created_by using 'main' as latest_votes %}
    
In the following example we display latest 10 votes given by *user*
using the 'by_staff' key:

.. code-block:: html+django

    {% get_latest_votes_by user uning 'mystaff' as latest_votes %}
    {% for vote in latest_votes|slice:":10" %}
        Vote for {{ vote.content_object }}: {{ vote.score }}
    {% endfor %}
    
The key can also be passed as a template variable (without quotes).
    
If you do not specify the key, then all the votes are taken regardless 
what key they have.


votes_annotate
~~~~~~~~~~~~~~

Use this templatetag when you need to update a queryset in bulk 
adding vote values given by a particular user, e.g:

.. code-block:: html+django

    {% votes_annotate queryset with 'user_score' for myuser using 'main' %}
    
After this call each queryset instance has a *user_score* attribute
containing the score given by *myuser* for the key 'main'.
The score field name and the key can also be passed as 
template variables, without quotes, e.g.:

.. code-block:: html+django

    {% votes_annotate queryset with score_var for user using key_var %}

You can also specify a new context variable for the modified queryset, e.g.:

.. code-block:: html+django

    {% votes_annotate queryset with 'user_score' for user using 'main' as new_queryset %}
    {% for instance in new_queryset %}
        User's score: {{ instance.user_score }}
    {% endfor %}
            
Finally, you can also sort the queryset, e.g.:

.. code-block:: html+django

    {% votes_annotate queryset with 'myscore' for user using 'main' ordering by '-myscore' %}
    
The order of arguments is important: the following example shows how
to use this tempaltetag with all arguments:

.. code-block:: html+django

    {% votes_annotate queryset with 'score' for user using 'main' ordering by 'score' as new_queryset %}
    
Note: it is not possible to annotate querysets with anonymous votes.


show_starrating
~~~~~~~~~~~~~~~

Show the starrating widget in read-only mode for the given *score_or_vote*.
If *score_or_vote* is a score instance, then the average score is displayed.

Usage:

.. code-block:: html+django

    {# show star rating for the given vote #}
    {% show_starrating vote %}
    
    {# show star rating for the given score #}
    {% show_starrating score %}
    
    {# show star rating for the given score, using 10 stars with half votes #}
    {% show_starrating score 10 2 %}

Normally the handler is used to get the number of stars and the how each 
one must be splitted, but you can override using *stars* and *split*
arguments.
