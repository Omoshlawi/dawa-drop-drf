from django.db import models


# Create your models here.

class LoyaltyProgram(models.Model):
    name = models.CharField(max_length=255, help_text="Name of the loyalty program")
    unit_point = models.PositiveIntegerField(help_text="Number of points awarded on each successful order")
    description = models.TextField(null=True, blank=True)
    point_rate = models.DecimalField(decimal_places=2, max_digits=12, help_text='Point worth in KES')


class Reward(models.Model):
    program = models.ForeignKey(LoyaltyProgram, related_name='rewards', on_delete=models.CASCADE)
    description = models.TextField()
    point_value = models.PositiveIntegerField(help_text='Number of points needed to redeem the reward')
    max_redemptions = models.PositiveIntegerField(null=True, blank=True,
                                                  help_text='Maximum number of times this reward can be redeemed')


