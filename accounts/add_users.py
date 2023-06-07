from django.contrib.auth.models import User

new_user = User.objects.create_user(username='newuser', password='newpassword')

new_user.first_name = 'Faisal'
new_user.last_name = 'Rehman'

new_user.save()
