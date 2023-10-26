from django.shortcuts import render
from django.views import View
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib import messages
from django.shortcuts import redirect
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings
from django.http import Http404

from random import randint

from . import models
#added by sreekanth
class NavMenu(View):
    def get(self, request):
        
        return render(request, 'mininavbar.html',)

class Index_view(View):

    def get(self, request):

        if request.user.is_superuser:
                return redirect("/moderator/dashboard/")
        
        return redirect("/dashboard")

class Dashboard_view(View):
    
    def get(self, request):
        
        user_plans = models.User_plan.objects.filter(user=request.user)
        payments = [payment for payment in models.Payment.objects.filter(user=request.user) if payment.transaction_status != "approved"]
        withdraws = [withdraw for withdraw in models.Withdraw.objects.filter(user=request.user) if withdraw.withdraw_status != "done"]

        context = {
            "user_plans": user_plans,
            "payments": payments,
            "withdraws": withdraws,
            "plans": models.Plans.objects.all(),
        }
        
        return render(request, 'user/index.html', context=context)

class Signup_view(View):

    def get(self, request):
        return render(request, 'signup.html')
    
    def post(self, request):

        fname = request.POST["fname"]
        lname = request.POST["lname"]
        email = request.POST["signup_email"]
        contact = request.POST["contact"]
        uname = request.POST["signup_uname"]
        passw1 = request.POST["signup_passw1"]
        passw2 = request.POST["signup_passw2"]
        referral_id = request.POST.get("referral_id", None)

        temp_context = {
                "fname": fname,
                "lname": lname,
                "email": email,
                "contact": contact,
                "uname": uname,
                "referral": referral_id,
            }
        
        if models.User.objects.filter(email=email).exists() == True:

            messages.error(request, f"an account exists in this email {email}")
            return redirect("/signup")
        
        if models.User.objects.filter(username=uname).exists() == True:

            messages.error(request, "username is taken")
            return redirect("/signup")
        
        if models.User.objects.filter(username=uname, email=email).exists() == True:

            messages.error(request, "user already exists")
            return redirect("/signup")
        
        try:
            int(contact)
        except:
            messages.error(request, "not a valid contact number")
            return redirect("/signup")
        
        try:
            validate_password(passw1)
        except ValidationError:
            messages.error(request, "password validation error")
            return render(request, "signup.html", context=temp_context)

        if passw1 != passw2:

            messages.error(request, "password did not match")
            return render(request, "signup.html", context=temp_context)

        user = User(first_name=fname, last_name=lname,username=uname, email=email)
        user.set_password(passw1)
        user.save()
        authenticate(username=uname, password=passw1)
        login(request, user)

        self.add_user_plan(request.user, contact)
        self.add_referral(request.user)
        print(f"refer [{referral_id}]")
        if len(referral_id) > 5:
            if models.Referral.objects.filter(referral_id=referral_id).exists():
                self.add_referred(request.user, referral_id)
                print("referral tree")
            else:
                messages.error(request, "Referral number did not exists")
                return redirect("/signup")

        messages.success(request, "Signup Successful")
        return redirect("/dashboard")
    
    def add_user_plan(self, user, contact):

        user_plan = models.User_plan()
        user_plan.user = user
        user_plan.contact = contact
        user_plan.invested_amount = "0"
        user_plan.plan = models.Plans.objects.get(id=1)
        user_plan.user_status = "Inactive"
        user_plan.user_profit = "0"
        user_plan.user_referral_profit = "0"
        user_plan.days = "0"
        user_plan.save()

    def add_referral(self, user):

        referral = models.Referral()
        referral.user = user
        referral.referral_details = models.ReferralDetails.objects.all()[0]
        referral_id = str(user.username)+"@"+str(randint(1000, 9999))
        referral.referral_id = referral_id
        referral.save()

    def add_referred(self, user, id):

        referred_user = models.Referral.objects.get(referral_id=id)
        referred_user.direct.add(user)
        referred_user.save()
        
        referrer_user = models.Referral.objects.get(user=user)
        referrer_user.referred_user = referred_user.user
        referrer_user.save()

        if referred_user.referred_user is not None:
            referred_user_1 = models.Referral.objects.get(user=referred_user.referred_user)
            referred_user_1.level_1.add(referrer_user.user)
            if referred_user_1.referred_user is not None:
                referred_user_2 = models.Referral.objects.get(user=referred_user_1.referred_user)
                referred_user_2.level_2.add(referrer_user.user)
                if referred_user_2.referred_user is not None:
                    referred_user_3 = models.Referral.objects.get(user=referred_user_2.referred_user)
                    referred_user_3.level_3.add(referrer_user.user)


