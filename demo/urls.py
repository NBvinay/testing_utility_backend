
from django.contrib import admin
from django.urls import path
from compareDB import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('compareSchema/', views.CompareSchema.as_view()),
    path('getTableNames/', views.GetTableNames.as_view()),
    path('getTableData/', views.GetTableData.as_view()),
    path('compareFiles/', views.CompareTwoFiles.as_view()),
    # path('sqlExecute/', views.SQLExecutor.as_view()),
    path('compareTwoData',views.CompareTwoData.as_view()),
]
