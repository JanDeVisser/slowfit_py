from ..models.fits import Customer

CUSTOMER_FIRST_NAME = "Testy"
CUSTOMER_LAST_NAME = "McTestface"
CUSTOMER_ADDRESS = "42, Test Terrace\nTestville, ON, T5T 7S7"
CUSTOMER_EMAIL = "testy.mctestface@test.com"
CUSTOMER_EMAIL_2 = "testy.mctestface_2@test.com"
CUSTOMER_PHONE_MAIN = "(555) 555-0001"
CUSTOMER_PHONE_ALT = "(555) 555-0002"
CUSTOMER_DATE_OF_BIRTH = "2000-07-13"
CUSTOMER_HEIGHT = "180"
CUSTOMER_INSEAM = "80"

CUSTOMER_DATA = {
    "firstName":  CUSTOMER_FIRST_NAME,
    "lastName":  CUSTOMER_LAST_NAME,
    "address":  CUSTOMER_ADDRESS,
    "email":  CUSTOMER_EMAIL,
    "phoneMain":  CUSTOMER_PHONE_MAIN,
    "phoneAlt":  CUSTOMER_PHONE_ALT,
    "dateOfBirth":  CUSTOMER_DATE_OF_BIRTH,
    "height":  CUSTOMER_HEIGHT,
    "inseam":  CUSTOMER_INSEAM,
}


def create_customer():
    customer = Customer(**CUSTOMER_DATA)
    customer.save()
    return customer.id
