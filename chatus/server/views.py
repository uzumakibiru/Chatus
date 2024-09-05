from django.shortcuts import render
from rest_framework import viewsets
from .models import Server
from .serializer import ServerSerializer
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError,AuthenticationFailed
from django.db.models import Count
from .schema import server_list_docs

# Create your views here.
class ServerListViewSet(viewsets.ViewSet):
    """ViewSet for listing and filtering Server instances.

    This ViewSet provides an endpoint to list all available Server instances
    with optional filtering based on query parameters. It supports filtering
    by category, limiting the number of results, filtering by server ID,
    and annotating the results with the number of members in each server.

    Attributes:
        queryset (QuerySet): The base queryset for all Server objects.

    Methods:
        list(request): Handles GET requests to retrieve a filtered list of servers.
    """
    

    queryset = Server.objects.all()  # Initial queryset for all Server objects
    @server_list_docs
    def list(self, request):
        """Retrieve a filtered list of servers based on query parameters.

        Args:
            request (HttpRequest): The request object containing query parameters.

        Query Parameters:
            - category (str, optional): Filter servers by the name of the category.
            - qty (int, optional): Limit the number of results to the specified quantity.
            - by_user (str, optional): Filter servers by the authenticated user. Must be 'true' to apply the filter.
            - by_serverid (int, optional): Filter servers by a specific server ID.
            - with_num_members (str, optional): Annotate the results with the number of members in each server. Must be 'true' to apply.

        Raises:
            AuthenticationFailed: If `by_user` or `by_serverid` is specified and the user is not authenticated.
            ValidationError: If `by_serverid` is specified and the server ID is invalid or does not exist.

        Returns:
            Response: A Response object containing the serialized server data.
        """
        # Get query parameters from the request
        category = request.query_params.get("category")
        qty = request.query_params.get("qty")
        by_user = request.query_params.get("by_user") == "true"  # Convert to boolean
        by_serverid = request.query_params.get("by_serverid")
        with_num_members = request.query_params.get("with_num_members") == "true"  # Convert to boolean

      

        # If with_num_members is true, annotate the queryset with the number of members
        if with_num_members:
            self.queryset = self.queryset.annotate(num_members=Count("member"))

        # If category is provided, filter the queryset by the category name
        if category:
            self.queryset = self.queryset.filter(category__name=category)
        
          # If filtering by user or server ID, check if the user is authenticated
        if by_user:
            if by_user and  request.user.is_authenticated:
                user_id= request.user.id
                self.queryset=self.queryset.filter(member=user_id)
            else:
                raise AuthenticationFailed()  # Raise an error if the user is not authenticated

        # If qty is provided, limit the number of results returned
        if qty:
            self.queryset = self.queryset[:int(qty)]

        # If by_serverid is provided, filter the queryset by the server ID
        if by_serverid:
            if not request.user.is_authenticated:
                return AuthenticationFailed()
            else:
                try:
                    self.queryset = self.queryset.filter(id=by_serverid)
                    # If no servers are found with the given ID, raise a validation error
                    if not self.queryset.exists():
                        raise ValidationError(detail=f"Server with id {by_serverid} doesn't exist")
                except ValueError:
                    # Raise a validation error if by_serverid is not a valid integer
                    raise ValidationError(detail=f"Server value error")

        # Serialize the queryset with the context of num_members if applicable
        serializer = ServerSerializer(self.queryset, many=True, context={"num_members": with_num_members})
        return Response(serializer.data)  # Return the serialized data as a response