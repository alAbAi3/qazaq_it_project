from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Қолданушы")
    bio = models.TextField(blank=True, null=True, verbose_name="Өзі туралы")
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png', verbose_name="Аватар")

    def __str__(self):
        return f"{self.user.username} профилі"

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профильдер"

class Course(models.Model):
    title = models.CharField(max_length=200, verbose_name="Курс атауы")
    description = models.TextField(verbose_name="Сипаттамасы")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Бағасы")
    image = models.ImageField(upload_to='course_images/', blank=True, null=True, verbose_name="Суреті")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Құрылған уақыты")
    

    enrolled_users = models.ManyToManyField(User, related_name='purchased_courses', blank=True, verbose_name="Сатып алғандар")
    views = models.IntegerField(default=0, verbose_name="Қаралым саны")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курстар"
        ordering = ['-created_at']

class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('Жұмыс', 'Жұмыс'),
        ('Стажировка', 'Стажировка'),
    ]
    title = models.CharField(max_length=255, verbose_name="Позиция атауы")
    company = models.CharField(max_length=200, verbose_name="Компания")
    description = models.TextField(verbose_name="Талаптар мен сипаттама")
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, verbose_name="Түрі")
    location = models.CharField(max_length=150, verbose_name="Орналасқан жері")
    published_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.company})"

    class Meta:
        verbose_name = "Жұмыс/Стажировка"
        verbose_name_plural = "Жұмыс/Стажировкалар"
        ordering = ['-published_at']

class FavoriteCourse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Қолданушы")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="Курс")

    def __str__(self):
        return f"{self.user.username} - {self.course.title}"

    class Meta:
        verbose_name = "Сүйікті курс"
        verbose_name_plural = "Сүйікті курстар"
        unique_together = ('user', 'course')

class Lesson(models.Model):
    course = models.ForeignKey(Course, related_name='lessons', on_delete=models.CASCADE, verbose_name="Курс")
    title = models.CharField(max_length=200, verbose_name="Сабақ тақырыбы")
    order = models.PositiveIntegerField(verbose_name="Реттік нөмірі")
    content = RichTextField(verbose_name="Сабақтың мазмұны", blank=True, null=True)
    youtube_url = models.URLField(verbose_name="YouTube видеосының сілтемесі", blank=True, null=True)

    class Meta:
        verbose_name = "Сабақ"
        verbose_name_plural = "Сабақтар"
        ordering = ['order'] # Сабақтарды реттік нөмірі бойынша сұрыптау

    def __str__(self):
        return f"{self.order}. {self.title}"

    def get_youtube_embed_url(self):
        """YouTube сілтемесін bepul.kz сілтемесіне айналдырады."""
        if self.youtube_url:
            # https://www.youtube.com/watch?v=VIDEO_ID -> https://www.youtube.com/embed/VIDEO_ID
            video_id = self.youtube_url.split('v=')[-1].split('&')[0]
            return f"https://www.youtube.com/embed/{video_id}"
        return None
    

class Partner(models.Model):
    name = models.CharField(max_length=100, verbose_name="Серіктес аты")
    logo = models.ImageField(upload_to='partner_logos/', verbose_name="Логотипі")
    url = models.URLField(verbose_name="Сайтқа сілтеме", blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Серіктес"
        verbose_name_plural = "Серіктестер"

class ScheduleEvent(models.Model):
    EVENT_TYPE_CHOICES = [
        ('Вебинар', 'Вебинар'),
        ('Курс басталуы', 'Курс басталуы'),
        ('Мастер-класс', 'Мастер-класс'),
    ]
    title = models.CharField(max_length=200, verbose_name="Оқиға атауы")
    description = models.TextField(verbose_name="Сипаттамасы", blank=True, null=True)
    event_date = models.DateTimeField(verbose_name="Өтетін уақыты")
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES, verbose_name="Оқиға түрі")
    related_course = models.ForeignKey(Course, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Байланысты курс")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Оқиға"
        verbose_name_plural = "Оқиғалар кестесі"
        ordering = ['event_date']

class JobApplication(models.Model):
    job = models.ForeignKey('Job', on_delete=models.CASCADE, related_name='applications')
    applicant_name = models.CharField(max_length=100, verbose_name="Үміткердің аты-жөні")
    applicant_email = models.EmailField(verbose_name="Email")
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Телефон нөмірі")
    cover_letter = models.TextField(blank=True, null=True, verbose_name="Хат (Cover Letter)")
    resume = models.FileField(upload_to='resumes/', verbose_name="Түйіндеме (Резюме)")
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.applicant_name} - {self.job.title}"

    class Meta:
        verbose_name = "Жұмысқа өтініш"
        verbose_name_plural = "Жұмысқа өтініштер"
        ordering = ['-submitted_at']