Getting started
===============

Requirements
~~~~~~~~~~~~

======  ======
Python  >= 2.5
Django  >= 1.0
======  ======

Installation
~~~~~~~~~~~~

The Mercurial repository of the application can be cloned with this command::

    # TODO hg clone https://django-endless-pagination.googlecode.com/hg/ django-endless-pagination

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

Add the ratings urls to your *urls.py*, e.g.::
    
    (r'^ratings/', include('ratings.urls')),

Quickstart
~~~~~~~~~~

Having a template like this:

.. code-block:: html+django

    {% for object in objects %}
        {# your code to show the entry #}
    {% endfor %}
    
You can use Digg-style pagination to display objects just adding:

.. code-block:: html+django

    {% load endless %}
    
    {% paginate objects %}
    {% for object in objects %}
        {# your code to show the entry #}
    {% endfor %}
    {% show_pages %}
    
Done.