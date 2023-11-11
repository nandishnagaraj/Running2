from django.contrib import admin
from .models import Product, ReviewRating, Variation, DownloadRecord
from ckeditor.widgets import CKEditorWidget

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'coach', 'category', 'modified_date', 'is_available')
    prepopulated_fields = {'slug': ('product_name',)}
    formfield_overrides = {
        Product.shortdescription: {'widget': CKEditorWidget},
        Product.longdescription: {'widget': CKEditorWidget},
    }


class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'variation_value', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('product', 'variation_category', 'variation_value')

class DownloadRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'download_time')

admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(ReviewRating)
admin.site.register(DownloadRecord, DownloadRecordAdmin)


