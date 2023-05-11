def obscure_email(email):
    username, domain = email.split("@")
    obscured_email = '{}{}@{}'.format(username[:2], '*' * len(username[2:]), domain)
    return obscured_email


def obscure_number(phone_number):
    obscured_number = '{}******{}'.format(phone_number[:3], phone_number[-2:])
    return obscured_number

def update_patient(patient):
    print(patient)