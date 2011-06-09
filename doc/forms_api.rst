Forms and widgets reference
===========================

The application provides some forms and widgets, useful for managing
the vote action using different methods (e.g. star  rating, slider rating).

Of course you can subclass the provided forms and widget in order to create
your custom vote methods.

The base vote forms, if the handler allows it, are used for vote deletion too.

You can take a look at :doc:`usage_examples` for an explanation of how to 
use AJAX with forms.

Forms
~~~~~

.. py:module:: ratings.forms

.. py:class:: VoteForm(forms.Form)

    Form class to handle voting of content objects.
    
    You can customize the app giving a custom form class, following
    some rules:
        
        - the form must define the *content_type* and *object_pk* fields
        - the form's *__init__* method must take as first and second positional
          arguments the target object getting voted and the ratings key
        - the form must define the *get_vote* method, getting the request and
          a boolean *allow_anonymous* and returning an unsaved instance of 
          the vote model
        - the form must define the *delete* method, getting the request and
          returning True if the form requests the deletion of the vote
          
    .. py:method:: get_score_field(self, score_range, score_step, can_delete_vote)
    
        Return the score field.
        Subclasses may ovveride this method in order to change 
        the field used to store score value.
    
    .. py:method:: get_score_widget(self, score_range, score_step, can_delete_vote)
    
        Return the score widget.
        Subclasses may ovveride this method in order to change 
        the widget used to display score input.
    
    .. py:method:: get_vote(self, request, allow_anonymous)
    
        Return an unsaved vote object based on the information in this form. 
        Assumes that the form is already validated and will throw a
        ValueError if not.
        
        The vote can be a brand new vote or a changed vote. If the vote is
        just created then the instance's id will be None.
    
    .. py:method:: get_vote_model(self)
        
        Return the vote model used to rate an object.
    
    .. py:method:: get_vote_data(self, request, allow_anonymous)
    
        Return two dicts of data to be used to look for a vote and to create 
        a vote. 
        
        Subclasses in custom ratings apps that override *get_vote_model* can 
        override this method too to add extra fields into a custom vote model.
        
        If the first dict is None, then the lookup is not performed.
    
    .. py:method:: delete(self, request)
    
        Return True if the form requests to delete the vote.
    

.. py:class:: SliderVoteForm(VoteForm)

    Handle voting using a slider widget.
    
    In order to use this form you must load the jQuery.ui slider
    javascript.
    
    This form triggers the following javascript events:
    
    - *slider_change* with the vote value as argument
      (fired when the user changes his vote)
    - *slider_delete* without arguments
      (fired when the user deletes his vote)
      
    It's easy to bind these events using jQuery, e.g.::
    
        $(document).bind('slider_change', function(event, value) {
            alert('New vote: ' + value);
        });


.. py:class:: StarVoteForm(VoteForm)

    Handle voting using a star widget.
    
    In order to use this form you must download the 
    jQuery Star Rating Plugin available at
    http://www.fyneworks.com/jquery/star-rating/#tab-Download
    and then load the required javascripts and css, e.g.::
    
        <link href="/path/to/jquery.rating.css" rel="stylesheet" type="text/css" />
        <script type="text/javascript" src="/path/to/jquery.MetaData.js"></script>
        <script type="text/javascript" src="/path/to/jquery.rating.js"></script>
        
    This form triggers the following javascript events:
    
    - *star_change* with the vote value as argument
      (fired when the user changes his vote)
    - *star_delete* without arguments
      (fired when the user deletes his vote)
      
    It's easy to bind these events using jQuery, e.g.::
    
        $(document).bind('star_change', function(event, value) {
            alert('New vote: ' + value);
        });
        

Widgets
~~~~~~~

.. py:module:: ratings.forms.widgets

.. py:class:: SliderWidget(BaseWidget)

    Slider widget.
    
    In order to use this widget you must load the jQuery.ui slider
    javascript.
    
    This widget triggers the following javascript events:
    
    - *slider_change* with the vote value as argument
      (fired when the user changes his vote)
    - *slider_delete* without arguments
      (fired when the user deletes his vote)
      
    It's easy to bind these events using jQuery, e.g.::
    
        $(document).bind('slider_change', function(event, value) {
            alert('New vote: ' + value);
        });


.. py:class:: StarWidget(BaseWidget)
    
    Starrating widget.
    
    In order to use this widget you must download the 
    jQuery Star Rating Plugin available at
    http://www.fyneworks.com/jquery/star-rating/#tab-Download
    and then load the required javascripts and css, e.g.::
    
        <link href="/path/to/jquery.rating.css" rel="stylesheet" type="text/css" />
        <script type="text/javascript" src="/path/to/jquery.MetaData.js"></script>
        <script type="text/javascript" src="/path/to/jquery.rating.js"></script>
        
    This widget triggers the following javascript events:
    
    - *star_change* with the vote value as argument
      (fired when the user changes his vote)
    - *star_delete* without arguments
      (fired when the user deletes his vote)
      
    It's easy to bind these events using jQuery, e.g.::
    
        $(document).bind('star_change', function(event, value) {
            alert('New vote: ' + value);
        });
