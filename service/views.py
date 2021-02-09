from account.models import User
from .models import Services, SubServices, Order, Rating, \
    Product, OrderProducts, Report, LatestBlogNews
from .serializers import ServicesSerializer, SubServicesSerializer, \
    OrderSerializer, RatingSerializer, ProductSerializer, ReportSerializer, LatestBlogNewsSerializer
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework import permissions


# Create your views here.
class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Services.objects.all()
    serializer_class = ServicesSerializer
    permission_classes = (AllowAny,)

    # disable delete method from viewset
    def destroy(self, request, *args, **kwargs):
        response = {'message': 'You Cant Delete from here !'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    # disable update method from viewset
    def update(self, request, *args, **kwargs):
        response = {'message': 'You Cant Update from here !'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['GET'])
    def get_sub_service(self, request, pk=None):
        sub_services = SubServices.objects.filter(service=pk)
        serializer = SubServicesSerializer(sub_services, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SubServicesViewSet(viewsets.ModelViewSet):
    queryset = SubServices.objects.all()
    serializer_class = SubServicesSerializer
    permission_classes = (AllowAny,)

    # disable update method from viewset
    def update(self, request, *args, **kwargs):
        response = {'message': 'You Cant Update from here !'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # disable delete method from viewset

    def destroy(self, request, *args, **kwargs):
        response = {'message': 'You Cant Delete from here !'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'],
            permission_classes=[permissions.IsAuthenticated])
    def apply_order(self, request, pk=None):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            customer = request.user
            service = SubServices.objects.get(id=request.data['service'])
            technical = User.objects.get(id=request.data['technical'])
            if request.data['orderId']:
                customer_order = Order.objects.get(id=request.data['orderId'])
                customer_order.technical = technical
                customer_order.date = request.data['date']
                response = {'message': 'Successfully updating order'}
            else:
                customer_order = Order.objects.create(
                    customer=customer,
                    service=service,
                    technical=technical,
                    date=request.data['date']
                )
                response = {'message': 'Successfully apply order'}

            # optional fields
            # check for description order
            if 'description' in request.data:
                customer_order.description = request.data['description']

            if 'service_cost' in request.data:
                customer_order.service_cost = request.data['service_cost']

            if 'product_cost' in request.data:
                customer_order.product_cost = request.data['product_cost']

            if 'product_names' in request.data:
                customer_order.product_names = request.data['product_names']

            if 'isEmergency' in request.data:
                customer_order.isEmergency = request.data['isEmergency']

            customer_order.save()



            # check for products in order
            if 'products' in request.data:
                for product in request.data['products']:
                    product = Product.objects.get(id=product)
                    OrderProducts.objects.create(order=customer_order, product=product)

            serializer = OrderSerializer(customer_order, many=False)
            response['result'] = serializer.data
            return Response(response, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerOrder(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (permissions.IsAuthenticated,)

    # disable delete method from viewset
    def destroy(self, request, *args, **kwargs):
        response = {'message': 'You Cant Delete from here !'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    # disable update method from viewset
    def update(self, request, *args, **kwargs):
        response = {'message': 'You Cant Update from here !'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def delete_order(self, request, pk=None):
        if 'orderId' in request.data:
            Order.objects.get(id=request.data['orderId']).delete()
            return Response({'message': 'order deleted successfully'}, status=status.HTTP_200_OK)
        return Response({'fail': 'Order id is missing !'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'])
    def get_all_customer_orders(self, request, pk=None):
        user = Token.objects.get(key=request.auth.key).user
        orders = Order.objects.filter(customer=user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductView(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    # disable delete method from viewset
    def destroy(self, request, *args, **kwargs):
        response = {'message': 'You Cant Delete from here !'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    # disable update method from viewset
    def update(self, request, *args, **kwargs):
        response = {'message': 'You Cant Update from here !'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['GET'])
    def get_products(self, request, pk=None):
        products = Product.objects.filter(category=pk)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReportService(APIView):
    """
       An endpoint for report service.
    """
    serializer_class = ReportSerializer
    # authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    # override post method
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            order = Order.objects.get(id=request.data['orderId'])
            Report.objects.create(
                order= order,
                issues=request.data['issues']
            )
            return Response({'message': 'Issues have been reported '}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RateTechnicianJob(APIView):
    """
       An endpoint for rate and review technician job.
    """
    serializer_class = ReportSerializer
    # authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        if 'rate' and 'orderId' in request.data and int(request.data['rate']) > 0:
            customer = request.user
            order = Order.objects.get(id=request.data['orderId'])
            rate = request.data['rate']
            technical = order.technical
            try:
                rating = Rating.objects.get(order=order)
                rating.rate = rate
                if 'review' in request.data:
                    rating.review = request.data['review']
                rating.save()
                technical.avg_rating = self.avg_rating(order.technical)
                serializer = RatingSerializer(rating, many=False)
                response = {'message': 'Rating Updated', 'result': serializer.data}
            except Exception as err:
                if 'review' in request.data:
                    rating = Rating.objects.create(customer=customer, technical=order.technical,
                                                   order=order,review=request.data['review'], rate=rate)
                else:
                    rating = Rating.objects.create(customer=customer, technical=order.technical,
                                                   order=order, rate=rate)
                technical.no_of_rating = self.no_of_rating(order.technical)
                technical.avg_rating = self.avg_rating(order.technical)
                serializer = RatingSerializer(rating, many=False)
                response = {'message': 'Rating Create', 'result': serializer.data}
            technical.save()
            return Response(response, status=status.HTTP_200_OK)
        else:
            response = {'fail': 'You Need to provide valid technician rate'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

    def no_of_rating(self, technical):
        rating = Rating.objects.filter(technical=technical)
        return len(rating)

    def avg_rating(self, technical):
        sum = 0
        ratings = Rating.objects.filter(technical=technical)
        for rate in ratings:
            sum += rate.rate
        if len(ratings) > 0:
            return sum / len(ratings)
        else:
            return 0


class ClientsReview(APIView):

    def get(self, request):
        reviews = Rating.objects.all().order_by('create_at')[::-1]
        reviewsObj = []
        count = 0
        for review in reviews:
            if review.review and count < 3:
                count+=1
                reviewsObj.append(self.constract_review_obj(review))
            else:
                break
        response = {'reviews': reviewsObj}
        return Response(reviewsObj, status=status.HTTP_200_OK)

    def constract_review_obj(self, obj):
        user = User.objects.get(email=obj.customer)
        review = obj.review
        return {
            'avatar': user.avatar.url,
            'username': user.username,
            'review': review
        }



class LatestBlogs(APIView):
    """
       An endpoint for LatestBlogs.
    """
    serializer_class = LatestBlogNewsSerializer

    # override post method
    def get(self, request):
        news = LatestBlogNews.objects.all().order_by('add_at')[::-1]
        serializer = LatestBlogNewsSerializer(news[0:3], many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

