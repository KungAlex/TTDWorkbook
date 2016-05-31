from django import forms
from lists.models import Item


class ItemForm(forms.models.ModelForm):

    class Meta:
        EMPTY_LIST_ERROR = "You can't have an empty list item"
        model = Item
        fields = ('text',)
        widgets = {
            'text': forms.fields.TextInput(attrs={
                'placeholder': 'Enter a to-do item',
                'class': 'form-control input-lg',

            }),
        }
        error_messages = {
            'text': {'required': EMPTY_LIST_ERROR}
        }
