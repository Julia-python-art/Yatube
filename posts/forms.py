from django import forms

from .models import Post, Group, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["group", "text", "image"]
        required = {"group": False}
        labels = {"group": "Сообщества",
                "text": "Текст записи",
                "image": "Картинка"}

    def validate_form(self):
        data = self.cleaned_data["text"]
        if data is None:
            raise forms.ValidationError("Пост не может быть пустым")
        return data    




class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]
        labels = {"text": "Текст комментария"}
        widgets = {"text": forms.Textarea()}

    def validate_form(self):
        data = self.cleaned_data["text"]
        if data is None:
            raise forms.ValidationError("Комментарий не может быть пустым")
        return data         