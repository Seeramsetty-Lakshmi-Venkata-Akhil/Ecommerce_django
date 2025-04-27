from django.shortcuts import render
from django.http import  HttpResponse
from django.views.generic import DeleteView
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from products.models import Products
from products.models import Order
from products.serializers import ProductSerializer
from products.serializers import OrderSerializer
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q  # To handle complex filters

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
        # Retrieves a single product based on the provided ID.
        data = Products.objects.get(id=id)
        # Serializes the specific product data into a format suitable for JSON responses.
        serialized_products = ProductSerializer(data)
        # Extracts the serialized product data (in JSON format).
        serialized_data = serialized_products.data
        # Sends the serialized product data as an API response.
        return Response(serialized_data)
    except Products.DoesNotExist:
        return Response({'error': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

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
        filter_query &= Q(name__icontains=name)
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


#Class based Orders Views

# View to list all orders or create a new order
class OrderListCreateView(APIView):
    def get(self, request):
        # Fetch all orders
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Create a new order with request data
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Save new order to database
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# View to retrieve, update, or delete a single order
class OrderDetailView(APIView):
    def get_object(self, pk):
        # Helper method to get the order by primary key (id)
        try:
            return Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return None

    def get(self, request, pk):
        # Retrieve a single order
        order = self.get_object(pk)
        if not order:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = OrderSerializer(order, context= {'request': request}) #passing request to serializer for dis &tax
        return Response(serializer.data)

    def patch(self, request, pk):
        # Update an existing order partially or fully
        order = self.get_object(pk)
        if not order:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = OrderSerializer(order, data=request.data, partial=True) # Important: partial=True
        if serializer.is_valid():
            serializer.save()  # Save the updated order
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        # Delete an order
        order = self.get_object(pk)
        if not order:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)