class Login_view(View):

    def get(self, request):
        return render(request, 'login.html')
    
    def post(self, request):

        uname = request.POST["login_uname"]
        passw = request.POST["login_passw"]
        user = authenticate(username=uname, password=passw)
        
        if user is not None:
            login(request, user)
            if request.user.is_superuser:
                return redirect("/moderator/dashboard/")
            return redirect(f"/dashboard")
        else:
            messages.error(request, "user name or password is invalid")
            return redirect("/login")
        
class Logout_view(View):
    
    def get(self, request):

        logout(request)
        messages.info(request, "logged out")
        return redirect("/login")

class ForgotPassword_view(View):

    def get(self, request):

        return render(request, "forgotpassw.html")
    
    def post(self, request, **kwargs):
        
        
        if "uname" in request.POST:
            otp_no = randint(100000, 999999)
            uname = request.POST["uname"]
            email = request.POST["email"]

            user = models.User.objects.get(username=uname)
            if email == email:
                
                subject = "Your OTP for AIFX"
                message = f"""
Dear {user.username},
Your OTP to reset your account password on Aifx. Please find your OTP below:

OTP: {otp_no}

Please note that this OTP is valid for a single use and will expire after a certain period. For security reasons, we recommend using this OTP as soon as possible.

If you did not request this OTP or have any concerns about your account security, please contact our support team.

Thank you for using AIFX. We prioritize your account security and are committed to providing you with a safe and secure experience.

Best regards,
"""

                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    ["akshayjosephjustin721@gmail.com",],
                    fail_silently=False,
                )
                context = {
                    "otp": otp_no,
                    "user": user.id
                }

                return render(request, "forgotpassw.html", context=context)
            else:

                messages.error(request, "email incorrect")
                return render(request, "forgotpassw.html")
        
        if "otp" in request.POST:

            otp = request.POST["otp"]
            otp_no = request.POST["otp_no"]
            id = request.POST["user"]

            if otp == otp_no:

                context = {
                    "change": True,
                    "user": id,
                }

                return render(request, "forgotpassw.html", context=context)
            
            else:
                
                context = {
                    "otp": otp_no,
                    "user": user.id
                }
                
                messages.error(request, "OTP Incorrect")
                return render(request, "forgotpassw.html", context=context)
            
        if "passw1" in request.POST:

            passw1 = request.POST["passw1"]
            passw2 = request.POST["passw2"]
            id = request.POST["user"]

            try:
                validate_password(passw1)
            except ValidationError:
                context = {
                    "chane": True,
                    "user": id,
                }
                messages.error(request, "password validation error")
                return render(request, "forgotpassw.html", context=context)
            
            if passw1 != passw2:

                context = {
                    "chane": True,
                    "user": id,
                }
                messages.error(request, "password didnt match")
                return render(request, "forgotpassw.html", context=context)

            user = models.User.objects.get(id=id)
            user.set_password(passw1)
            user.save()
            messages.success(request, "password changed")
            return redirect("/")


class ChangePassword_view(View):

    def get(self, request):

        return render(request, "changepassw.html")
    
    def post(self, request):

        old_passw = request.POST["old_passw"]
        passw1 = request.POST["passw1"]
        passw2 = request.POST["passw2"]

        if request.user.check_password(old_passw):
            
            try:
                validate_password(passw1)
            except ValidationError:
                messages.error(request, "password validation error")
                return redirect("/password/change/")

            if passw1 != passw2:
                messages.error(request, "password didnt match")
                return redirect("/password/change/")
            
            user = models.User.objects.get(id=request.user.id)
            user.set_password(passw1)
            user.save()

            messages.success(request, "password changed")
            return redirect("/")

        else:
            messages.error(request, "current password not match")
            return redirect("/password/change/")


