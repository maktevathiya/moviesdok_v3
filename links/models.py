from django.db import models
from django.contrib.auth.models import User

class Link(models.Model):
    QUALITY_CHOICES = [
        ('144p', '144p'),
        ('240p', '240p'),
        ('360p', '360p'),
        ('480p', '480p'),
        ('720p', '720p'),
        ('1080p', '1080p'),
        ('2k', '2k'),
        ('4k', '4k'),
        ('8k', '8k'),
    ]

    SITE_CHOICES = [
        ('website', 'Website'),
        ('telegram', 'Telegram'),
        ('gdrive', 'Google Drive'),
        ('mega', 'Mega'),
        ('dropbox', 'Dropbox'),
        ('4shared', '4shared'),
        ('zippyshare', 'Zippyshare'),
        ('other', 'Other File Sharing Service'),
    ]

    AUDIO_CHOICES = [
        ('original', 'Original'),
        ('fandubbed', 'Fandubbed'),
        ('english', 'English'),
        ('hindi', 'Hindi'),
        ('spanish', 'Spanish'),
        ('mandarin', 'Mandarin'),
        ('french', 'French'),
        ('german', 'German'),
        ('italian', 'Italian'),
        ('portuguese', 'Portuguese'),
        ('russian', 'Russian'),
        ('arabic', 'Arabic'),
        ('japanese', 'Japanese'),
        ('korean', 'Korean'),
        ('turkish', 'Turkish'),
        ('bengali', 'Bengali'),
        ('bulgarian', 'Bulgarian'),
        ('catalan', 'Catalan'),
        ('croatian', 'Croatian'),
        ('czech', 'Czech'),
        ('danish', 'Danish'),
        ('dutch', 'Dutch'),
        ('estonian', 'Estonian'),
        ('finnish', 'Finnish'),
        ('georgian', 'Georgian'),
        ('hebrew', 'Hebrew'),
        ('hungarian', 'Hungarian'),
        ('icelandic', 'Icelandic'),
        ('italian', 'Italian'),
        ('latvian', 'Latvian'),
        ('lithuanian', 'Lithuanian'),
        ('malay', 'Malay'),
        ('persian', 'Persian'),
        ('polish', 'Polish'),
        ('romanian', 'Romanian'),
        ('serbian', 'Serbian'),
        ('slovak', 'Slovak'),
        ('slovenian', 'Slovenian'),
        ('swahili', 'Swahili'),
        ('swedish', 'Swedish'),
        ('thai', 'Thai'),
        ('ukrainian', 'Ukrainian'),
        ('vietnamese', 'Vietnamese'),
        ('filipino', 'Filipino'),
        ('azerbaijani', 'Azeri'),

    ]

    SUBTITLE_CHOICES = [
        ('no_subtitles', 'No Subtitles'),
        ('english', 'English'),
        ('hindi', 'Hindi'),
        ('spanish', 'Spanish'),
        ('mandarin', 'Mandarin'),
        ('french', 'French'),
        ('german', 'German'),
        ('italian', 'Italian'),
        ('portuguese', 'Portuguese'),
        ('russian', 'Russian'),
        ('arabic', 'Arabic'),
        ('japanese', 'Japanese'),
        ('korean', 'Korean'),
        ('turkish', 'Turkish'),
        ('bengali', 'Bengali'),
        ('bulgarian', 'Bulgarian'),
        ('catalan', 'Catalan'),
        ('croatian', 'Croatian'),
        ('czech', 'Czech'),
        ('danish', 'Danish'),
        ('dutch', 'Dutch'),
        ('estonian', 'Estonian'),
        ('finnish', 'Finnish'),
        ('georgian', 'Georgian'),
        ('hebrew', 'Hebrew'),
        ('hungarian', 'Hungarian'),
        ('icelandic', 'Icelandic'),
        ('italian', 'Italian'),
        ('latvian', 'Latvian'),
        ('lithuanian', 'Lithuanian'),
        ('malay', 'Malay'),
        ('persian', 'Persian'),
        ('polish', 'Polish'),
        ('romanian', 'Romanian'),
        ('serbian', 'Serbian'),
        ('slovak', 'Slovak'),
        ('slovenian', 'Slovenian'),
        ('swahili', 'Swahili'),
        ('swedish', 'Swedish'),
        ('thai', 'Thai'),
        ('ukrainian', 'Ukrainian'),
        ('vietnamese', 'Vietnamese'),
        ('filipino', 'Filipino'),
        ('azerbaijani', 'Azeri'),
    ]

    DECODER_CHOICES = [
        ('H.264_8bit', 'H.264 (8-bit)'),
        ('H.264_10bit', 'H.264 (10-bit)'),
        ('H.265_8bit', 'H.265 (8-bit)'),
        ('H.265_10bit', 'H.265 (10-bit)'),
        ('H.265_12bit', 'H.265 (12-bit)'),
        ('VP8_8bit', 'VP8 (8-bit)'),
        ('VP9_8bit', 'VP9 (8-bit)'),
        ('VP9_10bit', 'VP9 (10-bit)'),
        ('AV1_8bit', 'AV1 (8-bit)'),
        ('AV1_10bit', 'AV1 (10-bit)'),
        ('AV1_12bit', 'AV1 (12-bit)'),
        ('MPEG-2_8bit', 'MPEG-2 (8-bit)'),
        ('ProRes_8bit', 'ProRes (8-bit)'),
        ('ProRes_10bit', 'ProRes (10-bit)'),
        ('ProRes_12bit', 'ProRes (12-bit)'),
        ('VP6_8bit', 'VP6 (8-bit)'),
    ]

    FORMAT_CHOICES = [
        ('WEB-DL', 'WEB-DL'),
        ('WEBRip', 'WEBRip'),
        ('HDRip', 'HDRip'),
        ('BluRay', 'BluRay'),
        ('BRRip', 'BRRip'),
        ('HDTV', 'HDTV'),
        ('HDTVRip', 'HDTVRip'),
        ('TVRip', 'TVRip'),
        ('BDRemux', 'BDRemux'),
        ('DVDRip', 'DVDRip'),
        ('Telesync', 'Telesync'),
        ('HDCAM', 'HDCAM'),
        ('CAM', 'CAM'),
        ('DVDScr', 'DVDScr'),
        ('Remux', 'Remux'),
        ('VOD', 'VOD'),
        ('PS3', 'PS3'),
    ]

    MEDIA_TYPE_CHOICES = [
        ('movie', 'Movie'),
        ('tv', 'TV Show'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tmdb_id = models.CharField(max_length=255)
    url = models.URLField()
    quality = models.CharField(max_length=10, choices=QUALITY_CHOICES)
    site = models.CharField(max_length=50, choices=SITE_CHOICES)
    size = models.CharField(max_length=20)
    audio = models.CharField(max_length=20, choices=AUDIO_CHOICES, blank=True, null=True)
    subtitles = models.CharField(max_length=20, choices=SUBTITLE_CHOICES, blank=True, null=True)
    decoder = models.CharField(max_length=50, choices=DECODER_CHOICES, blank=True, null=True)
    format = models.CharField(max_length=20, choices=FORMAT_CHOICES, blank=True, null=True)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES)
    season = models.CharField(max_length=10, blank=True, null=True)  
    episode = models.CharField(max_length=10, blank=True, null=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    expiration = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f'{self.tmdb_id} - {self.quality} - {self.url}'
