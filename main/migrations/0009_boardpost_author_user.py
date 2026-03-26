# BoardPost 로그인 작성자 (목록/상세에서 아이디 표시)

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0008_rename_main_bc_post_parent_idx_main_boardc_post_id_7a37ce_idx_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="boardpost",
            name="author_user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="board_posts",
                to=settings.AUTH_USER_MODEL,
                verbose_name="로그인 작성자",
            ),
        ),
    ]