class Chat_view(View):
    
    def get(self, request):

        context = {
            "chats": models.Chat.objects.filter(user=request.user)[::-1],
        }

        return render(request, 'user/chatpage.html', context=context)

    def post(self, request):

        message = request.POST["message"]

        chat = models.Chat()
        chat.user = request.user
        chat.message = message
        chat.save()

        messages.success(request, "message sended")
        return redirect("/chat")


class Plans_view(View):
    
    def get(self, request):

        context = {
            "plans": models.Plans.objects.all(),
        }
        return render(request, 'user/plans.html', context=context)

class Profit_view(View):
    
    def get(self,request):

        user_plan = models.User_plan.objects.get(user=request.user)
        context = {
            "user_plan": user_plan,
        }

        return render(request, 'user/profit.html', context=context)

class Withdraw_view(View):
    
    def get(self,request):
        return render(request, 'user/withdraw.html')
    
    def post(self, request):

        withdraw_name = request.POST["withdraw_name"]
        withdraw_amount = request.POST["withdraw_amount"]
        wallet_id = request.POST.get("wallet_id", None)
        account_no = request.POST.get("account_no", None)
        ifsc_code = request.POST.get("ifsc_code", None)

        if float(withdraw_amount) < 10:

            messages.info(request, "minimum amount is 10")
            return redirect("/withdraw")

        user_plan = models.User_plan.objects.get(user=request.user)

        if float(withdraw_amount) > float(user_plan.user_profit):

            messages.error(request, "insufficient fund")
            return redirect("/withdraw")

        withdraw = models.Withdraw()
        withdraw.user = request.user
        withdraw.withdraw_amount = withdraw_amount
        withdraw.account_name = withdraw_name
        withdraw.account_no = account_no
        withdraw.wallet_id = wallet_id
        withdraw.ifsc_code = ifsc_code
        withdraw.withdraw_status = "pending"
        withdraw.save()

        return redirect("/dashboard")

class Refer_view(View):
    
    def get(self,request):

        context = {
            "refer": models.Referral.objects.get(user=request.user),
            "members": models.Referral.objects.get(user=request.user).direct.all(),
        }

        return render(request, 'user/refer.html', context=context)
    
    def post(self, request):

        referral_id = request.POST["referred_id"]

        if not models.Referral.objects.filter(referral_id=referral_id):

            return redirect("/refer")

        referrer = models.Referral.objects.get(user=request.user)
        referred = models.Referral.objects.get(referral_id=referral_id)

        referrer.referred_user = referred.user
        referrer.save()
        referred.direct.add(request.user)
        referred.save()

        return redirect("/refer")

class UpdateReferDetails_view(View):

    def get(self, request):

        return render(request, "mod/referplan.html", {"details": models.ReferralDetails.objects.get(id=1)})

class Payment_view(View):
    
    def get(self,request):

        return render(request, 'user/payment.html')
    
    def post(self, request):
        
        transaction_name = request.POST["transaction_name"]
        transaction_id = request.POST["transaction_id"]
        amount = request.POST["amount"]

        
        if float(amount) < 100:
            messages.info(request, "minimum amount is 100")
            return render(request, "user/payment.html")
        if float(str(float(amount)/50).split(".")[1]) > 0:
            messages.info(request, "only multiples of 50")
            return render(request, "user/payment.html")
        else:

            payment = models.Payment()
            payment.user = request.user
            payment.transaction_name = transaction_name
            payment.transaction_id = transaction_id
            payment.transaction_amount = amount
            payment.transaction_status = "pending"
            payment.save()

            messages.info(request, "payment is requested")
            return redirect("/dashboard")
    
class Profile_view(View):
    
    def get(self,request, **kwargs):

        context = {
            "user_plan": models.User_plan.objects.get(user=request.user),
        }

        if "id" in kwargs:
            return render(request, "user/updateprofile.html", context=context)

        return render(request, 'user/profile.html', context=context)
    
    def post(self, request, **kwargs):

        fname = request.POST["fname"]
        lname = request.POST["lname"]
        uname = request.POST["uname"]
        email = request.POST["up_email"]
        contact = request.POST["contact"]

        user = models.User.objects.get(id=request.user.id)
        user.first_name = fname
        user.last_name = lname
        user.username = uname
        user.email = email
        user.save()
        user_plan = models.User_plan.objects.get(user=user)
        user_plan.contact = contact
        user_plan.save()

        return redirect("/profile")

