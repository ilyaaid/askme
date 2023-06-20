from django.core.files.images import get_image_dimensions
from django.contrib.auth.hashers import make_password

from app import models
from django import forms


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = models.Profile
        fields = ["username", "password"]
        help_texts = {
            "username": "",
        }

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            models.Profile.objects.get(username=username)
        except models.Profile.DoesNotExist:
            raise forms.ValidationError("Username does not exist")
        return username


class NewUserForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput)
    password_check = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = models.Profile
        fields = ["username", "email", "password", "password_check", "avatar"]
        help_texts = {
            "username": "",
        }

    def clean_password_check(self):
        data = self.cleaned_data
        if data['password'] != data['password_check']:
            raise forms.ValidationError('Two password fields didn\'t match')
        return data

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        try:
            w, h = get_image_dimensions(avatar)
            # validate dimensions
            max_height = 4000
            max_width = 4000
            if w > max_width or h > max_height:
                raise forms.ValidationError(
                    u'Please use an image that is '
                    '%s x %s pixels or smaller.' % (max_width, max_height))
            # validate content type
            main, sub = avatar.content_type.split('/')
            if not (main == 'image' and sub in ['jpeg', 'gif', 'png']):
                raise forms.ValidationError(u'Please use a JPEG, '
                                            'GIF or PNG image.')
            # validate file size
            if len(avatar) > (1024 * 1024):
                raise forms.ValidationError(
                    u'Avatar file size may not exceed 1MB')
        except AttributeError:
            """
            Handles case when we are updating the user profile
            and do not supply a new avatar
            """
            pass
        return avatar

    def save(self, commit=True):
        self.cleaned_data.pop('password_check')
        return models.Profile.objects.create_user(**self.cleaned_data)


class SettingForm(forms.ModelForm):
    class Meta:
        model = models.Profile
        fields = ["username", "email", "avatar"]
        help_texts = {
            "username": "",
        }

    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial', {})
        initial['avatar'] = ''
        kwargs['initial'] = initial
        super(SettingForm, self).__init__(*args, **kwargs)

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if not avatar:
            return avatar
        try:
            w, h = get_image_dimensions(avatar)
            # validate dimensions
            max_height = 4000
            max_width = 4000
            if w > max_width or h > max_height:
                raise forms.ValidationError(
                    u'Please use an image that is '
                    '%s x %s pixels or smaller.' % (max_width, max_height))
            # validate content type
            main, sub = avatar.content_type.split('/')
            if not (main == 'image' and sub in ['jpeg', 'gif', 'png']):
                raise forms.ValidationError(u'Please use a JPEG, '
                                            'GIF or PNG image.')
            # validate file size
            if len(avatar) > (1024 * 1024):
                raise forms.ValidationError(
                    u'Avatar file size may not exceed 1MB')
        except AttributeError:
            """
            Handles case when we are updating the user profile
            and do not supply a new avatar
            """
            pass
        return avatar

    def save(self, commit=True):
        user = super().save(commit)
        print(self.cleaned_data)
        return user


class NewQuestionForm(forms.ModelForm):
    tags = forms.CharField(required=False, max_length=50, help_text="the separator for tags is a comma(',')",
                           widget=forms.TextInput(attrs={'placeholder': 'c++, php, django, ...'}))

    class Meta:
        model = models.Question
        fields = ["title", "body", "tags"]

    def __init__(self, *args, **kwargs):
        if "request" in kwargs:
            self.request = kwargs.pop("request")
        super(NewQuestionForm, self).__init__(*args, **kwargs)

    def save_tags(self, q, tags_str):
        print(len(tags_str))
        if tags_str:
            tags_arr_str = tags_str.split(',')
            tags_for_creation = []
            tags_arr_strip_str = set()
            for tag in tags_arr_str:
                tag = tag.strip(' ')
                if len(tag) > 0:
                    tags_arr_strip_str.add(tag)
            # Ищем несуществующие теги
            for tag in tags_arr_strip_str:
                q_set = models.Tag.objects.filter(name=tag)
                if q_set.count() == 0:
                    tags_for_creation.append(models.Tag(name=tag))
            # Добавляем в базу несуществующие теги
            models.Tag.objects.bulk_create(tags_for_creation)

            # Добавляем теги как many_to_many поле
            question_tags = []
            for tag in tags_arr_strip_str:
                tag_obj = models.Tag.objects.get(name=tag)
                question_tags.append(models.Question.tags.through(question_id=q.id, tag_id=tag_obj.id))
            models.Question.tags.through.objects.bulk_create(question_tags)

    def save(self, commit=True):
        tags_str = self.cleaned_data.pop('tags')
        q = models.Question.objects.create(**self.cleaned_data, user=self.request.user)
        self.save_tags(q, tags_str)
        return q


class NewAnswer(forms.ModelForm):
    body = forms.CharField(widget=forms.Textarea(attrs={
    "placeholder": "Enter your answer",
    }), label="Your answer")
    class Meta:
        model = models.Answer
        fields = ["body"]

    def __init__(self, *args, **kwargs):
        if "request" in kwargs:
            self.request = kwargs.pop("request")
        if "question" in kwargs:
            self.question = kwargs.pop("question")
        super(NewAnswer, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        ans_body = self.cleaned_data.get('body')
        if ans_body:
            ans_body = ans_body.strip(' ')
        if not ans_body:
            return None

        answer = models.Answer.objects.create(user=self.request.user,
                                              question=self.question,
                                              body=ans_body)
        return answer
