from locust import HttpUser , task,between
import uuid

SOLUTION_CODE = """
class Solution:
    def two_sum_sorted(self, numbers, target):
        left, right = 0, len(numbers) - 1
        while left < right:
            s = numbers[left] + numbers[right]
            if s == target:
                return [left, right]
            elif s < target:
                left += 1
            else:
                right -= 1
        return []
"""


class LeetUser(HttpUser):
    wait_time=between(1,2)

    def on_start(self):
        uid=str(uuid.uuid4().hex[:8])
        self.username=f'bot_{uid}'
        self.email=f"bot_{uid}@test.com"
        self.password="123123123"

        reg= self.client.post("/auth/",json={
            "name": "bot",
            "nik_name": self.username,
            "email": self.email,
            "password": self.password,
            "password_confim": self.password
        })

        if reg.status_code!=200:
            print("REGISTER FAILED", reg.status_code,reg.text)
            return

        login=self.client.post("/auth/login", data={
            "username": self.username,
            "password": self.password
        })

        if login.status_code!=200:
            print("LOGIN FAILED", login.status_code,login.text)
            return

        token=login.json()["access_token"]
        self.client.headers["Authorization"]= f"Bearer {token}"

    @task
    def submit_solution(self):
        #print("hEADERS BEFOER REQUEST:", self.client.headers)
        resp = self.client.post("/solution/submit/2", json={"code": SOLUTION_CODE})
        if resp.status_code != 200:
            print("SUBMIT FAILED", resp.status_code, resp.text)
            return

        submission_id = resp.json()["id"]  
        self.client.get(f"/solution/result/{submission_id}")