class History_view(View):
    
    def get(self,request, **kwargs):

        action = kwargs["action"]

        if request.user.is_superuser:
            
            user = models.User.objects.get(id=kwargs['id'])
            context = {
                "payments": models.Payment.objects.filter(user=user),
                "withdraws":  models.Withdraw.objects.filter(user=user),
                "addprofits": models.Addprofit.objects.filter(user=user),
                "action": action,
                "user": user,
                "admin": True,
            }

            return render(request, "mod/history.html", context=context)

        context = {
            "payments": models.Payment.objects.filter(user=request.user),
            "withdraws": models.Withdraw.objects.filter(user=request.user),
            "addprofits": models.Addprofit.objects.filter(user=request.user),
            "action": action,
        }

        return render(request, 'user/history.html', context=context)


class ModDashboard_view(View):
    
    def get(self,request, **kwargs):

        if not request.user.is_superuser:
            raise Http404()
        
        chats = []

        for member in models.User.objects.all():
            if not member.is_superuser:
                last = None
                if models.Chat.objects.filter(user=member).exists():
                    last = list(models.Chat.objects.filter(user=member))[-1]
                lst = [member, last]

                chats.append(lst)

        context = {
            "chats": chats,
        }
        return render(request, 'mod/index.html', context=context)

class ModMembers_view(View):
    
    def get(self, request, **kwargs):

        if not request.user.is_superuser:
            raise Http404

        if "status" in kwargs:
            
            context = {
                "members": [[member, referred] for member in models.User_plan.objects.filter(user_status=kwargs["status"]) for referred in models.Referral.objects.filter(user=member.user)],
            }

            return render(request, 'mod/membersactive.html', context=context)

        context = {
            "members": [ [user, referred, user_plan] for user in User.objects.all() if not user.is_superuser for referred in models.Referral.objects.filter(user=user) for user_plan in models.User_plan.objects.filter(user=user)],
        }

        return render(request, 'mod/members.html', context=context)


