from django.db import models
from accounts.models import User


class Realtor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='realtors/')
    name = models.CharField(max_length=100)
    description = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=100)
    is_mvp = models.BooleanField(default=False)

    def __str__(self):
        return self.name


# INSERT INTO realtors_realtor (user_id, photo, name, description, phone, email, is_mvp)
# VALUES (4,'realtors/realtor6.jpg','Hamza Mehmood','Experienced realtor with a passion for helping clients','03424645345','hamza@gmail.com',false);


# INSERT INTO listings_listing (title, address, city, description, price, bedrooms, bathrooms, area_in_marla, photo_main, photo_1, photo_2, photo_3, nearMasjid, nearMarket, list_date, realtor_id)
# VALUES 
# ('Spacious Family Home', '123 Main Street', 'New York', 'Beautiful and spacious family home located.', 15000000, 4, 3, 15, 'home/house 1.jpg', 'home/house 1-1.jpg', 'home/house 1-2.jpg', 'home/house 1-3.jpg', 1, 1, NOW(), 2),
# ('Cozy Apartment', '456 Elm Street', 'Los Angeles', 'Cozy apartment in a desirable neighborhood.', 25000000, 2, 2, 8, 'home/house 2.jpg', 'home/house 2-1.jpg', 'home/house 2-2.jpg', 'home/house 2-3.jpg', 0, 1, NOW(), 3),
# ('Luxury Villa', '789 Oak Street', 'Miami', 'Luxurious villa with stunning ocean views.', 15000000, 5, 6, 25, 'home/house 3.jpg', 'home/house 3-1.jpg', 'home/house 3-2.jpg', 'home/house 3-3.jpg', 1, 0, NOW(), 4),
# ('Good Family', '123 Main Street', 'New York', 'Beautiful and spacious family home located.', 5000000, 4, 3, 15, 'home/house 4.jpg', 'home/house 4-1.jpg', 'home/house 4-2.jpg', 'home/house 4-3.jpg', 1, 1, NOW(), 2),
# ('Comfortable Apartment', '456 Elm Street', 'Los Angeles', 'Cozy apartment in a desirable neighborhood.', 2500000, 2, 2, 8, 'home/house 5.jpg', 'home/house 5-1.jpg', 'home/house 5-2.jpg', 'home/house 5-3.jpg', 0, 1, NOW(), 3),
# ('Amazing Villa', '789 Oak Street', 'Miami', 'Luxurious villa with stunning ocean views.', 17500000, 5, 6, 25, 'home/house 6.jpg', 'home/house 6-1.jpg', 'home/house 6-2.jpg', 'home/house 6-3.jpg', 1, 0, NOW(), 4),
# ('Modern Townhouse', '789 Elm Street', 'Chicago', 'Contemporary townhouse in a convenient location.', 12350000, 3, 2, 10, 'home/house 7.jpg', 'home/house 7-1.jpg', 'home/house 7-2.jpg', 'home/house 7-3.jpg', 1, 0, NOW(), 2),
# ('Cosmopolitan Condo', '456 Oak Street', 'San Francisco', 'Stylish condo in the heart of the city.', 12450000, 1, 1, 5, 'home/house 8.jpg', 'home/house 8-1.jpg', 'home/house 8-2.jpg', 'home/house 8-3.jpg', 0, 1, NOW(), 3),
# ('Spacious Ranch House', '123 Maple Avenue', 'Austin', 'Expansive ranch-style house with scenic views.', 18700000, 4, 3, 20, 'home/house 9.jpg', 'home/house 9-1.jpg', 'home/house 9-2.jpg', 'home/house 9-3.jpg', 1, 1, NOW(), 4);

# Realtor3
# Raja Jibran
# +92 347 8662524
# jibran3740@gmail.com

# INSERT INTO realtors_realtor (user_id, photo, name, description, phone, email, is_mvp)
# VALUES 
# (2, 'realtors/realtor4.jpg', 'Zeeshan', 'Excellant Seller', '+92 309 6518725', 'zeeshan@example.com', False),
# (3, 'realtors/realtor5.jpg', 'Aswad', 'Experienced realtor ', '+92 309 6518725', 'zeeshan@example.com', False),
# (4, 'realtors/realtor8.jpg', 'Wajeeh', 'Successful realtor', '+92 349 5685769', 'wajeeh@example.com', False);

# Realtor4
# Hamza Khalid
# +92 309 5086366
# hamza2345@gmail.com

# Realtor5
#  Mahmood
# +92 312 5044142
# aswadmalik@gmail.com

# Realtor6
# +92 349 5685769
# waji720@gmail.com