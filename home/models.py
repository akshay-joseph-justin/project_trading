
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Plans(models.Model):

    plan_name = models.CharField(max_length=100)
    plan_min_price = models.CharField(max_length=100)
    plan_max_price = models.CharField(max_length=100)
    plan_min_percentage = models.CharField(max_length=100)
    plan_max_percentage = models.CharField(max_length=100)

class User_plan(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plans, on_delete=models.CASCADE)
    contact = models.CharField(max_length=100, null=True)
    invested_amount = models.CharField(max_length=100)
    user_status = models.CharField(max_length=100)
    user_profit = models.CharField(max_length=100)
    user_referral_profit = models.CharField(max_length=100, null=True)
    total_profit = models.CharField(max_length=100, null=True)
    days = models.CharField(max_length=100, null=True)
    

class Payment(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_name = models.CharField(max_length=100)
    transaction_id = models.CharField(max_length=100)
    transaction_amount = models.CharField(max_length=100)
    transaction_status = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now=True, null=True)

class Withdraw(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    withdraw_amount = models.CharField(max_length=100)
    account_name = models.CharField(max_length=100)
    account_no = models.CharField(max_length=100, null=True)
    wallet_id = models.CharField(max_length=100, null=True)
    ifsc_code = models.CharField(max_length=100, null=True)
    withdraw_status = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now=True, null=True)

class Addprofit(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plans, on_delete=models.CASCADE)
    percentage = models.CharField(max_length=100, null=True)
    profit = models.CharField(max_length=100, null=True)
    referral_profit = models.CharField(max_length=100, null=True)
    date = models.DateTimeField(auto_now=True, null=True)

class ReferralDetails(models.Model):
    
    spot_percent_direct = models.CharField(max_length=100, null=True)
    spot_percent_level_1 = models.CharField(max_length=100, null=True)
    spot_percent_level_2 = models.CharField(max_length=100, null=True)
    spot_percent_level_3 = models.CharField(max_length=100, null=True)

    percent_direct = models.CharField(max_length=100, null=True)
    percent_level_1 = models.CharField(max_length=100, null=True)
    percent_level_2 = models.CharField(max_length=100, null=True)
    percent_level_3 = models.CharField(max_length=100, null=True)


class Referral(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    referral_details = models.ForeignKey(ReferralDetails, on_delete=models.CASCADE, null=True)
    referred_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="%(class)s_referred")
    referral_id = models.CharField(max_length=100)
    direct = models.ManyToManyField(User, blank=True, related_name="%(class)s_direct")
    level_1 = models.ManyToManyField(User, blank=True, related_name="%(class)s_level1")
    level_2 = models.ManyToManyField(User, blank=True, related_name="%(class)s_level2")
    level_3 = models.ManyToManyField(User, blank=True, related_name="%(class)s_level3")

class Chat(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    message = models.TextField(max_length=200, null=True)
    replay = models.TextField(max_length=200, null=True)
    date = models.DateTimeField(auto_now=True, null=True)