class ModPayments_view(View):
    
    def get(self,request, **kwargs):

        if not request.user.is_superuser:
            raise Http404

        action = kwargs["action"]
        
        if "id" in kwargs:
            
            payment_id = kwargs["id"]

            payment = models.Payment.objects.get(id=payment_id)
            if action == "approve":
                if payment.transaction_status == "Approved":
                    
                    messages.error(request, "already approved")
                    return redirect("/moderator/payments/approved")
                
                if models.User_plan.objects.filter(user=payment.user).exists() == True:

                    user_plan = models.User_plan.objects.get(user=payment.user)
                    user_plan.invested_amount = str(float(user_plan.invested_amount) + float(payment.transaction_amount))
                    plan = self.get_plan(user_plan.invested_amount)
                    user_plan.plan = plan
                    user_plan.user_status = "Active"
                    if not user_plan.user.is_active:
                        user_plan.user.is_active = True
                    user_plan.save()

                    self.add_referral_profit(user_plan.user, payment.transaction_amount)


                payment.transaction_status = "approved"
                payment.save()

                messages.success(request, "payment approved")
                return redirect("/moderator/payments/approved")

            elif action == "reject":

                payment.transaction_status = 'rejected'
                payment.save()

                messages.success(request, "payment rejected")
                return redirect("/moderator/payments/rejected")

        
        context = {
            "payments": models.Payment.objects.filter(transaction_status=action),
            "action": action,
        }

        return render(request, "mod/payments.html", context=context)
        
    def get_plan(self, amount):

        plan_db = models.Plans.objects.all()
        for plan in plan_db:
            if float(amount) >= float(plan.plan_min_price) and float(amount) < float(plan.plan_max_price):
                return plan
            
    def add_referral_profit(self, user, amount):

        referral = models.Referral.objects.get(user=user)
        if referral.referred_user is not None:
            referral_1 = models.Referral.objects.get(user=referral.referred_user)
            user_plan_1 = models.User_plan.objects.get(user=referral.referred_user)
            addprofit = models.Addprofit()
            addprofit.user = user
            addprofit.plan = user_plan_1.plan
            addprofit.referral_profit = (float(amount)*(float(referral_1.referral_details.spot_percent_direct)/100))
            addprofit.save()
            user_plan = models.User_plan.objects.get(user=referral.referred_user)
            user_plan.user_referral_profit = float(user_plan.user_referral_profit) + (float(amount)*(float(referral_1.referral_details.spot_percent_direct)/100))
            user_plan.save()
            if referral_1.referred_user is not None:
                referral_2 = models.Referral.objects.get(user=referral_1.referred_user)
                user_plan_2 = models.User_plan.objects.get(user=referral_1.referred_user)
                addprofit = models.Addprofit()
                addprofit.user = user
                addprofit.plan = user_plan_2.plan
                addprofit.referral_profit = (float(amount)*(float(referral_2.referral_details.spot_percent_level_1)/100))
                addprofit.save()
                user_plan = models.User_plan.objects.get(user=referral_1.referred_user)
                user_plan.user_referral_profit = float(user_plan.user_referral_profit) + (float(amount)*(float(referral_2.referral_details.spot_percent_level_1)/100))
                user_plan.save()
                if referral_2.referred_user is not None:
                    referral_3 = models.Referral.objects.get(user=referral_2.referred_user)
                    user_plan_3 = models.User_plan.objects.get(user=referral_2.referred_user)
                    addprofit = models.Addprofit()
                    addprofit.user = user
                    addprofit.plan = user_plan_3.plan
                    addprofit.referral_profit = (float(amount)*(float(referral_3.referral_details.spot_percent_level_2)/100))
                    addprofit.save()
                    user_plan = models.User_plan.objects.get(user=referral_2.referred_user)
                    user_plan.user_referral_profit = float(user_plan.user_referral_profit) + (float(amount)*(float(referral_3.referral_details.spot_percent_level_2)/100))
                    user_plan.save()
                    if referral_3.referred_user is not None:
                        referral_4 = models.Referral.objects.get(user=referral_3.referred_user)
                        user_plan_4 = models.User_plan.objects.get(user=referral_3.referred_user)
                        addprofit = models.Addprofit()
                        addprofit.user = user
                        addprofit.plan = user_plan_4.plan
                        addprofit.referral_profit = (float(amount)*(float(referral_4.referral_details.spot_percent_level_3)/100))
                        addprofit.save()
                        user_plan = models.User_plan.objects.get(user=referral_3.referred_user)
                        user_plan.user_referral_profit = float(user_plan.user_referral_profit) + (float(amount)*(float(referral_4.referral_details.spot_percent_level_3)/100))
                        user_plan.save()

class ModWithdraw_view(View):
    
    def get(self,request, **kwargs):

        if not request.user.is_superuser:
            raise Http404

        if "id" in kwargs:

            withdraw_id = kwargs["id"]
            action = kwargs["action"]

            withdraw = models.Withdraw.objects.get(id=withdraw_id)

            if action == "done":
                
                user_plan = models.User_plan.objects.get(user=withdraw.user)
                user_plan.user_profit = str(float(user_plan.user_profit) - float(withdraw.withdraw_amount))
                user_plan.save()
                withdraw.withdraw_status = "done"
                withdraw.save()

                messages.success(request, "withdraw success")
                return redirect("/moderator/withdraw/done")
            
            elif action == "rejected":

                withdraw.withdraw_status = "rejected"
                withdraw.save()

                messages.success(request, "withdraw rejected")
                return redirect("/moderator/withdraw/rejected")

        status = kwargs["status"]
        context = {
            "withdraws": models.Withdraw.objects.filter(withdraw_status=status),
            "status": status,
        }

        return render(request, 'mod/withdraw.html', context=context)

class ModAddPlan_view(View):
    
    def get(self,request):

        if not request.user.is_superuser:
            raise Http404
        
        return render(request, 'mod/addplan.html')
    
    def post(self, request):

        if not request.user.is_superuser:
            raise Http404

        plan_name = request.POST["plan_name"]
        plan_min_percentage = request.POST["plan_min_percentage"]
        plan_max_percentage = request.POST["plan_max_percentage"]
        plan_min_price = request.POST["plan_min_price"]
        plan_max_price = request.POST["plan_max_price"]

        if self.get_plan(plan_min_price) is not None:

            messages.error(request, "plan alredy exists")
            return redirect("/moderator/plans")

        plan = models.Plans()
        plan.plan_name = plan_name
        plan.plan_min_percentage = plan_min_percentage
        plan.plan_max_percentage = plan_max_percentage
        plan.plan_min_price = plan_min_price
        plan.plan_max_price = plan_max_price
        plan.save()

        messages.success(request, "Plan created")
        return redirect("/moderator/plans")
    
    def get_plan(self, amount):

        plan_db = models.Plans.objects.all()
        for plan in plan_db:
            if float(amount) >= float(plan.plan_min_price) and float(amount) < float(plan.plan_max_price):
                return plan
            else:
                return None

    
