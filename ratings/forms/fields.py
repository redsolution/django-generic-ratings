from django import forms

from ratings.forms import widgets

class SliderField(forms.FloatField):
    """
    Score field showing a slider to the user.
    """
    pass
    # TODO: SliderField
    
    
class StarField(forms.FloatField):
    """
    Score field implemnting starrating.
    """
    pass
    # TODO: StarField