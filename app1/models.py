from django.db import models

class Person(models.Model):  # Renamed class to follow Python class naming conventions
    userId = models.AutoField(primary_key=True)  # Auto-increment primary key
    userName = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=255)  # Store hashed passwords
    idProof = models.FileField(upload_to='id_proofs/', null=True, blank=True)  # File upload for ID proof

    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('User', 'User'),
        ('Manager', 'Manager'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='User')

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')

    createdDate = models.DateTimeField(auto_now_add=True)  # Set on creation
    updatedDate = models.DateTimeField(auto_now=True)  # Updated on every save

    def __str__(self):
        return self.userName


class Feed(models.Model):
    TYPE_CHOICES = [
        ('request', 'Request'),
        ('donation', 'Donation'),
    ]

    URGENCY_CHOICES = [
        ('urgent', 'Urgent'),
        ('standard', 'Standard'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    category = models.CharField(max_length=50)
    group = models.CharField(max_length=50, null=True)
    urgency = models.CharField(max_length=10, choices=URGENCY_CHOICES)
    user = models.ForeignKey(Person, on_delete=models.CASCADE)  # Updated reference to `Person`
    time_posted = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    content = models.TextField()
    status = models.CharField(max_length=20)
    date_posted = models.DateField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Interaction(models.Model):
    id = models.AutoField(primary_key=True)
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE, related_name="interactions")
    likes = models.PositiveIntegerField(default=0)
    shares = models.PositiveIntegerField(default=0)
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Interaction on {self.feed.title}"

class FeedRequest(models.Model):
    id = models.AutoField(primary_key=True)
    feedId = models.ForeignKey(Feed, on_delete=models.CASCADE, related_name='feed_requests')
    secondPersonId = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='feed_requests')
    requestedDate = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    updatedDate = models.DateTimeField(auto_now=True)
    message = models.TextField(blank=True, null=True)  # New field to store the message

    def __str__(self):
        return f"Request {self.id} for Feed {self.feedId} by {self.secondPersonId}"