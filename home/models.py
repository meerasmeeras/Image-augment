from django.db import models

# Create your models here.

class Image(models.Model):
    image = models.ImageField(upload_to='images/')
    augmented_image = models.ImageField(upload_to='images/', null=True, blank=True)

    def __str__(self):
        return f"Image {self.id}"