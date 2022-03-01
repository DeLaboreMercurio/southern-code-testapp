from core.models import Booking, PricingRule, Property
from django.core.validators import MinValueValidator
from rest_framework import serializers


class PropertySerializer(serializers.ModelSerializer):
    base_price = serializers.FloatField(validators=[MinValueValidator(0.01)])
    class Meta:
        model = Property
        fields = ('name', 'base_price', 'id')
        read_only_fields = tuple('id')
        extra_kwargs = {
            'name': {'required': True, 'allow_blank': False},
            'base_price': {'required': True}
        }

class PropertyPatchSerializer(serializers.ModelSerializer):
    base_price = serializers.FloatField(validators=[MinValueValidator(0.01)], required=False)
    class Meta:
        model = Property
        fields = ('name', 'base_price', 'id')
        extra_kwargs = {
            'name': {'allow_blank': False},
        }

class PropertyPutSerializer(serializers.ModelSerializer):
    base_price = serializers.FloatField(validators=[MinValueValidator(0.01)])
    id = serializers.IntegerField()
    class Meta:
        model = Property
        fields = ('name', 'base_price', 'id')
        extra_kwargs = {
            'name': {'required': True, 'allow_blank': False},
            'base_price': {'required': True}
        }

class PropertyDeleteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)
    class Meta:
        model = Property
        fields = ('id',)

class PricingRuleSerializer(serializers.ModelSerializer):

    fixed_price = serializers.FloatField(validators=[MinValueValidator(0.01)], required=False)
    min_stay_length = serializers.IntegerField(validators=[MinValueValidator(0)], required=False)
    specific_day = serializers.DateField(input_formats=['%m-%d-%Y'], format='%m-%d-%Y', required=False)
    price_modifier = serializers.FloatField(validators=[MinValueValidator(0.01)], required=False)
    
    class Meta:
        model = PricingRule
        fields = ('property', 'price_modifier', 'min_stay_length', 'fixed_price', 'specific_day', 'id')
        read_only_fields = tuple('id')
        extra_kwargs = {
            'property': {'required': True},
        }

class PricingRulePatchSerializer(serializers.ModelSerializer):

    fixed_price = serializers.FloatField(validators=[MinValueValidator(0.01)], required=False)
    min_stay_length = serializers.IntegerField(validators=[MinValueValidator(0)], required=False)
    specific_day = serializers.DateField(input_formats=['%m-%d-%Y'], format='%m-%d-%Y', required=False)
    price_modifier = serializers.FloatField(validators=[MinValueValidator(0.01)], required=False)
    class Meta:
        model = PricingRule
        read_only_fields = tuple('id')
        fields = ('property', 'price_modifier', 'min_stay_length', 'fixed_price', 'specific_day', 'id')
        extra_kwargs    = {
            'property': {'required': False},
        }





class PrincingRulePutSerializer(serializers.ModelSerializer):
    fixed_price = serializers.FloatField(validators=[MinValueValidator(0.01)])
    min_stay_length = serializers.IntegerField(validators=[MinValueValidator(0)])
    specific_day = serializers.DateField(input_formats=['%m-%d-%Y'], format='%m-%d-%Y')
    id = serializers.IntegerField()
    class Meta:
        model = PricingRule
        fields = ('property', 'price_modifier', 'min_stay_length', 'fixed_price', 'specific_day', 'id')
        extra_kwargs = {
            'property': {'required': True},
            'id' : {'required': True}
        }

class PricingRuleDeleteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = PricingRule
        fields = ('id',)


class BookingSerializer(serializers.ModelSerializer):
    date_start = serializers.DateField(input_formats=['%m-%d-%Y'], format='%m-%d-%Y', required=True, allow_null=False)
    date_end = serializers.DateField(input_formats=['%m-%d-%Y'], format='%m-%d-%Y', required=True, allow_null=False)
    class Meta:
        model = Booking
        fields = ('property', 'id', 'final_price', 'date_start', 'date_end')
        read_only_fields = ('id', 'final_price')
        extra_kwargs = {
            'property': {'required': True},
        }

class BookingPatchSerializer(serializers.ModelSerializer):
    date_start = serializers.DateField(input_formats=['%m-%d-%Y'], format='%m-%d-%Y', required=False)
    date_end = serializers.DateField(input_formats=['%m-%d-%Y'], format='%m-%d-%Y', required=False)
    class Meta:
        model = Booking
        fields = ('property', 'id', 'final_price', 'date_start', 'date_end')


class BookingPutSerializer(serializers.ModelSerializer):
    date_start = serializers.DateField(input_formats=['%m-%d-%Y'], format='%m-%d-%Y', required=True)
    date_end = serializers.DateField(input_formats=['%m-%d-%Y'], format='%m-%d-%Y', required=True)
    id = serializers.IntegerField()
    class Meta:
        model = Booking
        fields = ('property', 'id', 'final_price', 'date_start', 'date_end')
        extra_kwargs = {
            'property': {'required': True},
            'id' : {'required': True}
        }

class BookingDeleteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = Booking
        fields = ('id',)

