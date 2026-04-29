"""
Marketing views — news, announcements, campaigns, sponsor portal
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

from .models import NewsPost, Announcement, Campaign, SponsorPortal
from .forms import NewsPostForm, AnnouncementForm, CampaignForm


def news_list(request):
    posts = NewsPost.objects.filter(is_published=True).select_related("author")
    category = request.GET.get("category")
    q = request.GET.get("q", "")
    if category:
        posts = posts.filter(category=category)
    if q:
        posts = posts.filter(title__icontains=q)

    paginator = Paginator(posts, 12)
    page = paginator.get_page(request.GET.get("page", 1))
    featured = NewsPost.objects.filter(is_published=True, is_featured=True).first()

    if request.htmx:
        return render(request, "marketing/partials/news_cards.html", {"page": page})

    return render(request, "marketing/news.html", {
        "page": page, "featured": featured,
        "categories": NewsPost.Category.choices, "current_category": category,
    })


def news_detail(request, slug):
    post = get_object_or_404(NewsPost, slug=slug, is_published=True)
    post.views += 1
    post.save(update_fields=["views"])
    related = NewsPost.objects.filter(
        is_published=True, category=post.category,
    ).exclude(pk=post.pk)[:3]
    return render(request, "marketing/news_detail.html", {"post": post, "related": related})


@login_required
def news_create(request):
    form = NewsPostForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        if not post.slug:
            post.slug = slugify(post.title)[:300]
        if form.cleaned_data.get("publish_now"):
            post.publish()
        else:
            post.save()
        messages.success(request, _("Post saved."))
        return redirect("marketing:news_detail", slug=post.slug)
    return render(request, "marketing/news_form.html", {"form": form, "title": _("New Post")})


@login_required
def news_edit(request, slug):
    post = get_object_or_404(NewsPost, slug=slug)
    form = NewsPostForm(request.POST or None, request.FILES or None, instance=post)
    if request.method == "POST" and form.is_valid():
        p = form.save(commit=False)
        if form.cleaned_data.get("publish_now") and not p.is_published:
            p.publish()
        else:
            p.save()
        messages.success(request, _("Post updated."))
        return redirect("marketing:news_detail", slug=p.slug)
    return render(request, "marketing/news_form.html", {"form": form, "post": post, "title": _("Edit Post")})


@login_required
@require_POST
def news_delete(request, slug):
    post = get_object_or_404(NewsPost, slug=slug)
    post.delete()
    messages.success(request, _("Post deleted."))
    return redirect("marketing:news_list")


@login_required
def announcements(request):
    from django.utils import timezone
    active = Announcement.objects.filter(is_active=True).order_by("-created_at")
    form = AnnouncementForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        ann = form.save(commit=False)
        ann.created_by = request.user
        ann.save()
        messages.success(request, _("Announcement created."))
        return redirect("marketing:announcements")
    return render(request, "marketing/announcements.html", {"announcements": active, "form": form})


@login_required
def campaigns(request):
    camp_list = Campaign.objects.select_related("created_by").order_by("-created_at")
    return render(request, "marketing/campaigns.html", {"campaigns": camp_list})


@login_required
def campaign_create(request):
    form = CampaignForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        c = form.save(commit=False)
        c.created_by = request.user
        c.save()
        messages.success(request, _("Campaign created."))
        return redirect("marketing:campaigns")
    return render(request, "marketing/campaign_form.html", {"form": form})


@login_required
def campaign_detail(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk)
    return render(request, "marketing/campaign_detail.html", {"campaign": campaign})


def sponsor_portal(request):
    portals = SponsorPortal.objects.filter(is_visible=True).select_related("sponsorship").order_by("display_order")
    return render(request, "marketing/sponsor_portal.html", {"portals": portals})


@login_required
def announcement_edit(request, pk):
    ann = get_object_or_404(Announcement, pk=pk)
    form = AnnouncementForm(request.POST or None, instance=ann)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Announcement updated."))
        return redirect("marketing:announcements")
    return render(request, "marketing/announcement_form.html", {"form": form, "announcement": ann})


@login_required
@require_POST
def announcement_delete(request, pk):
    ann = get_object_or_404(Announcement, pk=pk)
    ann.delete()
    messages.success(request, _("Announcement deleted."))
    return redirect("marketing:announcements")


@login_required
def campaign_edit(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk)
    form = CampaignForm(request.POST or None, instance=campaign)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Campaign updated."))
        return redirect("marketing:campaign_detail", pk=pk)
    return render(request, "marketing/campaign_form.html", {"form": form, "campaign": campaign})
