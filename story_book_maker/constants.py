"""Session state keys shared by google-adk agents."""

STORY_WRITER_RESULT_KEY = "story_writer_result"
ILLUSTRATOR_RESULT_KEY = "illustrator_result"


def illustrator_page_result_key(page_number: int) -> str:
    """Session state output_key for ONE page illustrator (avoids ParallelAgent clashes)."""

    return f"{ILLUSTRATOR_RESULT_KEY}_page_{page_number}"
