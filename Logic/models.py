from django.db import models
from PIL import Image



class Konkurs(models.Model):
	chat = models.IntegerField()
	start = models.BooleanField()
	num = models.IntegerField()
	organaiser = models.IntegerField()

	def __str__(self):
		return f'{self.chat}: {self.start}'



class Work(models.Model):
	name = models.CharField(max_length=400)
	author = models.CharField(max_length=400)
	author_id = models.IntegerField()
	author_nick = models.CharField(max_length=400)
	image_id = models.CharField(max_length=1000000000)
	konkurs_id = models.IntegerField()
	votes = models.IntegerField(null=True, blank=True)

	def __str__(self):
		return f'{self.name}'


class Voter(models.Model):
	u_id = models.IntegerField()
	konkurs_id = models.IntegerField()


		


