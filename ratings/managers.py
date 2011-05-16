from django.db import models
from django.utils.functional import memoize
from django.contrib.contenttypes.models import ContentType

_get_content_type_for_model_cache = {}

def get_content_type_for_model(model):
    return ContentType.objects.get_for_model(model)

get_content_type_for_model = memoize(get_content_type_for_model, 
    _get_content_type_for_model_cache, 1)


class ScoreManager(models.Manager):
    """
    Score manager.
    """
    def get_for(self, content_object, key):
        """
        Return the score instance for the target object *content_object* and 
        the given *key*. Return None if a score is not found.
        """
        content_type = get_content_type_for_model(type(content_object))
        try:
            return self.get(key=key, content_type=content_type, 
                object_id=content_object.pk)
        except self.model.DoesNotExist:
            return None
                
        
class VoteManager(models.Manager):
    """
    Vote manager.
    """
    def get_for(self, content_object, key, **kwargs):
        """
        Return the vote instance assigned to *content_object* and created by 
        *user* or *cookie* (at least one of those values must be present 
        in *kwargs*). Return None if a vote is not found.
        """
        content_type = get_content_type_for_model(type(content_object))
        try:
            return self.get(key=key, content_type=content_type, 
                object_id=content_object.pk, **kwargs)
        except self.model.DoesNotExist:
            return None
            
    def filter_for(self, content_object, **kwargs):
        """
        Return all the vote instances assigned to content_object and
        matching *kwargs*.
        """
        content_type = get_content_type_for_model(type(content_object))
        return self.filter(content_type=content_type, 
            object_id=content_object.pk, **kwargs)
            
    def filter_with_contents(self, **kwargs):
        """
        Return all vote instances taking content objects in bulk in order
        to minimize db queries, e.g. to get all objects voted by a user::
        
            for vote in Vote.objects.filter_with_contents(user=myuser):
                vote.content_object # this does not hit the db
        """
        objects = list(self.filter(**kwargs))
        generics = {}
        for i in objects:
            generics.setdefault(i.content_type_id, set()).add(i.object_id)
        content_types = ContentType.objects.in_bulk(generics.keys())
        relations = {}
        for content_type_id, pk_list in generics.items():
            model = content_types[content_type_id].model_class()
            relations[content_type_id] = model.objects.in_bulk(pk_list)
        for i in objects:
            setattr(i, '_content_object_cache', 
                relations[i.content_type_id][i.object_id])
        return objects
    