class ModPlans_view(View):
    
    def get(self,request):

        if not request.user.is_superuser:
            raise Http404

        context = {
            "plans": models.Plans.objects.all()
        }

        return render(request, 'mod/plans.html', context=context)
    
class ModEditPlan_view(View):

    def get(self, request, plan_id):

        if not request.user.is_superuser:
            raise Http404

        context = {
            "plan": models.Plans.objects.get(id=plan_id),
            "edit": None,
        }
        return render(request, "mod/addplan.html", context=context)
    
    def post(self, request, plan_id):

        if not request.user.is_superuser:
            raise Http404
        
        plan_name = request.POST["plan_name"]
        plan_min_percentage = request.POST["plan_min_percentage"]
        plan_max_percentage = request.POST["plan_max_percentage"]
        plan_min_price = request.POST["plan_min_price"]
        plan_max_price = request.POST["plan_max_price"]

        plan = models.Plans.objects.get(id=plan_id)
        plan.plan_name = plan_name
        plan.plan_min_percentage = plan_min_percentage
        plan.plan_max_percentage = plan_max_percentage
        plan.plan_min_price = plan_min_price
        plan.plan_max_price = plan_max_price
        plan.save()

        messages.success(request, "Plan changed")
        return redirect("/moderator/plans")
    
