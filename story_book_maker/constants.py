"""Session state keys shared by google-adk agents."""

STORY_WRITER_RESULT_KEY = "story_writer_result"
ILLUSTRATOR_RESULT_KEY = "illustrator_result"
FINAL_STORY_BOOK_RESULT_KEY = "final_story_book_result"
FINAL_STORY_BOOK_PDF_FILENAME = "story_book.pdf"
ILLUSTRATION_PAGE_COUNT = 5

PROGRESS_PHASE_KEY = "progress_phase"
PROGRESS_MESSAGE_KEY = "progress_message"
PROGRESS_CURRENT_KEY = "progress_current"
PROGRESS_TOTAL_KEY = "progress_total"


def illustrator_page_result_key(page_number: int) -> str:
    """Session state output_key for ONE page illustrator (avoids ParallelAgent clashes)."""

    return f"{ILLUSTRATOR_RESULT_KEY}_page_{page_number}"
