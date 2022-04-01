from django import forms


class DatabaseForm(forms.Form):
    databaseName = forms.CharField(label='DatabaseName', max_length=100)
    collectionName = forms.CharField(label='CollectionName', max_length=100)
    dictionary = forms.CharField(
        label='Dictionary', widget=forms.Textarea(attrs={"rows": 10, "cols": 96, "wrap": "hard"}), required=False)
    myfile = forms.FileField(label='myfile', required=False)


class CollectionForm(forms.Form):
    collectionName = forms.CharField(label='CollectionName', max_length=100)
    dictionary = forms.CharField(
        label='Dictionary', widget=forms.Textarea(attrs={"rows": 10, "cols": 96, "wrap": "hard"}), required=False)
    myfile = forms.FileField(label='myfile', required=False)


class DocumentForm(forms.Form):
    dictionary = forms.CharField(
        label='Dictionary', widget=forms.Textarea(attrs={"rows": 10, "cols": 96, "wrap": "hard"}), required=False
    )
    myfile = forms.FileField(label='myfile', required=False)


class RenameForm(forms.Form):
    newname = forms.CharField(
        label='newname', widget=forms.Textarea(attrs={"rows": 10, "cols": 96, "wrap": "hard"})
    )


FORMATS = [
    ('json', 'json'), ('csv', 'csv')
]


class ExportForm(forms.Form):
    options = forms.CharField(label='Which Format?',
                              widget=forms.Select(choices=FORMATS))


class QueryForm(forms.Form):
    key = forms.CharField(
        label='key', widget=forms.Textarea(attrs={"rows": 1, "cols": 50, "wrap": "hard", "placeholder": "key"}),  required=False
    )
    value = forms.CharField(
        label='value', widget=forms.Textarea(attrs={"rows": 1, "cols": 50, "wrap": "hard", "placeholder": "value"}),  required=False
    )
    query = forms.CharField(
        label='query', widget=forms.Textarea(attrs={"rows": 4, "cols": 50, "wrap": "hard", "placeholder": "query"}), required=False
    )
    projection = forms.CharField(
        label='projection', widget=forms.Textarea(attrs={"rows": 4, "cols": 50, "wrap": "hard", "placeholder": "projection"}), required=False
    )