class ModAddProfit_view(View):
    
    def get(self,request):

        if not request.user.is_superuser:
            raise Http404

        context = {
            "plans": models.Plans.objects.all(),
            "members": [member for member in models.User.objects.all() if not member.is_superuser]
        }

        return render(request, 'mod/addprofit.html', context=context)
    
    def post(self, request):

        if not request.user.is_superuser:
            raise Http404

        plan_name = request.POST.get("plan_name", None)
        percentage = request.POST.get("percentage", None)

        uname = request.POST.get("uname", None)
        amount = request.POST.get("amount", None)

        days = request.POST["days"]

        print(request.POST)
        
        if uname == None or len(uname) < 0:

            plan = models.Plans.objects.get(plan_name=plan_name)
            user_plans = models.User_plan.objects.filter(plan=plan)
            for user_plan in user_plans:

                profit = float(days)*(float(user_plan.invested_amount)*(float(percentage)/100))
                user_plan.user_profit = float(user_plan.user_profit) + profit
                user_plan.days = float(user_plan.days) + float(days)

                self.add_referral_profit(user_plan.user, profit)
                
                user_plan.total_profit = str(float(user_plan.user_profit) + float(user_plan.user_referral_profit))
                user_plan.save()

                addprofit = models.Addprofit()
                addprofit.user = user_plan.user
                addprofit.plan = plan
                addprofit.profit = profit
                addprofit.percentage = percentage
                addprofit.save()

        else:

            user = models.User.objects.get(username=uname)
            user_plan = models.User_plan.objects.get(user=user)
            user_plan.user_profit = float(user_plan.user_profit) + float(amount)
            user_plan.days = float(user_plan.days) + float(days)

            self.add_referral_profit(user, amount)

            user_plan.total_profit = str(float(user_plan.user_profit) + float(user_plan.user_referral_profit))
            user_plan.save()

            addprofit = models.Addprofit()
            addprofit.user = user
            addprofit.plan = user_plan.plan
            addprofit.profit = amount
            addprofit.save()

        messages.success(request, "profit added")
        return redirect("/moderator/addprofit")
    
    def add_referral_profit(self, user, amount):

        referral = models.Referral.objects.get(user=user)
        if referral.referred_user is not None:
            referral_1 = models.Referral.objects.get(user=referral.referred_user)
            user_plan_1 = models.User_plan.objects.get(user=referral.referred_user)
            addprofit = models.Addprofit()
            addprofit.user = user
            addprofit.plan = user_plan_1.plan
            addprofit.referral_profit = (float(amount)*(float(referral_1.referral_details.percent_direct)/100))
            addprofit.save()
            user_plan = models.User_plan.objects.get(user=referral.referred_user)
            user_plan.user_referral_profit = float(user_plan.user_referral_profit) + (float(amount)*(float(referral_1.referral_details.percent_direct)/100))
            user_plan.save()
            if referral_1.referred_user is not None:
                referral_2 = models.Referral.objects.get(user=referral_1.referred_user)
                user_plan_2 = models.User_plan.objects.get(user=referral_1.referred_user)
                addprofit = models.Addprofit()
                addprofit.user = user
                addprofit.plan = user_plan_2.plan
                addprofit.referral_profit = (float(amount)*(float(referral_2.referral_details.percent_level_1)/100))
                addprofit.save()
                user_plan = models.User_plan.objects.get(user=referral_1.referred_user)
                user_plan.user_referral_profit = float(user_plan.user_referral_profit) + (float(amount)*(float(referral_2.referral_details.percent_level_1)/100))
                user_plan.save()
                if referral_2.referred_user is not None:
                    referral_3 = models.Referral.objects.get(user=referral_2.referred_user)
                    user_plan_3 = models.User_plan.objects.get(user=referral_2.referred_user)
                    addprofit = models.Addprofit()
                    addprofit.user = user
                    addprofit.plan = user_plan_3.plan
                    addprofit.referral_profit = (float(amount)*(float(referral_3.referral_details.percent_level_2)/100))
                    addprofit.save()
                    user_plan = models.User_plan.objects.get(user=referral_2.referred_user)
                    user_plan.user_referral_profit = float(user_plan.user_referral_profit) + (float(amount)*(float(referral_3.referral_details.percent_level_2)/100))
                    user_plan.save()
                    if referral_3.referred_user is not None:
                        referral_4 = models.Referral.objects.get(user=referral_3.referred_user)
                        user_plan_4 = models.User_plan.objects.get(user=referral_3.referred_user)
                        addprofit = models.Addprofit()
                        addprofit.user = user
                        addprofit.plan = user_plan_4.plan
                        addprofit.referral_profit = (float(amount)*(float(referral_4.referral_details.percent_level_3)/100))
                        addprofit.save()
                        user_plan = models.User_plan.objects.get(user=referral_3.referred_user)
                        user_plan.user_referral_profit = float(user_plan.user_referral_profit) + (float(amount)*(float(referral_4.referral_details.percent_level_3)/100))
                        user_plan.save()

class ModMember_view(View):

    def get(self, request, id):

        if not request.user.is_superuser:
            raise Http404

        user = models.User.objects.get(id=id)

        context = {
            "member": models.User_plan.objects.get(user=user)
        }

        return render(request, "mod/member.html", context=context)
    
    def post(self, request, **kwargs):

        if not request.user.is_superuser:
            raise Http404

        uname = request.POST["uname"]
        user_profit = request.POST["user_profit"]
        user_referral_profit = request.POST["user_referral_profit"]

        user = models.User.objects.get(username=uname)
        user_plan = models.User_plan.objects.get(user=user)
        user_plan.user_profit = user_profit
        user_plan.user_referral_profit = user_referral_profit
        user_plan.total_profit = str(float(user_profit) + float(user_referral_profit))
        user_plan.save()

        messages.info(request, "changes applied")
        return redirect(f"/moderator/member/{user.id}")

class ModChat_view(View):

    def get(self, request, **kwargs):

        if not request.user.is_superuser:
            raise Http404

        if "id" in kwargs:
            user = models.User.objects.get(id=kwargs["id"])
        else:
            user = request.user
        
        context = {
            "chats": models.Chat.objects.filter(user=user)[::-1],
        }

        return render(request, "mod/chat.html", context=context)
    
    def post(self, request, **kwargs):

        if not request.user.is_superuser:
            raise Http404

        replay = request.POST["replay"]
        id = request.POST["chat_id"]

        chat = models.Chat.objects.get(id=id)
        chat.replay = replay
        chat.save()

        messages.success(request, "repalyed to message")
        return redirect(f"/moderator/chat/{kwargs['id']}")

