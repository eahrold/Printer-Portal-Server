from rest_framework import serializers
from printers.models import Option, Printer, PrinterList


class OptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Option
        fields = ('option',)

    def create(self, validated_data):
        """
        Create and return a new `Option` instance, given the validated data.
        """
        return Option.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Option`
        instance, given the validated data.
        """
        instance.options = validated_data.get('name', instance.name)
        instance.save()
        return instance


class PrinterSerializer(serializers.ModelSerializer):
    # options = OptionSerializer(many=True, read_only=True)
    options = serializers.SlugRelatedField( many=True, read_only=True, slug_field='option')

    class Meta:
        model = Printer
        fields = ('name',
                  'description',
                  'host',
                  'protocol',
                  'location',
                  'model',
                  'ppd_file',
                  'options')

    def to_internal_value(self, data):
        return data

    def create(self, validated_data):
        """
        Create and return a new `Printer` instance, given the validated data.
        """
        return Printer.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Printer` instance,
        given the validated data.
        """

        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get(
            'description',
            instance.description)
        instance.host = validated_data.get('host', instance.host)
        instance.protocol = validated_data.get('protocol', instance.protocol)
        instance.location = validated_data.get('location', instance.location)
        instance.model = validated_data.get('model', instance.model)

        instance.ppd_file = validated_data.get('ppd_file', instance.ppd_file)
        
        options = validated_data.get('options')

        if options:
            for opt in options:
                obj = Option.objects.get_or_create(option=opt)
                instance.options.add(obj[0].pk)

        instance.save()
        return instance


class PrinterListSerializer(serializers.ModelSerializer):
    printers = PrinterSerializer(many=True, read_only=True)

    class Meta:
        model = PrinterList
        fields = ('name',
                  'printers',
                  'public')

    def create(self, validated_data):
        """
        Create and return a new `PrinterList` instance, given the validated data.
        """
        return PrinterList.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Printer List` instance, given the validated data.
        """
        instance.options = validated_data.get('name', instance.name)

        instance.save()
        return instance
