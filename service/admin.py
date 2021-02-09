from django.contrib import admin
from .models import Order, Services, SubServices, OrderProducts, Product, Report, Rating, LatestBlogNews
# Register your models here.
admin.site.register(Order)
admin.site.register(Services)
admin.site.register(SubServices)
admin.site.register(Product)
admin.site.register(Report)
admin.site.register(Rating)
admin.site.register(LatestBlogNews)