"""
Quiz answer checker module.
Validates user answers against correct answers.
"""

from typing import Dict, Any, List, Optional, Union


class AnswerChecker:
    """Checks user answers against correct answers."""
    
    @staticmethod
    def check_single_choice(user_answer: Optional[int], correct_answer: int) -> bool:
        """Check single choice answer."""
        return user_answer is not None and user_answer == correct_answer
    
    @staticmethod
    def check_multiple_choice(
        user_answer: List[int], 
        correct_answers: List[int], 
        partial_credit: bool = False
    ) -> tuple[bool, float]:
        """
        Check multiple choice answer.
        Returns (is_correct, score_ratio).
        """
        if not user_answer:
            return False, 0.0
        
        user_set = set(user_answer)
        correct_set = set(correct_answers)
        
        if user_set == correct_set:
            return True, 1.0
        
        if partial_credit:
            # Calculate partial credit
            correct_count = len(user_set & correct_set)
            incorrect_count = len(user_set - correct_set)
            total_correct = len(correct_set)
            
            if incorrect_count == 0:
                # Only partial correct answers, no incorrect
                score = correct_count / total_correct
            else:
                # Has incorrect answers, penalize
                score = max(0.0, (correct_count - incorrect_count) / total_correct)
            
            return False, score
        
        return False, 0.0
    
    @staticmethod
    def check_text_input(
        user_answer: str,
        correct_answers: Union[str, List[str]],
        case_sensitive: bool = False,
        trim_whitespace: bool = True
    ) -> bool:
        """Check text input answer."""
        if not user_answer:
            return False
        
        # Normalize user answer
        user_text = user_answer
        if trim_whitespace:
            user_text = user_text.strip()
        if not case_sensitive:
            user_text = user_text.lower()
        
        # Normalize correct answers
        if isinstance(correct_answers, str):
            correct_answers = [correct_answers]
        
        for correct in correct_answers:
            correct_text = correct
            if trim_whitespace:
                correct_text = correct_text.strip()
            if not case_sensitive:
                correct_text = correct_text.lower()
            
            if user_text == correct_text:
                return True
        
        return False
    
    @staticmethod
    def check_matching(user_answer: Dict[int, int], correct_matches: List[Dict[str, int]]) -> tuple[bool, float]:
        """
        Check matching answer.
        Returns (is_correct, score_ratio).
        """
        if not user_answer:
            return False, 0.0
        
        # Convert correct matches to dict
        correct_dict = {m["left"]: m["right"] for m in correct_matches}
        
        correct_count = 0
        total = len(correct_dict)
        
        for left, right in user_answer.items():
            if left in correct_dict and correct_dict[left] == right:
                correct_count += 1
        
        score = correct_count / total if total > 0 else 0.0
        is_correct = score == 1.0
        
        return is_correct, score
    
    @staticmethod
    def check_ordering(user_answer: List[int], correct_order: List[int]) -> bool:
        """Check ordering answer."""
        if not user_answer or len(user_answer) != len(correct_order):
            return False
        
        return user_answer == correct_order
    
    @staticmethod
    def check_question(question_data: Dict[str, Any], user_answer: Any) -> tuple[bool, float, str]:
        """
        Check a question answer.
        Returns (is_correct, score_ratio, feedback).
        """
        q_type = question_data.get("type")
        points = question_data.get("points", 1.0)
        
        if q_type == "single_choice":
            correct = AnswerChecker.check_single_choice(
                user_answer,
                question_data.get("correct_answer", -1)
            )
            score = 1.0 if correct else 0.0
            feedback = "Правильно!" if correct else "Неправильно"
            return correct, score, feedback
        
        elif q_type == "multiple_choice":
            correct, score_ratio = AnswerChecker.check_multiple_choice(
                user_answer or [],
                question_data.get("correct_answers", []),
                question_data.get("partial_credit", False)
            )
            if correct:
                feedback = "Правильно!"
            elif score_ratio > 0:
                feedback = f"Частично правильно ({int(score_ratio * 100)}%)"
            else:
                feedback = "Неправильно"
            return correct, score_ratio, feedback
        
        elif q_type == "text_input":
            correct = AnswerChecker.check_text_input(
                user_answer or "",
                question_data.get("correct_answers", ""),
                question_data.get("case_sensitive", False),
                question_data.get("trim_whitespace", True)
            )
            score = 1.0 if correct else 0.0
            feedback = "Правильно!" if correct else "Неправильно"
            return correct, score, feedback
        
        elif q_type == "matching":
            correct, score_ratio = AnswerChecker.check_matching(
                user_answer or {},
                question_data.get("matches", [])
            )
            if correct:
                feedback = "Правильно!"
            elif score_ratio > 0:
                feedback = f"Частично правильно ({int(score_ratio * 100)}%)"
            else:
                feedback = "Неправильно"
            return correct, score_ratio, feedback
        
        elif q_type == "ordering":
            correct = AnswerChecker.check_ordering(
                user_answer or [],
                question_data.get("correct_order", [])
            )
            score = 1.0 if correct else 0.0
            feedback = "Правильно!" if correct else "Неправильно"
            return correct, score, feedback
        
        return False, 0.0, "Неизвестный тип вопроса"
    
    @staticmethod
    def check_quiz(quiz_data: Dict[str, Any], user_answers: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check all answers in a quiz.
        Returns results dictionary with scores and feedback.
        """
        results = {
            "total_questions": 0,
            "correct_answers": 0,
            "total_points": 0.0,
            "earned_points": 0.0,
            "questions": []
        }
        
        questions = quiz_data.get("questions", [])
        results["total_questions"] = len(questions)
        
        for question in questions:
            q_id = question.get("id")
            user_answer = user_answers.get(q_id)
            
            is_correct, score_ratio, feedback = AnswerChecker.check_question(question, user_answer)
            points = question.get("points", 1.0)
            earned = points * score_ratio
            
            results["total_points"] += points
            if is_correct:
                results["correct_answers"] += 1
            results["earned_points"] += earned
            
            results["questions"].append({
                "id": q_id,
                "question": question.get("question", ""),
                "type": question.get("type", ""),
                "user_answer": user_answer,
                "correct_answer": AnswerChecker._get_correct_answer_display(question),
                "is_correct": is_correct,
                "score_ratio": score_ratio,
                "points": points,
                "earned_points": earned,
                "feedback": feedback,
                "explanation": question.get("explanation", ""),
                "options": question.get("options", []),
                "left_items": question.get("left_items", []),
                "right_items": question.get("right_items", []),
                "items": question.get("items", [])
            })
        
        return results
    
    @staticmethod
    def _get_correct_answer_display(question_data: Dict[str, Any]) -> Any:
        """Get display representation of correct answer."""
        q_type = question_data.get("type")
        
        if q_type == "single_choice":
            idx = question_data.get("correct_answer", -1)
            options = question_data.get("options", [])
            if 0 <= idx < len(options):
                return options[idx]
            return idx
        
        elif q_type == "multiple_choice":
            indices = question_data.get("correct_answers", [])
            options = question_data.get("options", [])
            return [options[i] if 0 <= i < len(options) else i for i in indices]
        
        elif q_type == "text_input":
            answers = question_data.get("correct_answers", [])
            if isinstance(answers, str):
                return answers
            return answers[0] if answers else ""
        
        elif q_type == "matching":
            matches = question_data.get("matches", [])
            left_items = question_data.get("left_items", [])
            right_items = question_data.get("right_items", [])
            result = []
            for m in matches:
                left_idx = m.get("left", -1)
                right_idx = m.get("right", -1)
                if 0 <= left_idx < len(left_items) and 0 <= right_idx < len(right_items):
                    result.append(f"{left_items[left_idx]} → {right_items[right_idx]}")
            return result
        
        elif q_type == "ordering":
            order = question_data.get("correct_order", [])
            items = question_data.get("items", [])
            return [items[i] if 0 <= i < len(items) else i for i in order]
        
        return None

