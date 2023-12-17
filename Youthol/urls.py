from django.urls import path

from . import views

urlpatterns = [
    path("SignIn/", views.SignIn),
    path("SignUp/", views.SignUp),
    path("getUserInfo/", views.GetUserInfo),
    path("getYoutholerInfo/", views.getYoutholerInfo),
    path("addDuty/", views.addDuty),
    path("StartDuty/", views.StartDuty),
    path("FinishDuty/", views.FinishDuty),
    path("getTodayDuty/", views.getTodayDuty),
    path("CheckDuty/", views.CheckDuty),
    path("GetAllDuty/", views.GetAllDuty),
    path("GetTotalDutyInRange/", views.GetTotalDutyInRange),
    path("GetAllYoutholer/", views.GetAllYoutholer),
    path("GetSingleTotalDuty/", views.GetSingleTotalDuty),
    path("modifySingleYoutholInfo/", views.modifySingleYoutholInfo),
    path("deletYoutholer/", views.deletYoutholer),
    path("addOneYoutholer/", views.addOneYoutholer),
    path("getSingleDutyTime/", views.getSingleDutyTime),
    path("applyDutyLeave/", views.applyDutyLeave),
    path("getSingleLeaveRecord/", views.getSingleLeaveRecord),
]