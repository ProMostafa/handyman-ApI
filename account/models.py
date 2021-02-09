from django.db import models
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser)
from .validations import phone_validation
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken
# Create your models here.

# for avoid circular import
class Services(models.Model):
    type = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='service/')

    def __str__(self):
        return f"Service Category: {self.type}"




class UserManager(BaseUserManager):

    def create_user(self, email, username, phone, address, password=None):
        """
                Creates and saves a User with the given email, date of
                birth and password.
        """
        # if not email or not username or not phone or not address:
        #     raise ValueError("User Must Have All Required Data ?")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            phone=phone,
            address=address
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, phone, address, password=None):
        user = self.create_user(
            email,
            username=username,
            phone=phone,
            password=password,
            address=address
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    username = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=60, blank=True, null=True)
    last_name = models.CharField(max_length=60, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatar/', blank=True, null=True)
    address = models.CharField(max_length=1024)
    city = models.CharField(max_length=1024, default='Luxor')
    country = models.CharField(max_length=1024, default='Egypt')
    phone = models.CharField(
        max_length=11,
        null=False,
        validators=[phone_validation]
    )
    date_of_creation = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    is_verified = models.BooleanField(default=False)

    # for technical Account
    is_technical = models.BooleanField(default=False)
    available = models.BooleanField(default=True)
    technical_job = models.ForeignKey(Services, on_delete=models.CASCADE, null=True, blank=True, default='')
    no_of_rating = models.IntegerField(default=0)
    avg_rating = models.IntegerField(default=0)


    # for manage users
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_stuff = models.BooleanField(default=False)

    objects = UserManager()

    # using for login
    # USERNAME_FIELD = 'username or email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone', 'address']

    def token(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }
        # return Token.objects.get(user=self)

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

