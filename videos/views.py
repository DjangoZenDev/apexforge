"""Videos views — library, detail, notes"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

from .models import Video, VideoCategory, VideoNote
from .forms import VideoForm, VideoNoteForm


@login_required
def video_library(request):
    qs = Video.objects.select_related("category", "team", "uploaded_by")
    if not request.user.can_manage:
        qs = qs.filter(Q(is_public=True) | Q(uploaded_by=request.user))
    category = request.GET.get("category")
    q = request.GET.get("q", "")
    if category:
        qs = qs.filter(category__name=category)
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(tags__icontains=q))
    paginator = Paginator(qs, 12)
    page = paginator.get_page(request.GET.get("page", 1))
    categories = VideoCategory.objects.all()
    return render(request, "videos/library.html", {
        "page": page,
        "categories": categories,
        "current_category": category,
    })


@login_required
def video_detail(request, pk):
    video = get_object_or_404(Video, pk=pk)
    if not request.user.can_manage and not video.is_public and video.uploaded_by != request.user:
        messages.error(request, _("Access denied."))
        return redirect("videos:library")
    # increment views
    Video.objects.filter(pk=pk).update(views=video.views + 1)
    notes = video.notes.select_related("created_by").prefetch_related("tagged_players")
    note_form = VideoNoteForm()
    return render(request, "videos/detail.html", {
        "video": video, "notes": notes, "note_form": note_form,
    })


@login_required
def video_upload(request):
    form = VideoForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        video = form.save(commit=False)
        video.uploaded_by = request.user
        video.save()
        messages.success(request, _("Video uploaded."))
        return redirect("videos:detail", pk=video.pk)
    return render(request, "videos/upload.html", {"form": form})


@login_required
def video_edit(request, pk):
    video = get_object_or_404(Video, pk=pk)
    form = VideoForm(request.POST or None, request.FILES or None, instance=video)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Video updated."))
        return redirect("videos:detail", pk=pk)
    return render(request, "videos/upload.html", {"form": form, "video": video})


@login_required
@require_POST
def add_note(request, video_pk):
    video = get_object_or_404(Video, pk=video_pk)
    form = VideoNoteForm(request.POST)
    if form.is_valid():
        note = form.save(commit=False)
        note.video = video
        note.created_by = request.user
        note.save()
        form.save_m2m()
        if request.htmx:
            notes = video.notes.select_related("created_by").prefetch_related("tagged_players")
            return render(request, "videos/partials/notes_list.html", {"notes": notes, "video": video})
        messages.success(request, _("Note added."))
    return redirect("videos:detail", pk=video_pk)


@login_required
def delete_note(request, pk):
    note = get_object_or_404(VideoNote, pk=pk)
    video_pk = note.video.pk
    note.delete()
    messages.success(request, _("Note deleted."))
    return redirect("videos:detail", pk=video_pk)
