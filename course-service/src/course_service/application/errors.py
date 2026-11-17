class CourseNotFoundError(Exception):
    """The requested course does not exist."""


class AssignmentNotFoundError(Exception):
    """The requested assignment does not exist."""


class SubmissionNotFoundError(Exception):
    """The requested submission does not exist."""


class ReviewNotFoundError(Exception):
    """The requested review does not exist."""


class SubmissionAttemptsLimitExceededError(Exception):
    """A submission would exceed the assignment attempt limit."""


class ApplicationNotConfiguredError(RuntimeError):
    """The web application has no configured composition root."""
