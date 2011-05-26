"""
Class based generic views.
These views are only available if you are using Django >= 1.3.
"""
from django.views.generic.detail import DetailView

from ratings.handlers import ratings

class VotedByView(DetailView):
    """
    Render a list of users that voted for a given object.
    """
    select_related = 'user'
    context_votes_name = 'votes'
    template_name_suffix = '_voted_by'
    
    def get_context_votes_name(self, obj):
        """
        Get the name to use for the votes.
        """
        return self.context_votes_name
        
    def get_votes(self, obj):
        """
        Return a queryset of votes given to *obj*.
        """
        handler = ratings.get_handler(obj)
        queryset = handler.get_votes_for(obj)
        if self.select_related:
            queryset = queryset.select_related(self.select_related)
        return queryset
        
    def get(self, request, **kwargs):
        self.object = self.get_object()
        self.votes = self.get_votes(self.object)
        kwargs = {
            'object': self.object,
            self.get_context_votes_name(self.object): self.votes,
        }
        context = self.get_context_data(**kwargs)
        response = self.render_to_response(context)
        # FIXME: try to avoid this workaround
        if hasattr(response, 'render') and callable(response.render):
            response.render()
        return response
