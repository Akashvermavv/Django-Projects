from django.db import models
from django.urls import reverse
from django.db.models.signals import pre_save
from django.utils.text import slugify
from django.conf import settings
from django.utils import timezone
from django.utils.safestring import mark_safe
from markdown_deux import markdown
from comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from .utils import get_read_time

class Contact(models.Model):
    name = models.CharField(max_length=120)
    phone_number = models.IntegerField()
    email_id = models.EmailField(max_length=50)
    msg = models.TextField(max_length=500)

    def __str__(self):
        return self.name

class PostManager(models.Manager):
    def active(self,*args,**kwargs):
        # Post.objects.all() = super(PostManager,self).all()
        return super(PostManager,self).filter(draft=False).filter(publish__lte=timezone.now())


def upload_location(instance,filename):
    # print('instance ----',instance)
    # print('filename ----',filename)
    # print('instance.id ----',instance.id)
    return f"{instance.pk}/{filename}"

class  Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,default=1,on_delete=models.CASCADE)
    title = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to=upload_location,null=True,blank=True,
                            width_field ="width_field",
                             height_field ="height_field"
                             )
    height_field = models.IntegerField(default=0)
    width_field = models.IntegerField(default=0)
    content = models.TextField()
    draft = models.BooleanField(default=False)
    publish = models.DateField(auto_now=False,auto_now_add=False)
    read_time = models.IntegerField(default=0) #models.TimeField(null=True,blank=True)
    updated = models.DateTimeField(auto_now=True,auto_now_add=False)
    timestamp = models.DateTimeField(auto_now_add=True,auto_now=False)

    objects = PostManager()

    def __str__(self):
        return self.title



    def get_absolute_url(self):
        # return f"/posts/{self.id}"
        return reverse("posts:detail",kwargs={"slug":self.slug})

    def get_api_url(self):
        # return f"/posts/{self.id}"
        return reverse("posts-api:api_detail",kwargs={"slug":self.slug})

    class Meta:
        ordering = ["-timestamp","-updated"]#["-id",]

    def get_markdown(self):
        content = self.content
        mark_text =markdown(content)
        return mark_safe(mark_text)

    @property
    def comments(self):
        instance = self
        qs = Comment.objects.filter_by_instance(instance)
        return qs

    @property
    def get_content_type(self):
        instance = self
        content_type = ContentType.objects.get_for_model(instance.__class__)
        return content_type


def create_slug(instance,new_slug=None):
    slug = slugify(instance.title)
    if new_slug is not None:
        slug = new_slug
    qs = Post.objects.filter(slug=slug).order_by("-id")
    exists = qs.exists()
    if exists:
        new_slug = f"{slug}-{qs.first().id}"
        return create_slug(instance,new_slug=new_slug)
    return slug


def pre_save_post_receiver(sender,instance,*args,**kwargs):

    print('before pre instance slug --',instance.slug)
    if not instance.slug:
        instance.slug = create_slug(instance)
    print('after pre instance slug --', instance.slug)

    if instance.content:
        html_string = instance.get_markdown()
        read_time_var = get_read_time(html_string)
        instance.read_time = read_time_var

pre_save.connect(pre_save_post_receiver,sender=Post)












