from django.urls import path, include
from django.contrib.auth.decorators import login_required


from . import views

urlpatterns = [   
    path('', login_required(views.Index_view.as_view()), name='home'),

    path('dashboard/', login_required(views.Dashboard_view.as_view()), name='user_dashboard'),
    path('profit/', login_required(views.Profit_view.as_view()), name='profit'),
    path('refer/', login_required(views.Refer_view.as_view()), name='refer'),
    path('profile/', login_required(views.Profile_view.as_view()), name='profile'),
    path('profile/update/<int:id>', login_required(views.Profile_view.as_view()), name='profile_update'),
    path('history/<str:action>', login_required(views.History_view.as_view()), name='history'),
    
    path('withdraw/', login_required(views.Withdraw_view.as_view()), name='withdraw'),
    path('payment/', login_required(views.Payment_view.as_view()), name='payment'),
    path('plans/', login_required(views.Plans_view.as_view()), name='plans'),
    path('chat/', login_required(views.Chat_view.as_view()), name='chat'),

    path('moderator/dashboard/', login_required(views.ModDashboard_view.as_view()), name='mod_dashboard'),
    path('moderator/referral/details', login_required(views.UpdateReferDetails_view.as_view()), name='mod_refer'),
    path('moderator/members/', login_required(views.ModMembers_view.as_view()), name='mod_mambers'),
    path('moderator/members/<str:status>', login_required(views.ModMembers_view.as_view()), name='mod_active_member'),
    path('moderator/member/<int:id>', login_required(views.ModMember_view.as_view()), name='mod_member'),
    path('moderator/payments/<str:action>', login_required(views.ModPayments_view.as_view()), name='mod_payments'),
    path('moderator/payments/action/<str:action>/<int:id>', login_required(views.ModPayments_view.as_view()), name="mod_payments_approve"),
    path('moderator/withdraw/<str:status>', login_required(views.ModWithdraw_view.as_view()), name='mod_withdraw'),
    path('moderator/withdraw/action/<str:action>/<int:id>', login_required(views.ModWithdraw_view.as_view()), name='mod_withdraw_action'),
    path('moderator/addprofit/', login_required(views.ModAddProfit_view.as_view()), name='mod_add_profit'),
    path('moderator/addprofit/<str:action>', login_required(views.ModAddProfit_view.as_view()), name='mod_add_referal_profit'),
    path('moderator/addplan/', login_required(views.ModAddPlan_view.as_view()), name='mod_add_plan'),
    path('moderator/plans/', login_required(views.ModPlans_view.as_view()), name='mod_plans'),
    path('moderator/editplan/<int:plan_id>', login_required(views.ModEditPlan_view.as_view()), name='mod_edit_plan'),
    path('history/<int:id>/<str:action>', login_required(views.History_view.as_view()), name='mod_history'),
    path('moderator/chat/', login_required(views.ModChat_view.as_view()), name='mod_chat'),
    path('moderator/chat/<int:id>', login_required(views.ModChat_view.as_view()), name='mod_user_chat'),

    path('signup/', views.Signup_view.as_view(), name='signup'),
    path('login/', views.Login_view.as_view(), name='login'),
    path('logout/', login_required(views.Logout_view.as_view()), name='logout'),
    path('password/forgot/', views.ForgotPassword_view.as_view(), name='passw_forgot'),
    path('password/change/', login_required(views.ChangePassword_view.as_view()), name='passw_change'),
]