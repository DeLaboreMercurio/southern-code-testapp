import logging

from django.forms import model_to_dict
from django.http import HttpRequest
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

import core.models as models
from core.bookings import BookingService
from core.utils.serializers import *

logger = logging.getLogger(__name__)


class Property(APIView):
    def post(self, request: HttpRequest) -> Response:
        """post creates a new property.

        Args:
            request (HttpRequest): The request object.

        Returns:
            Response: The response object.
        """
        property = PropertySerializer(data=request.data)
        if property.is_valid():
            property.save()
            logger.info(f'Property {property.data["name"]} created.')
            return Response(property.data, status=status.HTTP_201_CREATED)
        return Response(property.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request: HttpRequest) -> Response:
        """get returns all properties.

        Args:
            request (HttpRequest): The request object.

        Returns:
            Response: The response object.
        """
        properties = PropertySerializer(models.Property.objects.all(), many=True)
        return Response(properties.data)


class PropertyDetail(APIView):
    def get(self, request: HttpRequest, pk: int) -> Response:
        """get returns a single property.

        Args:
            request (HttpRequest): The request object.
            pk (int): The property ID.

        Returns:
            Response: The response object.
        """
        try:
            property = PropertySerializer(models.Property.objects.get(id=pk))
            return Response(property.data)
        except models.Property.DoesNotExist:
            logger.warning(f"Attempted to get Property {pk}, but does not exist.")
            return Response("Invalid ID. Property not found.", status=status.HTTP_404_NOT_FOUND)

    def patch(self, request: HttpRequest, pk: int) -> Response:
        """patch updates an existing property.

        Args:
            request (HttpRequest): The request object.
            pk (int): The property ID.

        Returns:
            Response: The response object.
        """
        property = PropertyPatchSerializer(data=request.data)
        if property.is_valid():
            saved_property = models.Property.objects.get(id=pk)
            updated = property.update(saved_property, property.validated_data)
            updated = PropertySerializer(updated)
            logger.info(f'Property {updated.data["name"]} updated.')
            return Response(updated.data, status=status.HTTP_200_OK)
        return Response(
            "Request body has missing or invalid fields.", status=status.HTTP_400_BAD_REQUEST
        )

    def put(self, request: HttpRequest, pk: int) -> Response:
        """put replaces an existing property.

        Args:
            request (HttpRequest): The request object.
            pk (int): The property ID.

        Returns:
            Response: The response object.
        """
        property = PropertySerializer(data=request.data)
        if property.is_valid():
            saved_property = models.Property.objects.get(id=pk)
            updated = property.update(saved_property, property.validated_data)
            updated = PropertySerializer(updated)
            logger.info(f'Property {updated.data["name"]} updated.')
            return Response(updated.data, status=status.HTTP_200_OK)
        return Response(
            "Request body has missing or invalid fields.", status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request: HttpRequest, pk: int) -> Response:
        """delete deletes an existing property.

        Args:
            request (HttpRequest): The request object.
            pk (int): The property ID.

        Returns:
            Response: The response object.
        """

        try:
            deleted_property = models.Property.objects.get(id=pk)
            models.Property.delete(deleted_property)
            logger.info(f"Property {pk} deleted.")
            return Response(status=status.HTTP_204_NO_CONTENT)
        except models.Property.DoesNotExist:
            logger.warning(f"Attempted to delete Property {pk}, but does not exist.")
            return Response("Invalid ID. Property not found.", status=status.HTTP_404_NOT_FOUND)


class PricingRule(APIView):
    def post(self, request: HttpRequest) -> Response:
        """post creates a new pricing rule.

        Args:
            request (HttpRequest): The request object.

        Returns:
            Response: The response object.
        """
        pricing_rule = PricingRuleSerializer(data=request.data)
        if pricing_rule.is_valid():
            pricing_rule.save()
            logging.info(
                f'PricingRule: Created pricing rule {pricing_rule.data["id"]} for property {pricing_rule.data["property"]}'
            )
            return Response(pricing_rule.data, status=status.HTTP_201_CREATED)
        return Response(pricing_rule.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request: HttpRequest) -> Response:
        """get returns all pricing rules.

        Args:
            request (HttpRequest): The request object.

        Returns:
            Response: The response object.
        """
        pricing_rules = PricingRuleSerializer(models.PricingRule.objects.all(), many=True)
        return Response(pricing_rules.data)


