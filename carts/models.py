from django.db import models
from django.forms import ValidationError
from accounts.models import Account
from store.models import Product, Variation

# Create your models here.

class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.cart_id


class CartItem(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    cart    = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)

    def sub_total(self):
        return self.product.price * self.quantity
    
    def save(self, *args, **kwargs):
        if self.quantity > 1:
            raise ValidationError("Quantity cannot be greater than 1")
        super().save(*args, **kwargs)

    def __unicode__(self):
        return self.product
