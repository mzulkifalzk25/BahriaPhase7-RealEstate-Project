create database fyp;

use fyp;

select * from accounts_user;

select * from realtors_realtor;

select * from listings_listing;

select * from accounts_user;

INSERT INTO realtors_realtor (user_id, photo, name, description, phone, email, is_mvp)
VALUES 
(2, 'realtors/realtor1.jpg', 'Zulkifal', 'Experienced realtor with a passion for helping clients', '+92 303 5542839', 'mzulkifalzk25@gmail.com', false),
(3, 'realtors/realtor2.jpg', 'Kamran', 'Experienced realtor with a passion for helping clients', '+92 344 5663368', 'iamkamran@gmail.com', false),
(4, 'realtors/realtor3.jpg', 'Aswad', 'Experienced realtor with a passion for helping clients', '+92 342 4645345', 'aswadhere@gmail.com', false),
(5, 'realtors/realtor4.jpg', 'Hamza', 'Experienced realtor with a passion for helping clients', '+92 348 5689421', 'hamza@gmail.com', false),
(6, 'realtors/realtor5.jpg', 'Ali', 'Excellent Seller with a passion for helping clients', '+92 309 6518725', 'ali@gmail.com', false),
(7, 'realtors/realtor6.jpg', 'Wajeeh', 'Experienced realtor with a passion for helping clients', '+92 312 3213545', 'its_wajeeh@gmail.com', false),
(8, 'realtors/realtor7.jpg', 'Faisal', 'Successful realtor with a passion for helping clients', '+92 321 7973789', 'rehman_faisal@gmail.com', false);

INSERT INTO listings_listing (title, address, city, description, price, bedrooms, bathrooms, area_in_marla, photo_main, photo_1, photo_2, photo_3, nearMasjid, nearMarket, list_date, realtor_id)
VALUES 
('Spacious Family Home', '123 Main Street', 'Rawalpindi', 'Beautiful and spacious family home located.', 45000000, 4, 3, 15, 'home/house 1.jpg', 'home/house 1-1.jpg', 'home/house 1-2.jpg', 'home/house 1-3.jpg', 1, 1, NOW(), 34),
('Cozy Apartment', '456 Elm Street', 'Rawalpindi', 'Cozy apartment in a desirable neighborhood.', 25000000, 2, 2, 8, 'home/house 2.jpg', 'home/house 2-1.jpg', 'home/house 2-2.jpg', 'home/house 2-3.jpg', 0, 1, NOW(), 34),
('Luxury Villa', '789 Oak Street', 'Rawalpindi', 'Luxurious villa with stunning ocean views.', 15000000, 5, 6, 25, 'home/house 3.jpg', 'home/house 3-1.jpg', 'home/house 3-2.jpg', 'home/house 3-3.jpg', 1, 0, NOW(), 34),
('Good Family', '123 Main Street', 'Rawalpindi', 'Beautiful and spacious family home located.', 5000000, 4, 3, 15, 'home/house 4.jpg', 'home/house 4-1.jpg', 'home/house 4-2.jpg', 'home/house 4-3.jpg', 1, 1, NOW(), 34),

('Comfortable Apartment', '456 Elm Street', 'Rawalpindi', 'Cozy apartment in a desirable neighborhood.', 2500000, 2, 2, 8, 'home/house 5.jpg', 'home/house 5-1.jpg', 'home/house 5-2.jpg', 'home/house 5-3.jpg', 0, 1, NOW(), 35),
('Amazing Villa', '789 Oak Street', 'Rawalpindi', 'Luxurious villa with stunning ocean views.', 17500000, 5, 6, 25, 'home/house 6.jpg', 'home/house 6-1.jpg', 'home/house 6-2.jpg', 'home/house 6-3.jpg', 1, 0, NOW(), 35),
('Modern Townhouse', '789 Elm Street', 'Rawalpindi', 'Contemporary townhouse in a convenient location.', 12350000, 3, 2, 10, 'home/house 7.jpg', 'home/house 7-1.jpg', 'home/house 7-2.jpg', 'home/house 7-3.jpg', 1, 0, NOW(), 35),
('Cosmopolitan Condo', '456 Oak Street', 'Rawalpindi', 'Stylish condo in the heart of the city.', 12450000, 1, 1, 5, 'home/house 8.jpg', 'home/house 8-1.jpg', 'home/house 8-2.jpg', 'home/house 8-3.jpg', 0, 1, NOW(), 35),

('Spacious Family Home', '123 Main Street', 'Rawalpindi', 'Beautiful and spacious family home located.', 15000000, 4, 3, 15, 'home/house 9.jpg', 'home/house 9-1.jpg', 'home/house 9-2.jpg', 'home/house 9-3.jpg', 1, 1, NOW(), 36),
('Cozy Apartment', '456 Elm Street', 'Rawalpindi', 'Cozy apartment in a desirable neighborhood.', 25000000, 2, 2, 8, 'home/house 10.jpg', 'home/house 10-1.jpg', 'home/house 10-2.jpg', 'home/house 10-3.jpg', 0, 1, NOW(), 36),
('Luxury Villa', '789 Oak Street', 'Rawalpindi', 'Luxurious villa with stunning ocean views.', 15000000, 5, 6, 25, 'hom11/house 11.jpg', 'home/house 11-1.jpg', 'home/house 11-2.jpg', 'home/house 11-3.jpg', 1, 0, NOW(), 36),
('Good Family', '123 Main Street', 'Rawalpindi', 'Beautiful and spacious family home located.', 5000000, 4, 3, 15, 'home/house 12.jpg', 'home/house 12-1.jpg', 'home/house 12-2.jpg', 'home/house 12-3.jpg', 1, 1, NOW(), 36),

