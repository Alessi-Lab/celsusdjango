import numpy as np
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework_simplejwt.tokens import AccessToken


def get_user_from_token(request):
    if 'HTTP_AUTHORIZATION' in request.META:
        authorization = request.META['HTTP_AUTHORIZATION'].replace("Bearer ", "")
        access_token = AccessToken(authorization)
        user = User.objects.filter(pk=access_token["user_id"]).first()
        if user:
            return user
    return


def is_user_staff(request):
    user = request.user
    if not user:
        user = get_user_from_token(request)
    if user:
        if user.is_staff:
            return True
    return False


def delete_file_related_objects(file):
    for c in file.comparisons.all():
        with transaction.atomic():
            for column in c.differential_sample_columns.all():
                column.delete()
            for da in c.differential_analysis_datas.all():
                da.delete()
    with transaction.atomic():
        for r in file.raw_datas.all():
            r.delete()
    for rc in file.raw_sample_columns.all():
        with transaction.atomic():
            rc.delete()


def calculate_boxplot_parameters(values):
    q1, med, q3 = np.percentile(values, [25, 50, 75])

    iqr = q3 - q1

    low = q1 - 1.5 * iqr
    high = q3 + 1.5 * iqr

    wisker_high = np.compress(values <= high, values)
    wisker_low = np.compress(values >= low, values)

    real_high_val = np.max(wisker_high)
    real_low_val = np.min(wisker_low)

    return {"low": real_low_val, "q1": q1, "med": med, "q3": q3, "high": real_high_val}
