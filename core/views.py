from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Course, Lesson, Job
from .forms import UserRegisterForm
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from .models import Profile
from .models import Course, Lesson, Job, FavoriteCourse 
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Course, Job, Partner
from django.utils import timezone
from .models import ScheduleEvent 
# БҰЛ ДҰРЫС ЖОЛ
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models.functions import TruncDay
from django.db.models import Count
import json
from .models import Job # JobApplication моделін импорттауды ұмытпаңыз
from .forms import JobApplicationForm

def index(request):
    courses = Course.objects.all().order_by('-created_at')[:3] # Соңғы 3 курсты аламыз
    context = {
        'courses': courses,
    }
    return render(request, 'index.html', context)

def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    course.views += 1
    course.save()
    lessons = course.lessons.all() # related_name арқылы сабақтарды аламыз
    context = {
        'course': course,
        'lessons': lessons,
    }
    return render(request, 'course_detail.html', context)


def lesson_detail(request, course_pk, lesson_pk):
    lesson = get_object_or_404(Lesson, course__pk=course_pk, pk=lesson_pk)
    context = {
        'lesson': lesson
    }
    return render(request, 'lesson_detail.html', context)

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Құттықтаймыз, {username}! Сіздің аккаунтыңыз сәтті құрылды. Енді жүйеге кіре аласыз.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})


def course_list(request):
    courses = Course.objects.all().order_by('-created_at')
    context = {
        'courses': courses
    }
    return render(request, 'course_list.html', context)

def job_list(request):
    jobs = Job.objects.all().order_by('-published_at')
    context = {
        'jobs': jobs
    }
    return render(request, 'job_list.html', context)

# core/views.py

@login_required
def profile(request):
    Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, 
                                   request.FILES,
                                   instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Сіздің профиліңіз сәтті жаңартылды!')
            return redirect('profile')

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    # 👇 САТЫП АЛЫНҒАН КУРСТАРДЫ АЛАМЫЗ
    purchased_courses = request.user.purchased_courses.all()

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'purchased_courses': purchased_courses # 👈 КОНТЕКСТКЕ ҚОСАМЫЗ
    }

    return render(request, 'profile.html', context)

# course_detail функциясының толық дұрыс нұсқасы
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    lessons = course.lessons.all()
    
    is_enrolled = False
    is_favorite = False
    
    if request.user.is_authenticated:
        is_enrolled = course.enrolled_users.filter(id=request.user.id).exists()
        is_favorite = FavoriteCourse.objects.filter(user=request.user, course=course).exists()

    context = {
        'course': course,
        'lessons': lessons,
        'is_enrolled': is_enrolled,
        'is_favorite': is_favorite,
    }
    return render(request, 'course_detail.html', context)

# enroll_course функциясы
@login_required
def enroll_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    course.enrolled_users.add(request.user)
    return redirect('course_detail', pk=course.pk)

# toggle_favorite функциясы
@login_required
def toggle_favorite(request, pk):
    course = get_object_or_404(Course, pk=pk)
    fav, created = FavoriteCourse.objects.get_or_create(user=request.user, course=course)
    
    if not created:
        fav.delete()
        
    return redirect('course_detail', pk=course.pk)

@login_required
def my_favorites(request):
    # Пайдаланушының сүйікті деп белгілеген барлық жазбаларын аламыз
    favorite_entries = FavoriteCourse.objects.filter(user=request.user)
    # Сол жазбалардан курстардың өзін бөліп аламыз
    favorite_courses = [entry.course for entry in favorite_entries]
    
    context = {
        'courses': favorite_courses
    }
    return render(request, 'my_favorites.html', context)

@login_required
def checkout(request, pk):
    course = get_object_or_404(Course, pk=pk)

    if request.method == 'POST':
        course.enrolled_users.add(request.user)
        return redirect('purchase_success', pk=course.pk)

    context = {
        'course': course
    }
    return render(request, 'checkout.html', context)

@login_required
def purchase_success(request, pk):
    course = get_object_or_404(Course, pk=pk)
    context = {
        'course': course
    }
    return render(request, 'purchase_success.html', context)


def job_list(request):
    jobs = Job.objects.all().order_by('-published_at')

    # Фильтр үшін дерекқордан бірегей мәндерді аламыз
    locations = Job.objects.values_list('location', flat=True).distinct().order_by('location')
    job_types = Job.objects.values_list('job_type', flat=True).distinct().order_by('job_type')

    # GET-сұраныстан параметрлерді аламыз
    query = request.GET.get('q')
    selected_location = request.GET.get('location')
    selected_job_type = request.GET.get('job_type')

    # Егер параметрлер бар болса, фильтрді қолданамыз
    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) | 
            Q(company__icontains=query) |
            Q(description__icontains=query)
        )
    
    if selected_location and selected_location != 'Барлық қала':
        jobs = jobs.filter(location=selected_location)

    if selected_job_type and selected_job_type != 'Барлық түрі':
        jobs = jobs.filter(job_type=selected_job_type)

    context = {
        'jobs': jobs,
        'locations': locations,
        'job_types': job_types,
        'query_val': query, # Таңдалған мәндерді шаблонға қайта жібереміз
        'location_val': selected_location,
        'job_type_val': selected_job_type,
    }
    return render(request, 'job_list.html', context)

def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk)
    context = {
        'job': job
    }
    return render(request, 'job_detail.html', context)


