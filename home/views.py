from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.shortcuts import redirect
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
import os
import zipfile
import cv2
from django.conf import settings
from albumentations import Compose, RandomRotate90, Flip, Transpose, RandomBrightnessContrast, RandomScale, ShiftScaleRotate
from .models import Image
from django.contrib import messages
from django.urls import reverse
from .forms import ImageForm
# Create your views here.

def index(request):
    
    return render(request, 'index.html')

def image_upload(request):
    if request.method == 'POST' and request.FILES.getlist('images'):
        images = request.FILES.getlist('images')
        uploaded_image_paths = []
        for image in images:
            img = Image(image=image)
            img.save()
            uploaded_image_paths.append(img.image.path)
        
        augmented_image_paths = augment_images(uploaded_image_paths)
        for image_path, img in zip(augmented_image_paths, Image.objects.filter(augmented_image__isnull=True)):
            img.augmented_image = image_path
            img.save()

        zip_file = create_zip_file(augmented_image_paths)

        response = HttpResponse(open(zip_file, 'rb').read(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=augmented_images.zip'
        

        return response
    
    return render(request, 'image_upload.html', {})

def augment_images(image_paths, num_versions=5):
    transform = Compose([
        RandomRotate90(),
        Flip(),
        Transpose(),
        RandomBrightnessContrast(),
        RandomScale(scale_limit=0.2, p=0.5),
        ShiftScaleRotate(shift_limit=0.0625, scale_limit=0.2, rotate_limit=45, p=0.5)
    ])

    augmented_image_paths = []
    for image_path in image_paths:
        for i in range(num_versions):
            image = cv2.imread(image_path)
            if image is None:
                print(f"Error reading image: {image_path}")
                continue
            augmented = transform(image=image)['image']
            augmented_image_path = os.path.join(settings.MEDIA_ROOT, f'aug_{i}_{os.path.basename(image_path)}')
            cv2.imwrite(augmented_image_path, augmented)
            augmented_image_paths.append(augmented_image_path)

    return augmented_image_paths

def create_zip_file(image_paths):
    zip_filename = os.path.join(settings.MEDIA_ROOT, 'augmented_images.zip')
    with zipfile.ZipFile(zip_filename, 'w') as zf:
        for image_path in image_paths:
            zf.write(image_path, os.path.basename(image_path))
    return zip_filename
