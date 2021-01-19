import pytest
import requests
import json


class TestPupilsFunctionality:
    pupil = {"first_name": "Peter", "last_name": "Peterhoff", "birth_date": "01-10-2005"}
    pupil_update = {"first_name": "Ivan", "last_name": "Ivanov", "birth_date": "01-01-2008"}
    host_url = 'http://127.0.0.1:5000/'
    headers = {'Content-Type': 'application/json'}

    def test_index_page(self):
        actual_response = requests.get(self.host_url, headers=self.headers)
        assert actual_response.status_code == 200

    @pytest.mark.parametrize("input_index,expected", [(1, 1), (2, 2), (44, 44)])
    def test_get_pupils(self, input_index, expected):
        pupil = {"first_name": "Peter" + str(input_index), "last_name": "Peterhoff" + str(input_index),
                 "birth_date": "01-10-2005"}
        actual_response = requests.post(self.host_url + 'api/pupils/', data=json.dumps(pupil), headers=self.headers)
        assert actual_response.status_code == 201
        assert actual_response.json()['pupil']['last_name'] == 'Peterhoff' + str(expected)

        actual_response = requests.get(self.host_url + 'api/pupils/', headers=self.headers)
        assert actual_response.status_code == 200

    def test_get_pupil_by_id(self):
        actual_response = requests.post(self.host_url + 'api/pupils/', data=json.dumps(self.pupil),
                                        headers=self.headers)
        assert actual_response.status_code == 201
        assert actual_response.json()['pupil']['last_name'] == 'Peterhoff'
        actual_response = requests.get(self.host_url + 'api/pupils/{}/'.format(actual_response.json()['pupil']['id']),
                                       headers=self.headers)
        assert actual_response.status_code == 200
        assert actual_response.json()['first_name'] == 'Peter'

    def test_pupil_assign_to_class(self):
        actual_response = requests.post(self.host_url + 'api/pupils/', data=json.dumps(self.pupil),
                                        headers=self.headers)
        assert actual_response.status_code == 201
        assert actual_response.json()['pupil']['last_name'] == 'Peterhoff'
        actual_response = requests.patch(
            self.host_url + 'api/pupils/{}/1/'.format(actual_response.json()['pupil']['id']), headers=self.headers)
        assert actual_response.status_code == 200
        assert actual_response.json()['pupil']['school_class']['id'] == 1

    def test_pupil_change_class(self):
        actual_response = requests.post(self.host_url + 'api/pupils/', data=json.dumps(self.pupil),
                                        headers=self.headers)
        assert actual_response.status_code == 201
        assert actual_response.json()['pupil']['last_name'] == 'Peterhoff'
        actual_response = requests.put(self.host_url + 'api/pupils/{}/2/'.format(actual_response.json()['pupil']['id']),
                                       headers=self.headers)
        assert actual_response.status_code == 200
        assert actual_response.json()['pupil']['school_class']['id'] == 2

    def test_update_pupil_by_id(self):
        actual_response = requests.post(self.host_url + 'api/pupils/', data=json.dumps(self.pupil),
                                        headers=self.headers)
        assert actual_response.status_code == 201
        assert actual_response.json()['pupil']['first_name'] == 'Peter'
        actual_response = requests.patch(self.host_url + 'api/pupils/{}/'.format(actual_response.json()['pupil']['id']),
                                         data=json.dumps(self.pupil_update), headers=self.headers)
        assert actual_response.status_code == 200
        assert actual_response.json()['first_name'] == 'Ivan'

    def test_create_pupil(self):
        actual_response = requests.post(self.host_url + 'api/pupils/', data=json.dumps(self.pupil),
                                        headers=self.headers)
        assert actual_response.status_code == 201
        assert actual_response.json()['pupil']['first_name'] == 'Peter'
        actual_response = requests.get(self.host_url + 'api/pupils/{}/'.format(actual_response.json()['pupil']['id']),
                                       headers=self.headers)
        assert actual_response.status_code == 200
        assert actual_response.json()['birth_date'] == "01-10-2005"
