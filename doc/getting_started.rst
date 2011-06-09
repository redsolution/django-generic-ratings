Getting started
===============

Requirements
~~~~~~~~~~~~

======  ======
Python  >= 2.5
Django  >= 1.0
======  ======

jQuery >= 1.4 is required if you want to take advantage of *AJAX* voting,
or if you want to use customized rating methods like slider rating or star rating.
This application, out of the box, provides widgets for these kind of rating user
interfaces (see :doc:`forms_api`).

Installation
~~~~~~~~~~~~

The Mercurial repository of the application can be cloned with this command::

    hg clone https://frankban@bitbucket.org/frankban/django-generic-ratings

The ``ratings`` package, included in the distribution, should be
placed on the ``PYTHONPATH``.

Otherwise you can just ``pip install django-generic-ratings``.

Settings
~~~~~~~~

Add the request context processor in your *settings.py*, e.g.::
    
    from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS
    TEMPLATE_CONTEXT_PROCESSORS += (
         'django.core.context_processors.request',
    )
    
Add ``'ratings'`` to the ``INSTALLED_APPS`` in your *settings.py*.

See :doc:`customization` section in this documentation for other settings options.
However, in settings you can define global application options valid for all
handled models (i. e. models whose instances can be voted), but it is easy
to customize rating options for each handled models (see :doc:`handlers`).

Add the ratings urls to your *urls.py*, e.g.::
    
    (r'^ratings/', include('ratings.urls')),
    
Time to create the needed database tables using *syncdb* management command::

    ./manage.py syncdb

Quickstart
~~~~~~~~~~

First, you have to tell to the system that your model can be voted and that
its instances have a rating. 

For instance, having a *Film* model::

    from ratings.handlers import ratings
    ratings.register(Film)
    
The *Film* model is now handled, and, by default, if you didn't customize things
in your settings file, only authenticated users can vote films using 
1-5 ranged scores (without decimal places).
See :doc:`handlers` for an explanation of how to change rating options
and how to define a custom rating handler.

Now it's time to let your users vote a film, e.g.:

.. code-block:: html+django

    {% load ratings_tags %}
    
    {% get_rating_form for film as rating_form %}
    
    <form action="{% url ratings_vote %}" method="post">
        {% csrf_token %}
        {{ rating_form }}
        <p><input type="submit" value="Vote &rarr;"></p>
    </form>
    
And why not to display current score for our film?

.. code-block:: html+django
    
    {% load ratings_tags %}
    
    {% get_rating_score for film as score %}
    
    {% if score %}
        Average score: {{ score.average|floatformat }}
        Number of votes: {{ score.num_votes }}
    {% else %}
        How sad: nobody voted {{ film }}
    {% endif %}

This application provides templatetags to get a vote by a given user, to annotate
a queryset with scores and votes, to get the latest votes given to an object
or by a user, and so on: see :doc:`templatetags_api` for a detailed explanation of
provided templatetags.

Anyway, you may want to take a look at :doc:`handlers` first.
