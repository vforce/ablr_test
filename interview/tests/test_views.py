from re import L
import unittest
from api.views import _parse_person_data, _get_decrypted_data, index, singpass_callback
from unittest.mock import patch
import django


class TestViews(unittest.TestCase):
    def test_dummy(self):
        assert 1 == 1

    def test_parse_person_data(self):
        email = "1234"
        name = "test_name"
        sex = "male"
        race = "European"
        nationality = "France"
        dob = "1988-03-20"
        email = "test_email"
        data = {
            "uinfin": {"value": email},
            "name": {"value": name},
            "sex": {"desc": sex},
            "race": {"desc": race},
            "nationality": {"desc": nationality},
            "dob": {"value": dob},
            "email": {"value": email},
        }
        person = _parse_person_data(data)
        assert person.name == name
        assert person.dob == dob
        assert person.nationality == nationality
        assert person.sex == sex
        assert person.race == race
        assert person.email == email

    @patch("myinfo.security.get_decrypted_person_data")
    @patch("myinfo.client.MyInfoClient")
    @patch("myinfo.security.get_decoded_access_token")
    def test_get_decrypted_data(
        self, mocked_decode_access_token, mocked_info_client, mocked_get_decrypted
    ):
        access_token = "dummy_token"
        decrypted_value = "decrypted_value"
        uinfin = "1234"
        mocked_decode_access_token.return_value = {"sub": uinfin}
        mocked_info_client.get_person.return_value = "dummy_response"
        mocked_get_decrypted.return_value = decrypted_value

        assert mocked_info_client.get_person.called_with(uinfin, access_token)
        assert _get_decrypted_data(access_token) == decrypted_value


class TestViewsDjango(django.test.TestCase):
    @patch("myinfo.client.MyInfoClient")
    @patch("os.path.exists")
    def test_index_page(self, mocked_exists, mocked_info_client):
        """
        Test when there's no data file, the index page should show the consent page
        """
        mocked_exists.return_value = False

        mocked_info_client.get_authorise_url.return_value = "consent_url"
        response = self.client.get("/")
        self.assertTemplateUsed("api/index.html")
        self.assertEqual(response.status_code, 200)

    @patch("myinfo.client.MyInfoClient")
    def test_singpass_callback(self, mocked_info_client):
        response = self.client.get("/callback")
        assert response.status_code == 400

    @patch("api.views._write_decrypted_data_to_file")
    @patch("api.views._get_decrypted_data")
    @patch("myinfo.client.MyInfoClient")
    def test_singpass_callback(
        self, mocked_info_client, mocked_get_decrypted_token, mocked_write_decrypted
    ):
        code = "1234"
        access_token = "5678"
        response = self.client.get("/callback", {"code": code})
        mocked_info_client.get_access_token.return_value = access_token
        mocked_get_decrypted_token.return_value = ""
        assert response.status_code == 302
