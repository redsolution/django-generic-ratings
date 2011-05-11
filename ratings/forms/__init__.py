import time

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.crypto import salted_hmac, constant_time_compare
from django.utils.encoding import force_unicode

from ratings import utils

class VoteForm(forms.Form):
    """
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
    """
    # rating data
    content_type  = forms.CharField(widget=forms.HiddenInput)
    object_pk = forms.CharField(widget=forms.HiddenInput)
    score = forms.IntegerField()
    key = forms.RegexField(regex=r'^[\w.+-]+$', widget=forms.HiddenInput,
        required=False)
    # security data
    timestamp = forms.IntegerField(widget=forms.HiddenInput)
    security_hash = forms.CharField(min_length=40, max_length=40, 
        widget=forms.HiddenInput)
    honeypot = forms.CharField(required=False, widget=forms.HiddenInput)
    
    def __init__(self, target_object, key, 
        score_range=None, score_decimals=None,
        data=None, initial=None):
        self.target_object = target_object
        self.key = key
        self.score_range = score_range
        self.score_decimals = score_decimals
        if initial is None:
            initial = {}
        initial.update(self.generate_security_data())
        super(VoteForm, self).__init__(data=data, initial=initial)
        
    # SECURITY
    
    def clean_security_hash(self):
        """
        Check the security hash.
        """
        security_hash_dict = {
            'content_type' : self.data.get('content_type', ''),
            'object_pk' : self.data.get('object_pk', ''),
            'key': self.data.get('key', ''),
            'timestamp' : self.data.get('timestamp', ''),
        }
        expected_hash = self.generate_security_hash(**security_hash_dict)
        actual_hash = self.cleaned_data["security_hash"]
        if not constant_time_compare(expected_hash, actual_hash):
            raise forms.ValidationError('Security hash check failed.')
        return actual_hash

    def clean_timestamp(self):
        """
        Make sure the timestamp isn't too far (> 2 hours) in the past.
        """
        timestamp = self.cleaned_data['timestamp']
        if time.time() - timestamp > (2 * 60 * 60):
            raise forms.ValidationError('Timestamp check failed')
        return timestamp
        
    def clean_honeypot(self):
        """
        Check that nothing's been entered into the honeypot.
        """
        value = self.cleaned_data["honeypot"]
        if value:
            raise forms.ValidationError('Your vote is spam. Shame on you!')
        return value

    def generate_security_data(self):
        """
        Generate a dict of security data for *initial* data.
        """
        timestamp = int(time.time())
        security_dict = {
            'content_type': str(self.target_object._meta),
            'object_pk': str(self.target_object._get_pk_val()),
            'key': str(self.key),
            'timestamp': str(timestamp),
            'security_hash': self.initial_security_hash(timestamp),
        }
        return security_dict

    def initial_security_hash(self, timestamp):
        """
        Generate the initial security hash from *self.target_object*
        and a (unix) timestamp.
        """
        initial_security_dict = {
            'content_type' : str(self.target_object._meta),
            'object_pk' : str(self.target_object._get_pk_val()),
            'key': str(self.key),
            'timestamp' : str(timestamp),
          }
        return self.generate_security_hash(**initial_security_dict)

    def generate_security_hash(self, content_type, object_pk, key, timestamp):
        """
        Generate a HMAC security hash from the provided info.
        """
        key_salt = "ratings.forms.VoteForm"
        value = "-".join((content_type, object_pk, key, timestamp))
        return salted_hmac(key_salt, value).hexdigest()
        
    # VOTE
    
    def clean_score(self):
        """
        If *score_range* was given to the form, then check if the 
        score is in range.
        Again, if *score_decimals* was given, then check for number
        of decimal places.
        """
        score = self.cleaned_data['score']
        # score range, if given is a tuple of min and max values for scores,
        # including the extremes
        if self.score_range:
            if not (self.score_range[0] <= score <= self.score_range[1]):
                raise forms.ValidationError('Score is not in range')
        # check decimal places
        if self.score_decimals:
            try:
                _, decimals = str(score).split('.')
            except ValueError:
                decimal_places = 0
            else:
                decimal_places = len(decimals)
            if decimal_places > self.score_decimals:
                raise forms.ValidationError('Invalid number of decimal places')
        return score
    
    def get_vote_model(self):
        """
        Return the vote model used to rate an object.
        """
        from ratings import models
        return models.Vote
        
    def get_vote_data(self, request, allow_anonymous):
        """
        Return two dicts of data to be used to look for a vote and to create 
        a vote. Subclasses in custom ratings apps that override 
        *get_vote_model* can override this method too to add extra 
        fields into a custom vote model.
        """
        content_type = ContentType.objects.get_for_model(self.target_object)
        key = self.cleaned_data["key"]
        data = {
            'content_type': content_type,
            'object_pk': self.target_object.pk,
            'key': self.cleaned_data["key"],
            'score': self.cleaned_data["score"],
            'ip_address': request.META.get("REMOTE_ADDR", None),
        }
        if allow_anonymous:
            cookie_name = utils.get_cookie_name(self.target_object, key)
            cookie_value = request.COOKIES.get(cookie_name)
            if cookie_value:   
                data['cookie'] = cookie_value
                # TODO: continuare
        elif request.user.is_authenticated():
            data['user'] = request.user
        else:
            # something went very wrong: if anonymous votes are not allowed
            # and the user is not authenticated the view should have blocked
            # the voting process
            raise utils.ForbiddenError('Unhandled exception: user cannot vote.')
        return data
        
    def get_vote(self, request, allow_anonymous):
        """
        Return a new (unsaved) vote object based on the information in this
        form. Assumes that the form is already validated and will throw a
        ValueError if not.
        
        The vote can be a brand new vote or a changed vote. If the vote is
        just created then the instance's id will be None.
        """
        if not self.is_valid():
            raise ValueError('get_vote may only be called on valid forms')
        # get vote model and data
        model = self.get_vote_model()
        data = self.get_vote_data(request, allow_anonymous)
        lookups = data.copy()
        score = lookups.pop('score')
        ip_address = lookups.pop('ip_address')
        if allow_anonymous:
            lookups['user__is_null'] = True
        else:
            lookups['cookie__isnull'] = True
        try:
            # trying to get an existing vote
            vote = model.objects.get(**lookups)
        except model.DoesNotExists:
            # create a brand new vote
            vote = model(**data)
        else:
            # we only have to change the score for existing vote
            vote.score = score
        # done
        return vote
        
    # DELETE
    
    def delete(self, request):
        """
        Return True if the form requests to delete the vote.
        By default check for a *delete_vote* key in POST data.
        """
        return 'delete_vote' in self.data and self.data['delete_vote']
