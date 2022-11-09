from django.db import models

# Create your models here.

QUESTIONS = [
    {
        'id': i,
        'avatar': str(i % 3 + 1),
        'title': 'title' + str(i + 1),
        'text': 'question' * 10,
        'answers_num': i + 1,
        'likes': (i + 10) % 6,
        'answers': [
            {
                'avatar': str(j % 3 + 1),
                'text': 'answer' * 10,
                'likes': (j + 10) % 6,
                'is_right': True if j == 0 else False,
            } for j in range(i + 1)
        ],
        'tags': ['python', 'c++', 'go', 'javascript']
    } for i in range(100)
]
