from rest_framework import serializers

from awards.models import LoyaltyProgram, Reward


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
