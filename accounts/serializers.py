import secrets

from rest_framework import serializers as sz

from .models import User, Student, Group


class StudentSerializer(sz.ModelSerializer):
    user = sz.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_student=True))

    class Meta:
        model = Student
        fields = ('user', 'group',)


class GroupSerializer(sz.ModelSerializer):
    students = StudentSerializer

    class Meta:
        model = Group
        fields = 'id', 'name', 'students'

    def validate(self, data):
        for student in data['students']:
            if student.group is not None:
                raise sz.ValidationError(
                    'Данный студент уже состоит в другой группе!')
        return data


class NewStudentUserSerializer(sz.ModelSerializer):
    auto_password = sz.HiddenField(default=True)
    is_student = sz.HiddenField(default=True)
    password = sz.HiddenField(default='default', write_only=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email',
                  'auto_password', 'is_student', 'password')
        extra_kwargs = {"first_name": {"required": True},
                        "last_name": {"required": True},
                        "email": {"required": True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            first_name=validated_data.get("first_name"),
            last_name=validated_data.get("last_name"),
            email=validated_data.get("email"),
            username="temporary_username",
            auto_password=validated_data.get("auto_password"),
            is_student=validated_data.get("is_student")
        )
        allowed_chars = "abcdefghjkmnpqrstuvwxyz" \
                        "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
        password = "".join(secrets.choice(allowed_chars) for i in range(14))
        user.set_password(password)
        user.check_password(password)
        user.save()

        return validated_data

    def validate(self, data):
        fields = ['first_name', 'last_name', 'email']
        for field in fields:
            if data[field] is None or len(data[field]) < 2:
                raise sz.ValidationError(
                    "Данное поле не может быть пустым!")
        return data
