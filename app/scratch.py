from datetime import date
import random

# today = date.today().toordinal()
# print(today)


user1 = {
    "answers": [
        {
            "date_created": "Thu, 08 Sep 2022 01:39:04 GMT",
            "id": 2,
            "line1": "first line words",
            "line2": "second line words",
            "line3": "some more words",
            "prompt_id": 2,
            "url": "http://www.blah.com",
            "user_id": 1
        }
    ],
    "email": "rpeace@email.com",
    "first_name": "Rebecca",
    "id": 1,
    "last_name": "Peace",
    "username": "rpeace"
}

for i in user1['answers']:
    print(i['prompt_id'])

print(len(user1['answers']))

num = 30
print(random.randint(1, num))

arr1 = [1, 2, 5, 6, 9]
id = random.randint(1, 10)
while id in arr1:
    id = random.randint(1, 10)
print(id)

