from django import forms


class DatabaseForm(forms.Form):
    databaseName = forms.CharField(label='DatabaseName', max_length=100)
    collectionName = forms.CharField(label='CollectionName', max_length=100)
    dictionary = forms.CharField(
        label='Dictionary', widget=forms.Textarea(attrs={"rows": 15, "cols": 169, "wrap": "hard"}), required=False)
    myfile = forms.FileField(label='myfile', required=False)


class CollectionForm(forms.Form):
    collectionName = forms.CharField(label='CollectionName', max_length=100)
    dictionary = forms.CharField(
        label='Dictionary', widget=forms.Textarea(attrs={"rows": 15, "cols": 169, "wrap": "hard"}), required=False)
    myfile = forms.FileField(label='myfile', required=False)


class DocumentForm(forms.Form):
    dictionary = forms.CharField(
        label='Dictionary', widget=forms.Textarea(attrs={"rows": 15, "cols": 169, "wrap": "hard"}), required=False
    )
    myfile = forms.FileField(label='myfile', required=False)


class RenameForm(forms.Form):
    newname = forms.CharField(
        label='newname', widget=forms.Textarea(attrs={"rows": 10, "cols": 96, "wrap": "hard"})
    )


FORMATS = [
    ('JSON', 'JSON'), ('CSV', 'CSV')
]


class QueryForm(forms.Form):
    key = forms.CharField(
        label='key', widget=forms.TextInput(attrs={'size': '24', 'placeholder': 'key'}),  required=False
    )
    value = forms.CharField(
        label='value',  widget=forms.TextInput(attrs={'size': '24', 'placeholder': 'value'}), required=False
    )
    query = forms.CharField(
        label='query', widget=forms.Textarea(attrs={"rows": 6, "cols": 27, "wrap": "hard", "placeholder": "query"}), required=False
    )
    projection = forms.CharField(
        label='projection', widget=forms.Textarea(attrs={"rows": 6, "cols": 27, "wrap": "hard", "placeholder": "projection"}), required=False
    )
    format = forms.CharField(label='Which Format?',
                              widget=forms.Select(choices=FORMATS), required=False)


class newUserForm(forms.Form):
    newUser = forms.CharField(
        label='newUser', max_length=100)
    pwd = forms.CharField(widget=forms.PasswordInput(),
                          label='pwd', min_length=8, max_length=100)
