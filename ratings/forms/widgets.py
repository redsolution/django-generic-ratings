from decimal import Decimal

from django import forms
from django.template.loader import render_to_string

class SliderWidget(forms.TextInput):
    """
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
    """
    def __init__(self, min_value, max_value, step, can_delete_vote, 
        read_only=False, default='', template='ratings/slider_widget.html', 
        attrs=None):
        """
        The argument *default* is used when the initial value is None.
        """
        super(SliderWidget, self).__init__(attrs)
        self.min_value = min_value
        self.max_value = max_value
        self.step = step
        self.can_delete_vote = can_delete_vote
        self.read_only = read_only
        self.default = default
        self.template = template
    
    def get_context(self, name, value, attrs=None):
        attrs = attrs or {}
        attrs['type'] = 'hidden'
        return {
            'min_value': self.min_value,
            'max_value': self.max_value,
            'step': self.step,
            'can_delete_vote': self.can_delete_vote,
            'read_only': read_only,
            'default': self.default,
            'parent': super(SliderWidget, self).render(name, value, attrs),
            'parent_id': name,
            'value': value,
            'slider_id': 'slider-%s' % name,
            'label_id': 'slider-label-%s' % name,
            'remove_id': 'slider-remove-%s' % name,
        }
    
    def render(self, name, value, attrs=None):
        context = self.get_context(name, value, attrs)
        return render_to_string(self.template, context)
    
    
class StarWidget(forms.TextInput):
    """
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
    """
    def __init__(self, min_value, max_value, step, can_delete_vote,
        template='ratings/star_widget.html', attrs=None):
        super(StarWidget, self).__init__(attrs)
        self.min_value = min_value
        self.max_value = max_value
        self.step = step
        self.can_delete_vote = can_delete_vote
        self.template = template
        
    def _get_values(self, max_value, step=1):
        decimal_step = Decimal(str(step))
        value = Decimal('1')
        while value <= max_value:
            yield value
            value += decimal_step
    
    def get_context(self, name, value, attrs=None):
        attrs = attrs or {}
        attrs['type'] = 'hidden'
        split_value = int(1 / self.step)
        if split_value == 1:
            values = range(1, self.max_value+1)
            split = u''
        else:
            values = self._get_values(self.max_value, self.step)
            split = u' {split:%d}' % split_value
        return {
            'min_value': self.min_value,
            'max_value': self.max_value,
            'step': self.step,
            'can_delete_vote': self.can_delete_vote,
            'values': values,
            'split': split,
            'parent': super(StarWidget, self).render(name, value, attrs),
            'parent_id': name,
            'value': Decimal(str(value)),
            'star_id': 'star-%s' % name,
        }
                
    def render(self, name, value, attrs=None):
        context = self.get_context(name, value, attrs)
        return render_to_string(self.template, context)
