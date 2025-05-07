from Demos.mmapfile_demo import page_size
from django.core.cache import cache
from django.shortcuts import render
from django.http import  HttpResponse
from django.views.generic import DeleteView
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from products.models import Products
from products.serializers import ProductSerializer
# from products.serializers import OrderSerializer
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q  # To handle complex filters
import logging
logger = logging.getLogger(__name__)  # Logger for debugging errors

from django.db import transaction

def greet(request):
    data = Products.objects.all()
    print(data)
    # if data.exists():
    product = data[0] #good practise to assign to a variable, rather access data[0] directly bcz query sets are lazy
    print("Before:", product.name)  # Output: ShivaShakti
    product.name = "SitaRam"
    product.save()  # Explicitly save the updated object
    product.refresh_from_db()  # Reload the object to confirm the change
    print("After:", product.name)  # Should now output: ShivaShakti
    # else:
    #     print("No products found.")
    return HttpResponse("Hey we found World")


@csrf_exempt
@api_view(['GET', 'POST'])
def create_r_get_products(request):
    if request.method == 'GET':
        # Fetch all products from the database
        data = Products.objects.all()
        # Serialize the data for JSON response
        serialized_products = ProductSerializer(data, many=True)
        return Response(serialized_products.data)  # Return the serialized data

    elif request.method == 'POST':
        # Deserialize and validate the incoming JSON data
        serialized_products = ProductSerializer(data=request.data)
        if serialized_products.is_valid():
            serialized_products.save()  # Save the valid data to the database
            return Response(serialized_products.data, status=status.HTTP_201_CREATED)  # Success response
        return Response(serialized_products.errors, status=status.HTTP_400_BAD_REQUEST)  # Error response


@api_view(['GET'])
def get_product(request, id):
    try:
        #first checking the cache before retrieving data from the db
        cache_key = f'products_{id}'
        data = cache.get(cache_key)
        if data:
            return Response(data, status=status.HTTP_200_OK)

        # Retrieves a single product based on the provided ID from the DB
        data = Products.objects.get(id=id)
        # Serializes the specific product data into a format suitable for JSON responses.
        serialized_products = ProductSerializer(data)
        # Extracts the serialized product data (in JSON format).
        serialized_data = serialized_products.data
        #setting the serialized data as the value of the cache key
        cache.set(cache_key, serialized_data)
        return Response(serialized_data) ## Sends the serialized product data as an API response.
    except Products.DoesNotExist:
        return Response({'error': f'Product with ID {id} does not exist.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def filter_products(request):
    # Extract 'description' and 'name' filters from query parameters
    name = request.query_params.get('name',None)   # Extract product name
    description = request.query_params.get('description', None) # Extract description
    # adding the validations for name to check name parameter cannot be Empty.
    if name is not None:  # Check if the name parameter exists
        if not name.strip() or name in ['""', "''", "None"]:  # Check if it's empty or invalid
            return Response({'error': 'Product name cannot be empty.'}, status=status.HTTP_400_BAD_REQUEST)
    # print(f"name: {repr(name)}", type(name))  # Use repr() to see if it's None or an empty string

    try:
        # Extract 'min_price' and 'max_price' from query parameters and convert them to float
        # If conversion fails, raise a validation error to inform the user
        min_price = float(request.query_params.get('min_price')) if request.query_params.get('min_price') else None
        max_price = float(request.query_params.get('max_price')) if request.query_params.get('max_price') else None
    except ValueError:
        # Return an error response if the price parameters are not numeric
        return Response({'error': 'Price parameters must be numeric.'}, status=status.HTTP_400_BAD_REQUEST)
    if min_price and max_price and min_price > max_price: #validation for the Prices
        return Response({'error': 'Minimum price cannot be greater than maximum price.'}, status=status.HTTP_400_BAD_REQUEST)

    # Initialize an empty filter using Q objects to dynamically combine conditions
    filter_query = Q()
    if name:   # Add a condition to filter products by name
        filter_query &= Q(name__icontains=name)   #&= means and query was getting constructed
    # add a condition to filter based on Description and Skip filtering by description if it's empty
    if description and not description.strip():
        filter_query &= Q(description__icontains=description)
    if min_price:
        filter_query &= Q(price__gte=min_price)  #Products with price >= min_price
    if max_price:
        filter_query &= Q(price__lte=max_price)  #Products with price <= max_price

    # Fetch products from the database that match the constructed filter query
    filtered_products = Products.objects.filter(filter_query)
    # Serialize the filtered products to convert them into a JSON-friendly format
    serialized_products = ProductSerializer(filtered_products, many=True)
    # Return the response with filtered data
    return Response(serialized_products.data, status=status.HTTP_200_OK)


#PATCH allows partial updates without affecting others, and also can update fully.
@api_view(['PATCH'])
def update_product(request, id):
    try:
        product = Products.objects.get(id=id)  # Get the product
        serialized_product = ProductSerializer(product, data=request.data, partial=True)  # Allow partial updates

        if serialized_product.is_valid():
            serialized_product.save()  # Save changes
            return Response(serialized_product.data, status=status.HTTP_200_OK)

        return Response(serialized_product.errors, status=status.HTTP_400_BAD_REQUEST)

    except Products.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
def delete_product(request, id):
    try:
        product = Products.objects.get(id=id)  # Fetch product by ID
        product.delete()  # Delete the product from the database
        return Response({'message': 'Product deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

    except Products.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)



# ✅ Custom paginator to control page size limits
class ProductPaginator(PageNumberPagination):
    page_size = 10  # Default number of products per page
    page_size_query_param = 'page_size'  # Allows dynamic resizing via query params
    max_page_size = 50  # Prevents excessive data requests that could slow down the server

# ✅ API View get the filtered products with Post request and pagination applied
class PageViewSet(APIView):

    def post(self, request):
        # 🎯 Get search query and sorting preference from request body
        query = request.data.get("query", "")
        order_by = request.data.get("order_by", "-created_at")

        # 🛠 Validate ordering field to prevent unexpected errors
        valid_ordering = {"created_at", "name", "price", "-created_at", "-name", "-price"}
        if order_by not in valid_ordering:
            order_by = "-created_at"  # Default fallback

        # 🔍 Build filtering query using Q() for flexibility
        filters = Q()
        if query:
            filters |= Q(name__icontains=query) | Q(description__icontains=query)  # Case-insensitive search on name & description

        # 📦 Fetch filtered and sorted products from the database
        queryset = Products.objects.filter(filters).order_by(order_by)

        # 🔢 Apply pagination with error handling in this post request to get the data
        paginator = ProductPaginator()
        try:
            result = paginator.paginate_queryset(queryset, request)
        except Exception as e:
            self.logger.error(f"Pagination error: {e}")
            return Response({"error": "Invalid pagination parameters"}, status=400)

        # 📝 Serialize results before returning
        serializer = ProductSerializer(result, many=True)
        return paginator.get_paginated_response(serializer.data)