class PricingRuleDetail(APIView):
    def get(self, request: HttpRequest, pk: int) -> Response:
        """get returns a single pricing rule.

        Args:
            request (HttpRequest): The request object.
            pk (int): The pricing rule ID.

        Returns:
            Response: The response object.
        """
        try:
            pricing_rule = PricingRuleSerializer(models.PricingRule.objects.get(id=pk))
            return Response(pricing_rule.data)
        except models.PricingRule.DoesNotExist:
            return Response(
                "Invalid ID. Pricing rule not found.", status=status.HTTP_404_NOT_FOUND
            )

    def patch(self, request: HttpRequest, pk: int) -> Response:
        """patch updates an existing pricing rule.

        Args:
            request (HttpRequest): The request object.
            pk (int): The pricing rule ID.

        Returns:
            Response: The response object.
        """
        pricing_rule = PricingRulePatchSerializer(data=request.data)
        if pricing_rule.is_valid():
            try:
                saved_pricing_rule = models.PricingRule.objects.get(id=pk)
                updated = pricing_rule.update(saved_pricing_rule, pricing_rule.validated_data)
                updated = PricingRuleSerializer(updated)
                logging.info(
                    f'PricingRule: Updated pricing rule {updated.data["id"]} for property {updated.data["property"]}'
                )
                return Response(updated.data, status=status.HTTP_200_OK)
            except models.PricingRule.DoesNotExist:
                return Response(
                    "Invalid ID. Pricing rule not found.", status=status.HTTP_404_NOT_FOUND
                )
        return Response(
            "Request body has missing or invalid fields.", status=status.HTTP_400_BAD_REQUEST
        )

    def put(self, request: HttpRequest, pk: int) -> Response:
        """put replaces an existing pricing rule.

        Args:
            request (HttpRequest): The request object.
            pk (int): The pricing rule ID.

        Returns:
            Response: The response object.
        """
        pricing_rule = PricingRuleSerializer(data=request.data)

        if pricing_rule.is_valid():
            try:
                saved_pricing_rule = models.PricingRule.objects.get(id=pk)
                updated = pricing_rule.update(saved_pricing_rule, pricing_rule.validated_data)
                updated = PricingRuleSerializer(updated)
                logging.info(
                    f'PricingRule: Updated pricing rule {updated.data["id"]} for property {updated.data["property"]}'
                )
                return Response(updated.data, status=status.HTTP_200_OK)
            except models.PricingRule.DoesNotExist:
                return Response(
                    "Invalid ID. Pricing rule not found.", status=status.HTTP_404_NOT_FOUND
                )
        return Response(
            "Request body has missing or invalid fields.", status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request: HttpRequest, pk: int) -> Response:
        """delete deletes an existing pricing rule.

        Args:
            request (HttpRequest): The request object.
            pk (int): The pricing rule ID.

        Returns:
            Response: The response object.
        """

        try:
            deleted_pricing_rule = models.PricingRule.objects.get(id=pk)
            models.PricingRule.delete(deleted_pricing_rule)
            logging.info(
                f"PricingRule: Deleted pricing rule {pk} for property {pricing_rule.data.property}"
            )
            return Response(status=status.HTTP_204_NO_CONTENT)
        except models.PricingRule.DoesNotExist:
            logging.warning(f"Attempted to delete PricingRule {pk}, but does not exist.")
            return Response("Invalid ID. PricingRule not found.", status=status.HTTP_404_NOT_FOUND)


class Booking(APIView):
    def post(self, request: HttpRequest) -> Response:
        """post creates a new booking.

        Args:
            request (HttpRequest): The request object.

        Returns:
            Response: The response object.
        """
        booking = BookingSerializer(data=request.data)
        if not booking.is_valid():
            return Response(booking.errors, status=status.HTTP_400_BAD_REQUEST)

        final_booking = BookingService(booking_information=booking).process_booking()
        booking_response = BookingSerializer(final_booking).data
        return Response(booking_response, status=status.HTTP_201_CREATED)

    def get(self, request: HttpRequest) -> Response:
        """get returns all bookings.

        Args:
            request (HttpRequest): The request object.

        Returns:
            Response: The response object.
        """
        bookings = BookingSerializer(models.Booking.objects.all(), many=True)
        return Response(bookings.data)


