from django import forms
from django.template.loader import render_to_string

class SliderWidget(forms.TextInput):
    """
    Slider widget.
    """
    def __init__(self, min_value, max_value, step, 
        default='', template='ratings/slider_widget.html', attrs=None):
        """
        The argument *default* is used when the initial value is None.
        """
        super(SliderWidget, self).__init__(attrs)
        self.min_value = min_value
        self.max_value = max_value
        self.step = step
        self.default = default
        self.template = template
    
    def render(self, name, value, attrs=None):
        attrs = attrs or {}
        attrs['type'] = 'hidden'
        context = {
            'min_value': self.min_value,
            'max_value': self.max_value,
            'step': self.step,
            'default': self.default,
            'parent': super(SliderWidget, self).render(name, value, attrs),
            'parent_id': name,
            'value': value,
            'slider_id': 'slider-%s' % name,
            'label_id': 'slider-label-%s' % name,
        }
        return render_to_string(self.template, context)
    
    
class StarWidget(forms.TextInput):
    """
    Starrating widget.
    """
    pass
    # TODO: StarWidget
