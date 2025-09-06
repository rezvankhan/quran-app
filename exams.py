from datetime import datetime
from typing import List, Optional

class Exam:
    def __init__(self):
        self.exams = []
    
    def create_exam(self, title: str, teacher_id: int, questions: List[dict], duration: int):
        exam = {
            "id": len(self.exams) + 1,
            "title": title,
            "teacher_id": teacher_id,
            "questions": questions,
            "duration": duration,
            "created_at": datetime.utcnow()
        }
        self.exams.append(exam)
        return exam