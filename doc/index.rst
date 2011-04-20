Django Generic Ratings
======================

Tis application provides rating functionality to a Django project.

You can handle scores and number of votes for each content type
without adding additional fields to your models.

Different vote types can be associated to a single content object, and you
can write rules and business logic as an handler describing how a 
model instance can be voted.

This app comes with jquery based widgets, useful for increasing the voting 
experience of users (e.g.: slider rating, star rating).

This app can be used to provide Twitter-style or Digg-style pagination, with
optional AJAX support and other features like multiple or lazy pagination.

The source code for this app is hosted on 
# TODO http://code.google.com/p/django-endless-pagination/.

Contents:

.. toctree::
   :maxdepth: 2
   
   getting_started
   rating_handlers
   model_api
   user_ratings
   templatetags
   customization
