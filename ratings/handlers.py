

class RatingHandler(object):
    """
    Default handler for content ratings.
    """
    use_cookies = False
    vote_range = range(1, 11)
    vote_decimals = 1
    model = None
    
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
            
    def get_key(self, request, instance):
        pass
            
    def allow(self, request, score, instance, key):
        pass
            
    def has_voted(self, request, instance, key):
        pass
        
    def vote(self, request, score, instance, key):
        pass
        
    def delete_vote(self, request, instance, key):
        pass
        
    def score_for(self, instance, key):
        pass
        
    def get_vote_by(self, request, instance, key):
        pass