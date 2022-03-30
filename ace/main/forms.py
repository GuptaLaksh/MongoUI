from django import forms


class DatabaseForm(forms.Form):
    databaseName = forms.CharField(label='DatabaseName', max_length=100)
    collectionName = forms.CharField(label='CollectionName', max_length=100)
    dictionary = forms.CharField(
        label='Dictionary', widget=forms.Textarea(attrs={"rows": 10, "cols": 96, "wrap": "hard"}),required=False)
    myfile = forms.FileField(label='myfile', required=False)

class CollectionForm(forms.Form):
    collectionName = forms.CharField(label='CollectionName', max_length=100)
    dictionary = forms.CharField(
        label='Dictionary', widget=forms.Textarea(attrs={"rows": 10, "cols": 96, "wrap": "hard"}),required=False)
    myfile = forms.FileField(label='myfile', required=False)

class DocumentForm(forms.Form):
    dictionary = forms.CharField(
        label='Dictionary', widget=forms.Textarea(attrs={"rows": 10, "cols": 96, "wrap": "hard"}),required=False
    )
    myfile = forms.FileField(label='myfile', required=False)


class RenameForm(forms.Form):
    newname = forms.CharField(
        label='newname', widget=forms.Textarea(attrs={"rows": 10, "cols": 96, "wrap": "hard"})
    )


class SimpleQueryForm(forms.Form):
    key = forms.CharField(
        label='key', widget=forms.Textarea(attrs={"rows": 10, "cols": 10, "wrap": "hard"})
    )
    value = forms.CharField(
        label='value', widget=forms.Textarea(attrs={"rows": 10, "cols": 10, "wrap": "hard"})
    )


class AdvanceQueryForm(forms.Form):
    Query = forms.CharField(
        label='Query', widget=forms.Textarea(attrs={"rows": 10, "cols": 96, "wrap": "hard"})
    )
    Projection = forms.CharField(
        label='Projection', widget=forms.Textarea(attrs={"rows": 10, "cols": 96, "wrap": "hard"})
    )
