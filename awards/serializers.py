from rest_framework import serializers

from awards.models import LoyaltyProgram, Reward


class LoyaltyProgramSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = LoyaltyProgram
        fields = ('url', 'name', 'unit_point', 'image', 'description', 'point_rate', 'is_default', 'created_at')
        extra_kwargs = {
            'url': {'view_name': 'awards:program-detail'}
        }


class RewardSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Reward
        fields = ('url', 'program', 'image', 'description', 'point_value', 'max_redemptions', 'created_at')
        extra_kwargs = {
            'url': {'view_name': 'awards:reward-detail'},
            'program': {'view_name': 'awards:program-detail'},
        }
