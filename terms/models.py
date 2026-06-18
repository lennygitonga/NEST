from django.db import models
from django.contrib.auth.models import User


class TermsAndConditions(models.Model):
    version = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200, default='NEST Terms and Conditions')
    content = models.TextField()
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"v{self.version} — {'Active' if self.is_active else 'Inactive'}"

    def save(self, *args, **kwargs):
        # Only one version can be active at a time
        if self.is_active:
            TermsAndConditions.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Terms and Conditions'
        ordering = ['-created_at']


class UserTermsAcceptance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='terms_acceptances')
    terms = models.ForeignKey(TermsAndConditions, on_delete=models.CASCADE, related_name='acceptances')
    accepted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} accepted v{self.terms.version}"

    class Meta:
        unique_together = ('user', 'terms')