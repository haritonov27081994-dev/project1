from django import forms
from .models import Post  # Относительный импорт модели

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'text', 'image']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': "Максимальная длина 200 символов"
            }),
            'text': forms.Textarea(attrs={
                'rows': 3,
                'cols': 20
            }),
            'image': forms.FileInput(attrs={'class': 'form-control'})
        }
        labels = {
            'title': 'Заголовок поста:',
            'text': 'Текст поста:',
            'image': 'Картинка поста'
        }

    # Валидация заголовка полностью сохраняется
    def clean_title(self):
        title = self.cleaned_data['title'].strip()
        if len(title) < 10:
            raise forms.ValidationError("Заголовок не должен быть короче 10 символов.")
        return title
