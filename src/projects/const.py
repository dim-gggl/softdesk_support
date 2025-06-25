ISSUE_LIST_FIELDS = [
    "id",
    "title",
    "description",
    "label",
    "priority",
    "status",
    "comments_count",
    "assignee",
]
ISSUE_LABELS = [
    "BUG",
    "FEATURE",
    "TASK",
]
ISSUE_PRIORITIES = [
    "LOW",
    "MEDIUM",
    "HIGH",
]
ISSUE_STATUSES = [
    "TO_DO",
    "IN_PROGRESS",
    "FINISHED",
]
PROJECT_TYPES = [
    "BACKEND",
    "FRONTEND",
    "IOS",
    "ANDROID",
]

PROJECT_ERROR_MESSAGE = {
    "name": "",
    "type": "BACKEND | FRONTEND | IOS | ANDROID",
    "description": "",
    "message": (
        "Missing or invalid fields. "
        "Check 'name', 'type'."
    )
}

ISSUE_ERROR_MESSAGE = {
    "title": "",
    "label": "BUG | FEATURE | TASK",
    "priority": "LOW | MEDIUM | HIGH",
    "status": "TODO | IN_PROGRESS | FINISHED",
    "message": (
        "Missing or invalid fields. "
        "Check 'title', 'label', 'priority'."
    )
}

COMMENT_ERROR_MESSAGE = {
    "content": "",
    "message": (
        "Missing or invalid fields. "
        "Check 'content'."
    )
}

CONTRIBUTOR_ERROR_MESSAGE = {
    "user": "{Must be a valid user ID}",
    "project": "{Must be a valid project ID}",
    "message": (
        "Missing or invalid fields. "
        "Check 'user', 'project'."
    )
}
IS_AUTHOR_TRUE_MESSAGE = {
    "message": "True. Contributor is the author of the project."
}
IS_AUTHOR_FALSE_MESSAGE = {
    "message": "False. Contributor is not the author of the project."
}
CONTRIBUTOR_UNAUTHORIZED_MESSAGE = {
    "message": (
        "This information is only available to "
        "the contributors of the project."
    )
}