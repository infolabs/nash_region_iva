from django import forms


class ProblemClassifierForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea)

    def send_email(self):
        print('send email')
        # send email using the self.cleaned_data dictionary
        pass
