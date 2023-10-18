from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Plans)
admin.site.register(models.User_plan)
admin.site.register(models.Payment)
admin.site.register(models.Withdraw)
admin.site.register(models.Referral)
admin.site.register(models.ReferralDetails)
admin.site.register(models.Chat)
