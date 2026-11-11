from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    tags_input = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите теги через запятую'
        }),
        label="Теги",
        help_text="- можно указать несколько тегов",
    )

    class Meta:
        model = Post
        fields = ['title', 'category', 'tags_input', 'text', 'image']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': "Максимальная длина 200 символов"
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'text': forms.Textarea(attrs={
                'rows': 3,
                'cols': 20
            }),
            'image': forms.FileInput(attrs={'class': 'form-control'})
        }
        labels = {
            'title': 'Заголовок поста:',
            'category': 'Категория:',
            'text': 'Текст поста:',
            'image': 'Картинка поста'
        }
        help_texts = {
            'category': "- можно выбрать только одну категорию",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = "- Категория -"

    def clean_title(self):
        title = self.cleaned_data['title'].strip()
        if len(title) < 10:
            raise forms.ValidationError("Заголовок не должен быть короче 10 символов.")
        return title

    def clean_tags_input(self):
        tags_data = self.cleaned_data.get('tags_input', '')
        tag_names = [
            tag_name.strip().lower()
            for tag_name in tags_data.split(',')
            if tag_name.strip()
        ]
        return tag_names
