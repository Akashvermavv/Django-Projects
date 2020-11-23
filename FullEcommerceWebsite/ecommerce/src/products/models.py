from django.db import models
import os
import random
from django.urls import reverse
from django.db.models import Q
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from ecommerce.utils import unique_slug_generator,get_filename
from django.db.models.signals import pre_save
from category.models import Categories


def get_filename_ext(filepath):
    print('filepath -',filepath)
    base_name = os.path.basename(filepath)
    name,ext = os.path.splitext(base_name)
    print('name ext --',name,ext)
    return name,ext

def upload_image_path(instance,filename):
    new_filename = random.randint(1,1234567)
    name,ext = get_filename_ext(filename)
    final_filename = f"{new_filename}{ext}"
    return f"products/{new_filename}/{final_filename}"

class ProductQuerySet(models.query.QuerySet):

    def active(self):
        return self.filter(active=True)

    def featured(self):
        return self.filter(featured=True,active=True)

    def search(self,query):
        lookups = (
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(price__icontains=query) |
                Q(tag__title__icontains=query)
        )
        return self.filter(lookups).distinct()


class ProductManager(models.Manager):

    def get_queryset(self):
        return ProductQuerySet(self.model,using=self._db)

    def all(self):
        return self.get_queryset().active()

    def featured(self):  # Product.objects.featured()
        return self.get_queryset().featured()

    def get_by_id(self,id):
        # return self.get_queryset().filter(id=id)  # Product.objects  ---> self.get_queryset()
        qs =  self.get_queryset().filter(id=id)   # Product.objects  ---> self.get_queryset()
        if qs.count() ==1:
            return qs.first()
        return None

    def search(self,query):
        return self.get_queryset().active().search(query)


# category_choice=(
#         ('created', 'Created'),
#         ('paid', 'Paid'),
#         ('shipped', 'Shipped'),
#         ('refunded', 'Refunded'),
#     )


class Product(models.Model):
    title           = models.CharField(max_length=120)
    category        = models.ForeignKey(Categories,on_delete=models.CASCADE,default=1)
    slug            = models.SlugField(blank=True,unique=True)
    description     = models.TextField()
    price           = models.DecimalField(decimal_places=2,max_digits=20,default=39.99)
    image           = models.ImageField(upload_to=upload_image_path,null=True,blank=True)
    featured        = models.BooleanField(default=False)
    active          = models.BooleanField(default=True)
    timestamp       = models.DateTimeField(auto_now_add=True)
    is_digital      = models.BooleanField(default=False)  # User Library

    objects = ProductManager()

    def get_absolute_url(self):
        # return f"/products/{self.slug}"
        return reverse("products:detail",kwargs={"slug":self.slug})

    def __str__(self):
        return self.title

    @property
    def name(self):
        return self.title

    def get_downloads(self):
        qs = self.productfile_set.all()
        return qs


def product_pre_save_receiver(sender,instance,*args,**kwargs):
    if not instance.slug:
        # instance.slug ='abc'
        instance.slug =unique_slug_generator(instance)


pre_save.connect(product_pre_save_receiver,sender=Product)


def upload_product_file_loc(instance,filename):
    print('instance id !!!--',instance.id)
    slug = instance.product.slug
    if not slug:
        slug = unique_slug_generator(instance.product)
    location = f"product/{slug}/"
    return location + filename  # "path/to/filename.mp4"


class ProductFile(models.Model):
    product         = models.ForeignKey(Product,on_delete=models.CASCADE)
    # file            = models.FileField(upload_to='products/')
    file            = models.FileField(
                                        upload_to=upload_product_file_loc,
                                       storage=FileSystemStorage(location=settings.PROTECTED_ROOT)
                                       )
    free            = models.BooleanField(default=False)   # purchase required
    user_required   = models.BooleanField(default=False)   # user doesn't matter

    def __str__(self):
        return str(self.file.name)

    def get_default_url(self):
        return self.product.get_absolute_url()

    def get_download_url(self):  # same as detail view  return file path
        # return self.file.url
        return reverse("products:download",kwargs={"slug":self.product.slug,"pk":self.pk})

    @property
    def name(self):
        return get_filename(self.file.name)
















