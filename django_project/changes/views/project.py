import logging
logger = logging.getLogger(__name__)

# noinspection PyUnresolvedReferences
import logging
logger = logging.getLogger(__name__)

from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.views.generic import (
    ListView,
    CreateView,
    DeleteView,
    DetailView,
    UpdateView,
    RedirectView,
    TemplateView)

from django.http import HttpResponseRedirect
from braces.views import LoginRequiredMixin, StaffuserRequiredMixin
from pure_pagination.mixins import PaginationMixin

from ..models import Project, Category, Version, Entry
from ..forms import ProjectForm, CategoryForm, VersionForm, EntryForm


class ProjectMixin(object):
    model = Project  # implies -> queryset = Entry.objects.all()
    form_class = ProjectForm


class ProjectCreateUpdateMixin(ProjectMixin, LoginRequiredMixin):
    def get_context_data(self, **kwargs):
        context = super(ProjectMixin, self).get_context_data(**kwargs)
        return context

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class ProjectListView(ProjectMixin, PaginationMixin, ListView):
    """List all approved projects"""
    context_object_name = 'projects'
    template_name = 'project/list.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(ProjectListView, self).get_context_data(**kwargs)
        context['num_projects'] = self.get_queryset().count()
        context['unapproved'] = False
        return context

    def get_queryset(self):
        projects_qs = Project.objects.all()
        return projects_qs


class ProjectDetailView(ProjectMixin, DetailView):
    context_object_name = 'project'
    template_name = 'project/detail.html'

    def get_context_data(self, **kwargs):
        context = super(ProjectDetailView, self).get_context_data(**kwargs)
        return context

    def get_queryset(self):
        projects_qs = Project.objects.all()
        return projects_qs

    def get_object(self, queryset=None):
        obj = super(ProjectDetailView, self).get_object(queryset)
        obj.request_user = self.request.user
        return obj


class ProjectDeleteView(ProjectMixin, DeleteView, LoginRequiredMixin):
    context_object_name = 'project'
    template_name = 'project/delete.html'

    def get_success_url(self):
        return reverse('project-list')

    def get_queryset(self):
        qs = Project.all_objects.all()
        if self.request.user.is_staff:
            return qs
        else:
            return qs.filter(creator=self.request.user)


class ProjectCreateView(ProjectCreateUpdateMixin, CreateView):
    context_object_name = 'project'
    template_name = 'project/create.html'

    def get_success_url(self):
        return reverse('pending-project-list')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()

        return HttpResponseRedirect(self.get_success_url())


class ProjectUpdateView(ProjectCreateUpdateMixin, UpdateView):
    context_object_name = 'project'
    template_name = 'project/update.html'

    def get_form_kwargs(self):
        kwargs = super(ProjectUpdateView, self).get_form_kwargs()
        return kwargs

    def get_queryset(self):
        qs = Project.objects
        if self.request.user.is_staff:
            return qs
        else:
            return qs.filter(creator=self.request.user)

    def get_success_url(self):
        return reverse('project-list')


class PendingProjectListView(
        ProjectMixin, PaginationMixin, ListView, StaffuserRequiredMixin):
    """List all users unapproved projects - staff users see all unapproved."""
    context_object_name = 'projects'
    template_name = 'project/list.html'
    paginate_by = 10

    def get_queryset(self):
        projects_qs = Project.unapproved_objects.all()
        if self.request.user.is_staff:
            return projects_qs
        else:
            return projects_qs.filter(creator=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(PendingProjectListView, self).get_context_data(**kwargs)
        context['num_projects'] = self.get_queryset().count()
        context['unapproved'] = True
        return context

    def get_queryset(self):
        projects_qs = Project.unapproved_objects.all()
        return projects_qs


class ApproveProjectView(ProjectMixin, StaffuserRequiredMixin, RedirectView):
    permanent = False
    query_string = True
    pattern_name = 'pending-project-list'

    def get_redirect_url(self, pk):
        projects_qs = Project.unapproved_objects.all()
        project = get_object_or_404(projects_qs, pk=pk)
        project.approved = True
        project.save()
        return reverse(self.pattern_name)