('Comfortable Flat', '456 Elm Street', 'Rawalpindi', 'Cozy apartment in a desirable neighborhood.', 2500000, 2, 2, 8, 'home/house 13.jpg', 'home/house 13-1.jpg', 'home/house 13-2.jpg', 'home/house 13-3.jpg', 0, 1, NOW(), 37),
('Amazing House', '789 Oak Street', 'Rawalpindi', 'Luxurious villa with stunning ocean views.', 17500000, 5, 6, 25, 'home/house 14.jpg', 'home/house 14-1.jpg', 'home/house 14-2.jpg', 'home/house 14-3.jpg', 1, 0, NOW(), 37),
('Modern Townhouse', '789 Elm Street', 'Rawalpindi', 'Contemporary townhouse in a convenient location.', 12350000, 3, 2, 10, 'home/house 15.jpg', 'home/house 15-1.jpg', 'home/house 15-2.jpg', 'home/house 15-3.jpg', 1, 0, NOW(), 37),
('Luxury Condo', '456 Oak Street', 'Rawalpindi', 'Stylish condo in the heart of the city.', 12450000, 1, 1, 5, 'home/house 16.jpg', 'home/house 16-1.jpg', 'home/house 16-2.jpg', 'home/house 16-3.jpg', 0, 1, NOW(), 37),

('Special Flat', '123 Maple Avenue', 'Rawalpindi', 'Expansive ranch-style house with scenic views.', 18700000, 4, 3, 20, 'home/house 17.jpg', 'home/house 17-1.jpg', 'home/house 17-2.jpg', 'home/house 17-3.jpg', 1, 1, NOW(), 38),
('Amazing Flat', '789 Oak Street', 'Rawalpindi', 'Luxurious villa with stunning ocean views.', 17500000, 5, 6, 25, 'home/house 18.jpg', 'home/house 18-1.jpg', 'home/house 18-2.jpg', 'home/house 18-3.jpg', 1, 0, NOW(), 38),
('Modern House', '789 Elm Street', 'Rawalpindi', 'Contemporary townhouse in a convenient location.', 12350000, 3, 2, 10, 'home/house 19.jpg', 'home/house 19-1.jpg', 'home/house 19-2.jpg', 'home/house 19-3.jpg', 1, 0, NOW(), 38),
('Excellant House', '456 Oak Street', 'Rawalpindi', 'Stylish condo in the heart of the city.', 12450000, 1, 1, 5, 'home/house 20.jpg', 'home/house 20-1.jpg', 'home/house 20-2.jpg', 'home/house 20-3.jpg', 0, 1, NOW(), 38),

('Comfortable Flat', '456 Elm Street', 'Rawalpindi', 'Cozy apartment in a desirable neighborhood.', 2500000, 2, 2, 8, 'home/house 21.jpg', 'home/house 21-1.jpg', 'home/house 21-2.jpg', 'home/house 21-3.jpg', 0, 1, NOW(), 39),
('Amazing House', '789 Oak Street', 'Rawalpindi', 'Luxurious villa with stunning ocean views.', 17500000, 5, 6, 25, 'home/house 22.jpg', 'home/house 22-1.jpg', 'home/house 22-2.jpg', 'home/house 22-3.jpg', 1, 0, NOW(), 39),
('Modern Townhouse', '789 Elm Street', 'Rawalpindi', 'Contemporary townhouse in a convenient location.', 12350000, 3, 2, 10, 'home/house 23.jpg', 'home/house 23-1.jpg', 'home/house 23-2.jpg', 'home/house 23-3.jpg', 1, 0, NOW(), 39),
('Luxury Condo', '456 Oak Street', 'Rawalpindi', 'Stylish condo in the heart of the city.', 12450000, 1, 1, 5, 'home/house 24.jpg', 'home/house 24-1.jpg', 'home/house 24-2.jpg', 'home/house 24-3.jpg', 0, 1, NOW(), 39),

('Special Flat', '123 Maple Avenue', 'Rawalpindi', 'Expansive ranch-style house with scenic views.', 18700000, 4, 3, 20, 'home/house 25.jpg', 'home/house 25-1.jpg', 'home/house 25-2.jpg', 'home/house 25-3.jpg', 1, 1, NOW(), 40),
('Amazing Flat', '789 Oak Street', 'Rawalpindi', 'Luxurious villa with stunning ocean views.', 17500000, 5, 6, 25, 'home/house 26.jpg', 'home/house 26-1.jpg', 'home/house 26-2.jpg', 'home/house 26-3.jpg', 1, 0, NOW(), 40),
('Modern House', '789 Elm Street', 'Rawalpindi', 'Contemporary townhouse in a convenient location.', 12350000, 3, 2, 10, 'home/house 27.jpg', 'home/house 27-1.jpg', 'home/house 27-2.jpg', 'home/house 27-3.jpg', 1, 0, NOW(), 40),
('Excellant House', '456 Oak Street', 'Rawalpindi', 'Stylish condo in the heart of the city.', 12450000, 1, 1, 5, 'home/house 28.jpg', 'home/house 28-1.jpg', 'home/house 28-2.jpg', 'home/house 28-3.jpg', 0, 1, NOW(), 40);
