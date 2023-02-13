from django import forms
from . models import Blog
from taggit.forms import TagField
class CreateBlogForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'style':"font-size:14px; padding:10px",'class':"form-control"}))
    short_description = forms.CharField(widget=forms.TextInput(attrs={'class':"form-control",'style':"font-size:14px; padding:10px"}))
    tags = TagField(widget=forms.TextInput(attrs={'class':"form-control",'style':"font-size:14px; padding:10px"}))
    image = forms.ImageField(widget=forms.FileInput(attrs={'style':'width:100%;border-color:#CED4DA;font-size:14px; margin-left:5px; padding:10px'}))

    class Meta:
        model = Blog
        fields = ['title','short_description','image','long_description','is_featured','tags']