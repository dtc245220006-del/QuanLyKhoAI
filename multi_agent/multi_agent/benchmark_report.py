from .benchmark import QUESTIONS, run


def get_question_count() -> int:
    return len(QUESTIONS)


if __name__ == "__main__":
    run()
