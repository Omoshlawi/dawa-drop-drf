from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from decimal import Decimal

from core.models import HIVClinic, DeliveryMode


# Create your tests here.


class HIVClinicApiTestCase(APITestCase):
    def setUp(self) -> None:
        self.url = reverse('core:clinic-list')
        self.factory = RequestFactory()
        self.normal_user = User.objects.create_user(username='testuser', password='testpassword')
        self.admin_user = User.objects.create_user(username='testadminuser', password='testpassword', is_staff=True)

        # create clinics
        for i in range(3):
            HIVClinic.objects.create(
                name=f"Clinic {i}",
                longitude=Decimal(f"{i}.34565433"),
                latitude=Decimal(f"{i}.098765"),
                address=f"Some address {i}"
            )

    def test_clinics_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)

    def test_post_unauthorised(self):
        data = {
            'name': "Sample name",
            'longitude': 20.002,
            'latitude': 20.002,
            'address': "Sample address",

        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_none_admin(self):
        data = {
            'name': "Sample name",
            'longitude': 20.002,
            'latitude': 20.002,
            'address': "Sample address",

        }
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_admin(self):
        data = {
            'name': "Sample name",
            'longitude': 20.002,
            'latitude': 20.002,
            'address': "Sample address",
        }
        self.client.login(username='testadminuser', password='testpassword')
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        clinic = HIVClinic.objects.all().first()
        self.assertEqual(clinic.name, data["name"])

    def test_retrieve(self):
        """Test clinic detail view"""
        clinic = HIVClinic.objects.all().first()
        url = reverse("core:clinic-detail", args=[clinic.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(clinic.name, response.data["name"])
        self.assertEqual(clinic.address, response.data["address"])
        self.assertEqual(str(clinic.longitude), response.data["longitude"])
        self.assertEqual(str(clinic.latitude), response.data["latitude"])

    def test_put(self):
        data = {
            'name': "Sample PUT",
            'longitude': 20.0009876542,
            'latitude': 20.00984567802,
            'address': "Sample PUT address",
        }
        clinic = HIVClinic.objects.all().first()
        url = reverse("core:clinic-detail", args=[clinic.id])
        self.client.login(username='testadminuser', password='testpassword')
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        update = HIVClinic.objects.get(id=clinic.id)
        self.assertEqual(update.name, response.data["name"])
        self.assertEqual(update.address, response.data["address"])
        self.assertEqual(str(update.longitude), response.data["longitude"])
        self.assertEqual(str(update.latitude), response.data["latitude"])

    def test_delete(self):
        clinic = HIVClinic.objects.all().first()
        url = reverse("core:clinic-detail", args=[clinic.id])
        self.client.login(username='testadminuser', password='testpassword')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(2, HIVClinic.objects.all().count())
        self.assertTrue(HIVClinic.objects.filter(id=clinic.id).count() == 0)


class DeliveryModeApiTestCase(APITestCase):
    def setUp(self) -> None:
        self.url = reverse('core:mode-list')
        self.factory = RequestFactory()
        self.normal_user = User.objects.create_user(username='testuser', password='testpassword')
        self.admin_user = User.objects.create_user(username='testadminuser', password='testpassword', is_staff=True)

        # create clinics
        for i in range(3):
            DeliveryMode.objects.create(
                mode=f"Mode {i}",
            )

    def test_clinics_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)

    def test_post_unauthorised(self):
        data = {
            'mode': "Sample mode",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_none_admin(self):
        data = {
            'mode': "Sample mode",
        }
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_admin(self):
        data = {
            'mode': "Sample mode",
        }
        self.client.login(username='testadminuser', password='testpassword')
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mode = DeliveryMode.objects.all().first()
        self.assertEqual(mode.mode, data["mode"])

    def test_retrieve(self):
        """Test clinic detail view"""
        mode = DeliveryMode.objects.all().first()
        url = reverse("core:mode-detail", args=[mode.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(mode.mode, response.data["mode"])

    def test_put(self):
        data = {
            'mode': "Sample mode",
        }
        mode = DeliveryMode.objects.all().first()
        url = reverse("core:mode-detail", args=[mode.id])
        self.client.login(username='testadminuser', password='testpassword')
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        update = DeliveryMode.objects.get(id=mode.id)
        self.assertEqual(update.mode, response.data["mode"])

    def test_delete(self):
        mode = DeliveryMode.objects.all().first()
        url = reverse("core:mode-detail", args=[mode.id])
        self.client.login(username='testadminuser', password='testpassword')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(2, DeliveryMode.objects.all().count())
        self.assertTrue(DeliveryMode.objects.filter(id=mode.id).count() == 0)
