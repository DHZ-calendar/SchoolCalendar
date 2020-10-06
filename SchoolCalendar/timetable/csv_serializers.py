from rest_framework.serializers import Serializer, DateField, CharField, SerializerMethodField


class WeekTimetableCSVSerializer(Serializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    hour_start = DateField(format="%H:%M")
    hour_end = DateField(format="%H:%M")
    monday = CharField()
    tuesday = CharField()
    wednesday = CharField()
    thursday = CharField()
    friday = CharField()
    saturday = CharField()

    class Meta(object):
        fields = ('hour_start', 'hour_end', 'monday', 'tuesday', 'wednesday',
                  'thursday', 'friday', 'saturday')  # used to set the order of the fields


class GeneralTimetableCSVSerializer(Serializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    teacher = CharField()

    def __init__(self, queryset, dow_with_hour_slots, **kwargs):
        self.Meta.fields += tuple(dow_with_hour_slots)
        for field in dow_with_hour_slots:
            self.fields[field] = CharField()
        super().__init__(queryset, **kwargs)

    class Meta(object):
        fields = ('teacher',)  # used to set the order of the fields
