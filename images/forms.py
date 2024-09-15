from django import forms
import requests
from django.core.files.base import ContentFile
from django.utils.text import slugify

from .models import Image


class ImageCreateForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ["title", "url", "description"]
        widgets = {
            "url": forms.HiddenInput,
        }

    def clean_url(self):
        url = self.cleaned_data["url"]
        valid_extensions = ["jpg", "jpeg", "png"]
        extension = url.rsplit(".", 1)[1].lower()
        if extension not in valid_extensions:
            raise forms.ValidationError(
                "The given URL does not match valid image extensions."
            )
        return url

    def save(self, commit=True):
        # Get the instance of Image without saving to database yet
        image = super(ImageCreateForm, self).save(commit=False)

        # Retrieve the URL and other cleaned data
        image_url = self.cleaned_data["url"]
        name = slugify(self.cleaned_data["title"])  # Use cleaned_data to get 'title'
        extension = image_url.rsplit(".", 1)[1].lower()
        image_name = f"{name}.{extension}"

        # Download image from the given URL
        response = requests.get(image_url)

        # Save image to the Image model's 'image' field
        image.image.save(
            image_name,
            ContentFile(response.content),
            save=False,  # Do not save to database yet
        )

        if commit:
            image.save()  # Save to database if commit is True

        return image
