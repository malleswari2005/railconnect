from django.db import models

class Station(models.Model):
    code = models.CharField(max_length=10, unique=True, db_index=True)
    name = models.CharField(max_length=120)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zone = models.CharField(max_length=10, default='NR')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"

    def save(self, *args, **kwargs):
        self.code = self.code.upper().strip()
        super().save(*args, **kwargs)

class Train(models.Model):
    TRAIN_TYPE_CHOICES = [
        ('RAJDHANI', 'Rajdhani Express'),
        ('SHATABDI', 'Shatabdi Express'),
        ('VANDE_BHARAT', 'Vande Bharat Express'),
        ('SUPERFAST', 'Superfast Express'),
        ('EXPRESS', 'Express / Mail'),
    ]

    train_number = models.CharField(max_length=10, unique=True, db_index=True)
    name = models.CharField(max_length=150)
    train_type = models.CharField(max_length=20, choices=TRAIN_TYPE_CHOICES, default='SUPERFAST')
    source_station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='originating_trains')
    destination_station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='terminating_trains')
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    runs_on_days = models.CharField(max_length=50, default='MON,TUE,WED,THU,FRI,SAT,SUN')
    distance_km = models.PositiveIntegerField(default=500)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['train_number']

    def __str__(self):
        return f"{self.train_number} - {self.name}"

    def runs_on_day(self, day_abbr):
        """day_abbr is three letter uppercase e.g. MON, TUE"""
        return day_abbr.upper() in [d.strip().upper() for d in self.runs_on_days.split(',')]

class TrainStop(models.Model):
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name='stops')
    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='train_stops')
    stop_order = models.PositiveIntegerField()
    arrival_time = models.TimeField(null=True, blank=True)
    departure_time = models.TimeField(null=True, blank=True)
    halt_minutes = models.PositiveIntegerField(default=2)
    distance_from_source_km = models.PositiveIntegerField(default=0)
    day_offset = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['stop_order']
        unique_together = [('train', 'stop_order'), ('train', 'station')]

    def __str__(self):
        return f"{self.train.train_number} - Stop #{self.stop_order}: {self.station.code}"

class TrainClass(models.Model):
    CLASS_CHOICES = [
        ('1A', 'AC First Class (1A)'),
        ('2A', 'AC 2 Tier (2A)'),
        ('3A', 'AC 3 Tier (3A)'),
        ('SL', 'Sleeper Class (SL)'),
        ('CC', 'AC Chair Car (CC)'),
        ('2S', 'Second Sitting (2S)'),
    ]

    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name='classes')
    class_code = models.CharField(max_length=5, choices=CLASS_CHOICES)
    class_name = models.CharField(max_length=50)
    base_fare = models.DecimalField(max_digits=8, decimal_places=2, default=100.00)
    per_km_rate = models.DecimalField(max_digits=5, decimal_places=2, default=1.20)
    total_coaches = models.PositiveIntegerField(default=2)
    seats_per_coach = models.PositiveIntegerField(default=72)

    class Meta:
        unique_together = [('train', 'class_code')]
        ordering = ['class_code']

    def __str__(self):
        return f"{self.train.train_number} - {self.class_code}"

    @property
    def total_seats(self):
        return self.total_coaches * self.seats_per_coach