class BookingDetail(APIView):
    def get(self, request: HttpRequest, pk: int) -> Response:
        """get returns a single booking.

        Args:
            request (HttpRequest): The request object.
            pk (int): The booking ID.

        Returns:
            Response: The response object.
        """
        try:
            booking = BookingSerializer(models.Booking.objects.get(id=pk))
            return Response(booking.data)
        except models.Booking.DoesNotExist:
            return Response("Invalid ID. Booking not found.", status=status.HTTP_404_NOT_FOUND)

    def patch(self, request: HttpRequest, pk: int) -> Response:
        """patch updates an existing booking.

        Args:
            request (HttpRequest): The request object.
            pk (int): The booking ID.

        Returns:
            Response: The response object.
        """
        booking = BookingPatchSerializer(data=request.data)
        if not booking.is_valid():
            return Response(booking.errors, status=status.HTTP_400_BAD_REQUEST)

        existing_booking = models.Booking.objects.get(id=pk)
        new_data = model_to_dict(existing_booking)
        new_data.update(booking.data)
        new_booking = BookingPatchSerializer(data=new_data)
        if not new_booking.is_valid():
            return Response(new_booking.errors, status=status.HTTP_400_BAD_REQUEST)
        final_booking = BookingService(booking_information=new_booking).process_booking()
        booking_response = BookingSerializer(final_booking).data
        return Response(booking_response, status=status.HTTP_201_CREATED)

    def put(self, request: HttpRequest, pk: int) -> Response:
        """put replaces an existing booking.

        Args:
            request (HttpRequest): The request object.
            pk (int): The booking ID.

        Returns:
            Response: The response object.
        """
        booking = BookingSerializer(data=request.data)
        if not booking.is_valid():
            return Response(booking.errors, status=status.HTTP_400_BAD_REQUEST)

        existing_booking = models.Booking.objects.get(id=pk)
        new_data = model_to_dict(existing_booking)
        new_data.update(booking.data)
        new_booking = BookingPatchSerializer(data=new_data)
        if not new_booking.is_valid():
            return Response(new_booking.errors, status=status.HTTP_400_BAD_REQUEST)

        final_booking = BookingService(booking_information=new_booking).process_booking()
        booking_response = BookingSerializer(final_booking).data
        return Response(booking_response, status=status.HTTP_201_CREATED)

    def delete(self, request: HttpRequest, pk: int) -> Response:
        """delete deletes an existing booking.

        Args:
            request (HttpRequest): The request object.
            pk (int): The booking ID.

        Returns:
            Response: The response object.
        """

        try:
            deleted_booking = models.Booking.objects.get(id=pk)
            models.Booking.delete(deleted_booking)
            logging.info(f"Booking: Deleted booking {pk} for property {deleted_booking.property}")
            return Response(status=status.HTTP_204_NO_CONTENT)
        except models.Booking.DoesNotExist:
            logging.warning(f"Attempted to delete Booking {pk}, but does not exist.")
            return Response("Invalid ID. Booking not found.", status=status.HTTP_404_NOT_FOUND)


class PropertyList(generics.ListAPIView):
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    queryset = models.Property.objects.all()
    serializer_class = PropertySerializer
    search_fields = ["name", "base_price"]
    filterset_fields = {
        "base_price": ["lt", "gt", "lte", "gte", "exact"],
        "name": ["icontains"],
    }
    ordering_fields = "__all__"
    ordering = ["-id"]


class BookingList(generics.ListAPIView):
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    queryset = models.Booking.objects.all()
    serializer_class = BookingSerializer
    search_fields = ["property", "date_start", "date_end", "final_price"]
    filterset_fields = {
        "property": ["exact"],
        "date_start": ["lt", "gt", "lte", "gte", "exact"],
        "date_end": ["lt", "gt", "lte", "gte", "exact"],
        "final_price": ["lt", "gt", "lte", "gte", "exact"],
    }
    ordering_fields = "__all__"
    ordering = ["-id"]
