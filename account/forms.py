from django import forms
from account.models import User

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    
    class Meta:
        model = User
        fields = ['first_name','last_name','username','email','password']

    def clean(self):
        cleaned_data = super(UserForm,self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password != confirm_password:
            raise forms.ValidationError("Passwords does not matched")

class UpdateProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name','last_name','username','email','phone_number','about','image']
        widgets = {
            'first_name': forms.TextInput(attrs={'style':"font-size:14px; padding:10px",'class':"form-control"}),
            'last_name': forms.TextInput(attrs={'style':"font-size:14px; padding:10px",'class':"form-control"}),
            'username': forms.TextInput(attrs={'style':"font-size:14px; padding:10px",'class':"form-control"}),
            'email': forms.TextInput(attrs={'style':"font-size:14px; padding:10px",'class':"form-control"}),
            'phone_number': forms.TextInput(attrs={'style':"font-size:14px; padding:10px",'class':"form-control"}),
            'about': forms.Textarea(attrs={'style':"font-size:14px; padding:10px; height:200px;",'class':"form-control"}),  
            'image': forms.FileInput(attrs={'style':"font-size:14px; padding:10px",'class':"form-control"}),  
        }