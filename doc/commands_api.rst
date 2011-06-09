Management commands reference
=============================

.. py:module:: ratings.management.commands.upsert_scores

.. py:class:: Command

    Create or update all scores, based on existing votes.
    This is useful if you have to migrate your votes from a legacy table,
    or you want to change the weight of current votes, e.g.::
    
        ./manage.y upsert_scores -w 5
