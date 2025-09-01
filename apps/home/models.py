# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class RoomType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Room(models.Model):
    number = models.IntegerField()
    room_type = models.ForeignKey('RoomType', on_delete=models.CASCADE, related_name='rooms')
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Room {self.number} - {self.room_type.name}"

class Guest(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return self.name

class Booking(models.Model):
    check_in = models.DateField()
    check_out = models.DateField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    guest_count = models.PositiveIntegerField(default=1)
    rooms_count = models.PositiveIntegerField(default=1)

    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{8,15}$',
        message="Phone number must be entered in digits only (8-15 digits)."
    )
    phone = models.CharField(validators=[phone_regex], max_length=15)

    def clean(self):
        if self.check_out <= self.check_in:
            raise ValidationError("The check-in date must be before the check-out date.")

        overlapping_bookings = Booking.objects.filter(
            rooms_count=self.rooms_count,
            check_in__lt=self.check_out,
            check_out__gt=self.check_in,
        )
        if self.pk:
            overlapping_bookings = overlapping_bookings.exclude(pk=self.pk)

        if overlapping_bookings.exists():
            raise ValidationError("The room is already booked for these dates.")

    def save(self, *args, **kwargs):
        if not self.price_per_night:
            self.price_per_night = 100
        if not self.pk:
            self.price_per_night = self.price_per_night * self.rooms_count
        super().save(*args, **kwargs)

    def total_price(self):
        nights = (self.check_out - self.check_in).days
        return nights * self.price_per_night

    def __str__(self):
        return f"Booking {self.id} - {self.check_in} to {self.check_out}"