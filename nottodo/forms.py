from django import forms
from django.contrib.auth.models import User
from .models import NotToDo, SharedNotToDo, Comment
from django import forms
from .models import NotToDo, SharedNotToDo, Comment

class NotToDoForm(forms.ModelForm):
    class Meta:
        model = NotToDo
        fields = ['title', 'description', 'context', 'scheduled_start_time', 'scheduled_end_time', 'repeat']
        widgets = {
            'scheduled_start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'scheduled_end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['scheduled_start_time'].required = True
        self.fields['scheduled_end_time'].required = True


class ShareNotToDoForm(forms.ModelForm):
    class Meta:
        model = SharedNotToDo
        fields = ['shared_with']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

class CustomChangeEmailForm(forms.Form):
    email = forms.EmailField(label="New Email")
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email
    def save(self):
        self.user.email = self.cleaned_data['email']
        self.user.save()
