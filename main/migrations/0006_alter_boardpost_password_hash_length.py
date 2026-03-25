# Django password hash 문자열 길이 여유

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0005_boardattachment"),
    ]

    operations = [
        migrations.AlterField(
            model_name="boardpost",
            name="password",
            field=models.CharField(
                help_text="게시글 수정/삭제 시 사용할 비밀번호 (해시 저장)",
                max_length=256,
                verbose_name="수정/삭제 비밀번호",
            ),
        ),
    ]
