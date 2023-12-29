from django.urls import path

from . import views

urlpatterns = [
    # path("SignUp/", views.SignUp),
    # path("addDuty/", views.addDuty),
    # path("Create/", views.Create),
    # path("ClearNotFinishDuty/", views.ClearNotFinishDuty),

    path("SignIn/", views.SignIn),
    path("ChangePassword/", views.ChangePassword),
    path("GetUserInfo/", views.GetUserInfo), 
    path("GetYoutholerInfo/", views.getYoutholerInfo),
    path("CheckDuty/", views.CheckDuty),

    # 值班
    path("StartDuty/", views.StartDuty),
    path("FinishDuty/", views.FinishDuty),

    # 获取数据
    path("GetAllYoutholer/", views.GetAllYoutholer),
    
    path("GetTodayDuty/", views.getTodayDuty),
    path("GetSingleDutyTime/", views.getSingleDutyTime),
    path("GetAllDutyRecord/", views.GetAllDutyRecord),
    path("GetSingleTotalDuty/", views.GetSingleTotalDuty),
    path("GetTotalDutyInRange/", views.GetTotalDutyInRange),

    path("GetSingleDutyRecord/", views.getSingleDutyRecord),
    path("GetSingleLeaveRecord/", views.getSingleLeaveRecord),

    path("GetRoomBorrow/", views.GetRoomBorrow),

    # 修改数据
    path("ModifySingleYoutholInfo/", views.modifySingleYoutholInfo),
    path("DeletYoutholer/", views.deletYoutholer),
    path("AddOneYoutholer/", views.addOneYoutholer),
    path("ApplyDutyLeave/", views.applyDutyLeave),
]