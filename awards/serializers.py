from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.reverse import reverse

from awards.models import LoyaltyProgram, Reward
from users.models import Redemption


class RewardSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Reward
        fields = ('url', 'name', 'program', 'image', 'description', 'point_value', 'max_redemptions', 'created_at')
        extra_kwargs = {
            'url': {'view_name': 'awards:reward-detail'},
            'program': {'view_name': 'awards:program-detail'},
        }

    def to_representation(self, instance):
        dictionary = super().to_representation(instance)
        program_url = dictionary.pop("program")
        program_obj = {
            'program': {
                'url': program_url,
                'name': instance.program.name
            }
        }
        dictionary.update(program_obj)
        return dictionary


class LoyaltyProgramSerializer(serializers.HyperlinkedModelSerializer):
    members_count = serializers.SerializerMethodField()
    rewards = RewardSerializer(read_only=True, many=True)

    def get_members_count(self, instance):
        return instance.members.count()

    class Meta:
        model = LoyaltyProgram
        fields = (
            'url', 'name', 'unit_point', 'image', 'description', 'point_rate',
            'rewards', 'members_count', 'is_default', 'created_at'
        )
        extra_kwargs = {
            'url': {'view_name': 'awards:program-detail'}
        }


class RedemptionSerializer(serializers.HyperlinkedModelSerializer):
    # url = serializers.SerializerMethodField()
    # points_balance = serializers.SerializerMethodField()

    # def get_points_balance(self, instance):
    #     return instance.patient.points_balance

    def get_url(self, instance):
        return reverse(
            viewname='users:patient-redeem-detail',
            request=self.context.get('request'),
            args=[instance.patient.id, instance.id]
        )

    def validate_reward(self, reward):
        user = self.context.get('request').user
        points = user.patient.points_balance
        if points < reward.point_value:
            raise ValidationError(
                f"Insufficient points of {points}, you must have at least {reward.point_value} points")
        return reward

    class Meta:
        model = Redemption
        fields = (
            # 'url',
            'patient',
            'points_redeemed', 'reward', 'created_at',
            # 'points_balance'
        )
        extra_kwargs = {
            'patient': {'view_name': 'users:patient-detail', 'read_only': True},
            'reward': {'view_name': 'awards:reward-detail'},
            'points_redeemed': {'read_only': True}
        }
