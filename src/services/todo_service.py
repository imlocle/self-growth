"""
ToDo service for business logic and data operations.
"""

from typing import Any, Dict

from models.enum import ToDoStatusEnum
from models.todo import ToDo
from repositories.todo_repository import ToDoRepository
from services.access_service import AccessService
from models.errors import NotFoundError, ValidationError
from utils.helper import generate_id, parse_iso, utc_now_iso
from utils.error_handler import log_error_with_context


class ToDoService:
    """Service for todo business logic"""

    def __init__(
        self,
        todo_repo: ToDoRepository | None = None,
        access_service: AccessService | None = None,
    ):
        self.todo_repo = todo_repo or ToDoRepository()
        self.access = access_service or AccessService()

    def create(
        self, user_id: str, household_id: str, subject_id: str, data: Dict[str, Any]
    ) -> ToDo:
        """
        Create a new todo.

        Args:
            user_id: User ID (for authorization)
            household_id: Household ID
            subject_id: Subject ID
            data: Validated todo data from Controller

        Returns:
            Created ToDo object
        """
        try:
            self.access.assert_household_member(
                user_id=user_id, household_id=household_id
            )
            self.access.assert_subject_in_household(
                household_id=household_id, subject_id=subject_id
            )

            now = utc_now_iso()
            todo = ToDo(
                id=generate_id(),
                household_id=household_id,
                subject_id=subject_id,
                date_created=now,
                date_modified=now,
                title=data["title"],
                description=data.get("description"),
                difficulty=data.get("difficulty", "easy"),
                status=data.get("status", "active"),
                date_due=data.get("date_due"),
                checklist=data.get("checklist"),
            )

            self.todo_repo.create(todo)
            return todo
        except Exception as e:
            log_error_with_context(
                e,
                user_id=user_id,
                operation="create_todo",
                household_id=household_id,
                subject_id=subject_id,
            )
            raise

    def get(
        self, user_id: str, household_id: str, subject_id: str, todo_id: str
    ) -> ToDo:
        """
        Get a single todo.

        Args:
            user_id: User ID (for authorization)
            household_id: Household ID
            subject_id: Subject ID
            todo_id: Todo ID

        Returns:
            ToDo object

        Raises:
            NotFoundError: If todo not found
        """
        try:
            self.access.assert_household_member(
                user_id=user_id, household_id=household_id
            )
            self.access.assert_subject_in_household(
                household_id=household_id, subject_id=subject_id
            )

            item = self.todo_repo.get(
                household_id=household_id, subject_id=subject_id, todo_id=todo_id
            )
            if not item:
                raise NotFoundError(
                    message="Todo not found", resource_type="todo", resource_id=todo_id
                )
            return ToDo.from_dynamo(item)
        except Exception as e:
            log_error_with_context(
                e,
                user_id=user_id,
                operation="get_todo",
                household_id=household_id,
                subject_id=subject_id,
                todo_id=todo_id,
            )
            raise

    def get_all(
        self,
        user_id: str,
        household_id: str,
        subject_id: str,
        sort_by: str = "date_modified",
        limit: int | None = None,
        next_token: dict | None = None,
        status: str | None = None,
    ) -> Dict[str, Any]:
        """
        Get all todos for a subject.

        Args:
            user_id: User ID (for authorization)
            household_id: Household ID
            subject_id: Subject ID
            sort_by: Sort field ("date_modified" or "date_due")
            limit: Max items to return
            next_token: DynamoDB ExclusiveStartKey for pagination
            status: Filter by status (active, completed, deleted)

        Returns:
            Dict with items list and pagination token
        """
        try:
            self.access.assert_household_member(
                user_id=user_id, household_id=household_id
            )
            self.access.assert_subject_in_household(
                household_id=household_id, subject_id=subject_id
            )

            # Validate sort_by parameter
            valid_sort_options = ["date_modified", "date_due"]
            if sort_by not in valid_sort_options:
                raise ValidationError(
                    f"Invalid sort_by parameter. Must be one of: {', '.join(valid_sort_options)}",
                    field="sort_by",
                    value=sort_by,
                    details={"valid_values": valid_sort_options},
                )

            # Build filter expression for status
            filter_expr = None
            expr_names = None
            expr_values = None
            if status:
                filter_expr = "#status = :status"
                expr_names = {"#status": "status"}
                expr_values = {":status": status}

            response = self.todo_repo.get_all(
                household_id=household_id,
                subject_id=subject_id,
                limit=limit,
                next_token=next_token,
                filter_expression=filter_expr,
                expression_attr_names=expr_names,
                expression_attr_values=expr_values,
            )
            items = [ToDo.from_dynamo(i) for i in response.get("items")]

            if sort_by == "date_due":
                items.sort(
                    key=lambda t: (
                        t.date_due is None,
                        parse_iso(t.date_due or t.date_modified),
                    )
                )
            else:
                items.sort(key=lambda t: parse_iso(t.date_modified))

            return {
                "items": items,
                "lastEvaluatedKey": response.get("lastEvaluatedKey"),
            }
        except Exception as e:
            log_error_with_context(
                e,
                user_id=user_id,
                operation="get_all_todos",
                household_id=household_id,
                subject_id=subject_id,
                sort_by=sort_by,
            )
            raise

    def update(
        self, user_id: str, household_id: str, subject_id: str, todo_id: str, data: dict
    ) -> ToDo:
        """
        Update an existing todo.

        Args:
            user_id: User ID (for authorization)
            household_id: Household ID
            subject_id: Subject ID
            todo_id: Todo ID
            data: Validated update data from Controller

        Returns:
            Updated ToDo object
        """
        try:
            todo = self.get(
                user_id=user_id,
                household_id=household_id,
                subject_id=subject_id,
                todo_id=todo_id,
            )

            # Update fields from validated data
            for field, value in data.items():
                if hasattr(todo, field):
                    setattr(todo, field, value)

            # Update modification timestamp
            todo.date_modified = utc_now_iso()

            self.todo_repo.update(todo=todo)
            return todo
        except Exception as e:
            log_error_with_context(
                e,
                user_id=user_id,
                operation="update_todo",
                household_id=household_id,
                subject_id=subject_id,
                todo_id=todo_id,
            )
            raise

    def delete(
        self, user_id: str, household_id: str, subject_id: str, todo_id: str
    ) -> None:
        """
        Delete a todo (soft delete).

        Args:
            user_id: User ID (for authorization)
            household_id: Household ID
            subject_id: Subject ID
            todo_id: Todo ID
        """
        try:
            todo = self.get(
                user_id=user_id,
                household_id=household_id,
                subject_id=subject_id,
                todo_id=todo_id,
            )
            todo.status = ToDoStatusEnum.DELETED
            todo.date_modified = utc_now_iso()
            self.todo_repo.update(todo=todo)
        except Exception as e:
            log_error_with_context(
                e,
                user_id=user_id,
                operation="delete_todo",
                household_id=household_id,
                subject_id=subject_id,
                todo_id=todo_id,
            )
            raise
