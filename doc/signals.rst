Django signals
==============

.. py:module:: ratings.signals

.. py:attribute:: vote_will_be_saved

    **Providing args**: *vote*, *request*
    
    Fired before a vote is saved.
    
    Receivers can stop the vote process returning *False*.
    
    One receiver is always called: *handler.pre_vote*
    
----
    
.. py:attribute:: vote_was_saved

    **Providing args**: *vote*, *request*, *created*
    
    Fired after a vote is saved. 
    
    One receiver is always called: *handler.post_vote*.
    
----
    
.. py:attribute:: vote_will_be_deleted

    **Providing args**: *vote*, *request*
    
    Fired before a vote is deleted. 
    
    Receivers can stop the vote deletion process returning *False*.
    
    One receiver is always called: *handler.pre_delete*

----

.. py:attribute:: vote_was_deleted

    **Providing args**: *vote*, *request*
    
    Fired after a vote is deleted.
    
    One receiver is always called: *handler.post_delete*
