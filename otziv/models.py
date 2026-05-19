from django.db import models

from films.models import Room


class Otziv(models.Model):
    name = models.CharField(max_length=30)
    text = models.TextField(max_length=20000)
    email = models.EmailField()
    date = models.DateField()
    room = models.ForeignKey(Room, on_delete=models.CASCADE)

    def __str__(self):
        return self.room.name

    def get_room_name(self):
        return self.room.name
