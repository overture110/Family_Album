from django.db import models


class Album(models.Model):
    name = models.CharField(max_length=100)
    year = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-year']

    def __str__(self):
        return f"{self.name} ({self.year})"


class Photo(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='photos')
    image = models.FileField(upload_to='photos/%Y/%m/')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    taken_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-taken_date']

    def __str__(self):
        return self.title