def job_list(request):
    jobs_list = Job.objects.all().order_by('-published_at')

    locations = Job.objects.values_list('location', flat=True).distinct().order_by('location')
    job_types = Job.objects.values_list('job_type', flat=True).distinct().order_by('job_type')

    query = request.GET.get('q')
    selected_location = request.GET.get('location')
    selected_job_type = request.GET.get('job_type')

    if query:
        jobs_list = jobs_list.filter(
            Q(title__icontains=query) | 
            Q(company__icontains=query) |
            Q(description__icontains=query)
        )
    
    if selected_location and selected_location != 'Барлық қала':
        jobs_list = jobs_list.filter(location=selected_location)

    if selected_job_type and selected_job_type != 'Барлық түрі':
        jobs_list = jobs_list.filter(job_type=selected_job_type)

    # --- ПАГИНАЦИЯ ЛОГИКАСЫ ---
    paginator = Paginator(jobs_list, 6) # Әр бетте 6 жұмыстан көрсетеміз
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Фильтр параметрлерін пагинация сілтемелерінде сақтау үшін
    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']
    
    context = {
        'page_obj': page_obj, # jobs орнына page_obj жібереміз
        'query_params': query_params.urlencode(), # URL параметрлерін жібереміз
        'locations': locations,
        'job_types': job_types,
        'query_val': query,
        'location_val': selected_location,
        'job_type_val': selected_job_type,
    }
    return render(request, 'job_list.html', context)

def index(request):
    courses = Course.objects.all().order_by('-created_at')[:3]
    partners = Partner.objects.all() # Барлық серіктестерді аламыз
    context = {
        'courses': courses,
        'partners': partners, # Контекстке қосамыз
    }
    return render(request, 'index.html', context)


def schedule(request):
    # Тек болашақтағы немесе дәл қазір басталатын оқиғаларды аламыз
    events = ScheduleEvent.objects.filter(event_date__gte=timezone.now()).order_by('event_date')
    
    context = {
        'events': events
    }
    return render(request, 'schedule.html', context)

@staff_member_required # Бұл бетке тек админ/стафф кіре алады
def dashboard(request):
    # 1-график: Ең көп қаралған 10 курс
    top_courses = Course.objects.all().order_by('-views')[:10]
    course_labels = [course.title for course in top_courses]
    course_views_data = [course.views for course in top_courses]

    # 2-график: Соңғы 30 күндегі тіркелулер
    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
    registrations = User.objects.filter(date_joined__gte=thirty_days_ago) \
        .annotate(day=TruncDay('date_joined')) \
        .values('day') \
        .annotate(count=Count('id')) \
        .order_by('day')
        
    reg_labels = [reg['day'].strftime('%d %b') for reg in registrations]
    reg_data = [reg['count'] for reg in registrations]

    context = {
        'course_labels': json.dumps(course_labels),
        'course_views_data': json.dumps(course_views_data),
        'reg_labels': json.dumps(reg_labels),
        'reg_data': json.dumps(reg_data),
    }
    return render(request, 'dashboard.html', context)

@staff_member_required
def dashboard(request):
    # 1. Негізгі көрсеткіштер (KPI)
    total_users = User.objects.count()
    total_courses = Course.objects.count()
    total_jobs = Job.objects.count()
    # enrolled_users.through.objects.count() - бұл барлық "сатып алу" санын санайды
    total_enrollments = Course.enrolled_users.through.objects.count()

    # 2. Соңғы 5 тіркелген пайдаланушы
    recent_users = User.objects.order_by('-date_joined')[:5]

    # 3. Графиктер үшін деректер (бұрынғы код)
    # 1-график: Ең көп қаралған 10 курс
    top_courses = Course.objects.all().order_by('-views')[:10]
    course_labels = [course.title for course in top_courses]
    course_views_data = [course.views for course in top_courses]

    # 2-график: Соңғы 30 күндегі тіркелулер
    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
    registrations = User.objects.filter(date_joined__gte=thirty_days_ago) \
        .annotate(day=TruncDay('date_joined')) \
        .values('day') \
        .annotate(count=Count('id')) \
        .order_by('day')
        
    reg_labels = [reg['day'].strftime('%d %b') for reg in registrations]
    reg_data = [reg['count'] for reg in registrations]

    context = {
        # KPI үшін
        'total_users': total_users,
        'total_courses': total_courses,
        'total_jobs': total_jobs,
        'total_enrollments': total_enrollments,
        # Соңғы тіркелгендер үшін
        'recent_users': recent_users,
        # Графиктер үшін
        'course_labels': json.dumps(course_labels),
        'course_views_data': json.dumps(course_views_data),
        'reg_labels': json.dumps(reg_labels),
        'reg_data': json.dumps(reg_data),
    }
    return render(request, 'dashboard.html', context)

@login_required
def toggle_favorite(request, pk):
    course = get_object_or_404(Course, pk=pk)
    fav, created = FavoriteCourse.objects.get_or_create(user=request.user, course=course)
    
    if not created:
        fav.delete()
        messages.success(request, f"'{course.title}' курсы сүйіктілер тізімінен алынды.")
    else:
        messages.success(request, f"'{course.title}' курсы сүйіктілер тізіміне қосылды.")

    # Пайдаланушыны қай беттен келсе, сол бетке қайта бағыттау
    return redirect(request.META.get('HTTP_REFERER', 'index'))

@login_required
def my_courses(request):
    # Пайдаланушының purchased_courses (сатып алған курстары) тізімін аламыз.
    purchased_courses = request.user.purchased_courses.all().order_by('-created_at')
    context = {
        'courses': purchased_courses
    }
    return render(request, 'my_courses.html', context)


def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk)
    
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.save()
            
            # TODO: Email жіберу логикасын осында қосуға болады
            
            messages.success(request, 'Сіздің өтінішіңіз сәтті жіберілді!')
            return redirect('job_detail', pk=job.pk)
    else:
        form = JobApplicationForm()

    context = {
        'job': job,
        'form': form
    }
    return render(request, 'job_detail.html', context)