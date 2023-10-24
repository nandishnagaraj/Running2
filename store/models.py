from django.db import models
from django.urls import reverse
from accounts.models import Account
from category.models import Category
from ckeditor.fields import RichTextField
from django.db.models import Avg, Count

# Create your models here.

class Product(models.Model):
    product_name    = models.CharField(max_length=200, unique=True)
    slug            = models.SlugField(max_length=200, unique=True)
    shortdescription     = RichTextField()
    longdescription     = RichTextField()
    price           = models.IntegerField()
    images          = models.ImageField(upload_to='photos/products')
    coach           = models.CharField(max_length=500, blank=True, default='Generic')
    is_available    = models.BooleanField(default=True)
    category        = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date    = models.DateTimeField(auto_now_add=True)
    modified_date   = models.DateTimeField(auto_now=True)
    level           = models.CharField(max_length=255,choices=[('1','Level 1'),('2','Level II'),('3','Level III')],default="1")
    pdf_file        = models.FileField(upload_to='pdfs/', blank=True, null=True)
    weeks           = models.IntegerField()
    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])

    def __str__(self):
        return self.product_name
    
    def averageReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg

    def countReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(count=Count('id'))
        count = 0
        if reviews['count'] is not None:
            count = int(reviews['count'])
        return count
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Create a generic "event" variation for this product
        event_variation = Variation.objects.create(
            product=self,
            variation_category='event',
            variation_value='Generic Event',
            is_active=True
        )
        event_variation.save()
    
class VariationManager(models.Manager):

    def event(self):
        return super(VariationManager, self).filter(variation_category='event', is_active=True)
    
variation_category_choice = (
    ('event', 'event'),
)

class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=100, choices=variation_category_choice)
    variation_value     = models.CharField(max_length=100, default='Generic')
    is_active           = models.BooleanField(default=True)
    created_date        = models.DateTimeField(auto_now=True)

    objects = VariationManager()

    def __str__(self):
        return self.variation_value
    
class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject