from django.urls import path
from django.conf import settings
from django.conf.urls.static import static


from .views import (
    DepartmentView, DepartmentDetail, Policy, Home,
    CustomLoginView, RegisterForm,
    DepartmentPoliciesPDFView, PolicyCreateView, DepartmentPolicyListView, PolicyDeleteView
)
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('register/', RegisterForm.as_view(), name='register'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('', Home.as_view(), name='index'),
    path('searchbar/', views.searchbar, name='searchbar'),
    path('departments/', DepartmentView.as_view(), name='dept'),
    path('departments/<int:pk>/', DepartmentDetail.as_view(), name='department_detail'),
    path('departments/<int:pk>/policies/', DepartmentPolicyListView.as_view(), name='department_policies_list'), 
    path('departments/<int:pk>/policies/pdf/', DepartmentPoliciesPDFView.as_view(), name='department_policies_pdf'),
    path('departments/<int:pk>/policies/add/', PolicyCreateView.as_view(), name='policy_add'),
    path('policies/<int:pk>/delete/', PolicyDeleteView.as_view(), name='policy_delete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)