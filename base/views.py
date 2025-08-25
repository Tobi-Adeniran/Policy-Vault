from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, ListView, DetailView, FormView, View
from django.urls import reverse_lazy, reverse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.db.models import Q

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import DeleteView
from django.urls import reverse_lazy

from .models import Department, Policy  # ensure Policy is imported


class CustomLoginView(LoginView):
    template_name = 'base/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        # Redirect to the departments list after login
        return reverse_lazy('dept')


class RegisterForm(FormView):
    template_name = 'base/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('dept')

    def form_valid(self, form):
        user = form.save()
        if user:
            login(self.request, user)
        return super().form_valid(form)

    def get(self, *args, **kwargs):
        # Prevent authenticated users from accessing registration
        if self.request.user.is_authenticated:
            return redirect('dept')
        return super().get(*args, **kwargs)


class Home(LoginRequiredMixin, ListView):
    model = Department
    context_object_name = 'departments'
    template_name = 'base/index.html'

    

def searchbar(request):
    query = request.GET.get('search-area', '').strip()
    departments = []
    policies = []

    if query:
        # Search Departments by name (and description if you added one)
        departments = Department.objects.filter(
            Q(department__icontains=query)
            # | Q(description__icontains=query)    # uncomment if you have a description field
        )

        # Search Policies by title or file name (document field)
        policies = Policy.objects.filter(
            Q(title__icontains=query) |
            Q(document__icontains=query)
        )

    return render(request, 'base/searchbar.html', {
        'search_input': query,
        'departments': departments,
        'policies': policies,
    })


class DepartmentView(LoginRequiredMixin, ListView):
    model = Department
    context_object_name = 'departments'
    template_name = 'base/departments_list.html'

class DepartmentPolicyListView(LoginRequiredMixin, ListView):
    model = Policy
    template_name = 'base/policies_list.html'
    context_object_name = 'policies'
    paginate_by = 6

    def get_queryset(self):
        self.department = get_object_or_404(Department, pk=self.kwargs['pk'])
        return Policy.objects.filter(department=self.department)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['department'] = self.department
        # Only IT Admins get add‑policy rights:
        ctx['can_add_policy'] = (
            self.request.user.is_authenticated
            and self.request.user.groups.filter(name='IT Admin').exists()
        )
        return ctx

class DepartmentDetail(LoginRequiredMixin, DetailView):
    model = Department
    context_object_name = 'department'
    template_name = 'base/policies_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch all policies related via related_name 'policies'
        context['policies'] = self.object.policies.all()
        return context


class DepartmentPoliciesPDFView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        department = get_object_or_404(Department, pk=pk)
        policies = department.policies.all()
        template = get_template('base/policies_pdf.html')
        html = template.render({'department': department, 'policies': policies})
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = (
            f'attachment; filename="{department.department}_policies.pdf"'
        )
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('Error generating PDF', status=500)
        return response


class PolicyCreateView(LoginRequiredMixin, CreateView):
    model = Policy
    fields = ['department', 'title', 'document']
    template_name = 'base/policy_form.html'

    def get_initial(self):
        initial = super().get_initial()
        dept_pk = self.kwargs.get('pk')
        if dept_pk:
            initial['department'] = get_object_or_404(Department, pk=dept_pk)
        return initial

    def form_valid(self, form):
        # Ensure the uploaded file is saved
        response = super().form_valid(form)
        return response

    def get_success_url(self):
        return reverse('department_policies_list', args=[self.object.department.pk])

class PolicyDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Policy
    template_name = 'base/policy_confirm_delete.html'

    def test_func(self):
        # only allow users in IT Admin group
        return self.request.user.groups.filter(name='IT Admin').exists()

    def get_success_url(self):
        # redirect back to this policy's department list
        dept_id = self.object.department.pk
        return reverse_lazy('department_policies_list', args=[dept_id])