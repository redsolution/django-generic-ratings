Django Generic Ratings
======================

This application provides rating functionality to a Django project.

You can handle scores and number of votes for each content type
without adding additional fields to your models.

Different vote types can be associated to a single content object, and you
can write rules and business logic in a customized rating handler describing 
how a model instance can be voted.

This app provides *jQuery* based widgets, useful for increasing the voting 
experience of users (e.g.: slider rating, star rating).

The source code for this app is hosted on 
https://bitbucket.org/frankban/django-generic-ratings

Contents:

.. toctree::
   :maxdepth: 2
   
   getting_started
   handlers
   usage_examples
   customization
   signals
   templatetags_api
   handlers_api
   forms_api
   models_api
   commands_api
