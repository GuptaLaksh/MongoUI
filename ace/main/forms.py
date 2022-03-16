
from django import forms


class DatabaseForm(forms.Form):
    databaseName = forms.CharField(label='DatabaseName', max_length=100)
    collectionName = forms.CharField(label='CollectionName', max_length=100)
    dictionary = forms.JSONField(label='Dictionary')
    #document = forms.JSONField(label='document')


class CollectionForm(forms.Form):
    collectionName = forms.CharField(label='CollectionName', max_length=100)
    dictionary = forms.JSONField(label='Dictionary')
    #document = forms.JSONField(label='document')
