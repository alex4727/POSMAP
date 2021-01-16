from django import forms
from .models import Place, Pool
from bootstrap_datepicker_plus import DatePickerInput, TimePickerInput, DateTimePickerInput
from functools import partial
from django.core.exceptions import ValidationError
from django.utils import timezone

class AddJoinForm(forms.Form):
    number = forms.IntegerField(min_value=0, max_value=4)
    load = forms.IntegerField(min_value=0, max_value=4)

class AddPoolForm(forms.ModelForm):
    def clean_departure_date(self):
        departure_date = self.cleaned_data['departure_date']
        print(departure_date < timezone.now())
        if departure_date < timezone.now():
            raise ValidationError("Start date should be before end date.")
        return departure_date

    class Meta:
        model = Pool
        fields = ['place', 'load', 'number', 'departure_date']
        widgets = {
            'departure_date': DateTimePickerInput(format='%Y-%m-%d %H:%M'),
        }

class SearchTimeForm(forms.Form):
    from_date = forms.DateTimeField(input_formats=['%Y-%m-%d %H:%M'], widget=DateTimePickerInput(format='%Y-%m-%d %H:%M'))
    to_date = forms.DateTimeField(input_formats=['%Y-%m-%d %H:%M'], widget=DateTimePickerInput(format='%Y-%m-%d %H:%M'))

class AddPlaceForm(forms.Form):
    name = forms.CharField(max_length=200)
    address = forms.CharField(max_length=200)
    latitude = forms.FloatField()
    longitude = forms.FloatField()
