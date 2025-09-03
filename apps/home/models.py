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
    start_date = models.DateField()
    end_date = models.DateField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    guest_count = models.PositiveIntegerField(default=1)
    rooms_count = models.PositiveIntegerField(default=1)

    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{8,15}$',
        message="Phone number must be entered in digits only (8-15 digits)."
    )
    phone = models.CharField(validators=[phone_regex], max_length=15)

    def clean(self):
        if self.start_date and self.end_date:
            if self.start_date >= self.end_date:
                raise ValidationError("The start date cannot be later than the end date.")

            # Check for booking overlap only if dates are specified
            if self.rooms_count:
                overlap = Booking.objects.filter(room=self.rooms_count,
                                                 start_date=self.end_date,
                                                 end_date=self.start_date)
                if overlap.exists():
                    raise ValidationError("This room is already booked for the selected dates.")


        overlapping_bookings = Booking.objects.filter(
            rooms_count=self.rooms_count,
            start_date__lt=self.start_date,
            end_date__gt=self.end_date,
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
        nights = (self.end_date - self.start_date).days
        return nights * self.price_per_night

    def __str__(self):
        return f"Booking {self.id} - {self.start_date} to {self.end_date}"