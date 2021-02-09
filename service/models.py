from django.db import models
from django.core.validators import MaxLengthValidator,MinLengthValidator
from account.models import User, Services
from account.validations import issues_validation


# Create your models here.


# class Services(models.Model):
#     type = models.CharField(max_length=100)
#     description = models.TextField()
#     image = models.ImageField(upload_to='service/')
#
#     def __str__(self):
#         return f"Service Category: {self.type}"


# class ServicePicture(models.Model):
#     service = models.ForeignKey(Services, on_delete=models.CASCADE)
#     picture = models.ImageField(upload_to='services/')


class SubServices(models.Model):
    service = models.ForeignKey(Services, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    note = models.CharField(max_length=1024, default='')
    # image = models.ImageField(upload_to='sub_services/')
    cost = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"Service Category: {self.service.type}, Service Name: {self.name}"

    def get_service_name(self):
        return self.service.type


class Product(models.Model):
    category = models.ForeignKey(Services, on_delete=models.CASCADE, related_name='product_category')
    name = models.CharField(max_length=255)
    cost = models.FloatField()
    image = models.ImageField(upload_to='products/')

    def __str__(self):
        return f"category: {self.category.type} , product name:{self.name}"


class Order(models.Model):
    customer = models.ForeignKey(User, related_name='customer_order', on_delete=models.CASCADE)
    technical = models.ForeignKey(User, related_name='technical_order', on_delete=models.CASCADE)
    service = models.ForeignKey(SubServices, related_name='service_order', on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    create_at = models.DateField(auto_now_add=True)
    description = models.TextField(blank=True)
    date = models.CharField(max_length=50,default='')
    service_cost = models.CharField(max_length=50,default='Vary After Inspection')
    product_cost = models.FloatField(default=0)
    # for now product_names as str , best should be in order serializer and fetch this names then constract this fields
    product_names = models.CharField(max_length=255,default='')
    isEmergency = models.BooleanField(default=False)

    def __str__(self):
        return f"customer Name:{self.customer.username}, technician Name: {self.technical.username}, service:{self.service.name}"


class OrderPictures(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    pictures = models.ImageField(upload_to='order/')


class OrderSubService(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    sub_service = models.ForeignKey(SubServices, related_name='sub_services_order', on_delete=models.CASCADE)


class OrderProducts(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)


class Rating(models.Model):
    customer = models.ForeignKey(User, related_name='customer_rate', on_delete=models.CASCADE)
    technical = models.ForeignKey(User, related_name='technical_rate', on_delete=models.CASCADE)
    order = models.ForeignKey(Order, related_name='customer_rate_order', on_delete=models.CASCADE, blank=True)
    review = models.TextField(default='')
    create_at = models.DateField(auto_now_add=True)
    rate = models.IntegerField(choices=[
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
    ])

    class Meta:
        unique_together = (('customer', 'technical','order'),)
        # when ordering data
        index_together = (('customer', 'technical','order'),)

    def __str__(self):
        return f"customer: {self.customer.username}, review: {self.review}"


class Report(models.Model):
    order = models.ForeignKey(Order, related_name='service_report', on_delete=models.CASCADE)
    issues = models.TextField()

    def __str__(self):
        return f"customer Name: {self.order.customer.username}, issues: {self.issues}"


# Blog News Add by admin
class LatestBlogNews(models.Model):
    title = models.CharField(max_length=100);
    post = models.TextField()
    add_at = models.DateField(auto_now_add=True)
    picture = models.ImageField(upload_to='blogNews/')

    def __str__(self):
        return f'title: {self.title}, post: {self.post}'
