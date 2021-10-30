from django.db import models

STATUS = (
    (0,"Draft"),
    (1,"Publish")
)

class Author(models.Model):
    name = models.CharField(max_length=32)
    user = models.TextField(blank=True, null=True)

class Post(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete= models.CASCADE,related_name='blog_posts', blank=True, null=True)
    updated_on = models.DateTimeField(auto_now= True)
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=STATUS, default=0)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return self.title    
