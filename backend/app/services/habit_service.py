from datetime import datetime, timedelta
import uuid
from typing import Optional

from app.models.domain import Habit, HabitLog
from app.repositories.postgres import habit_repo
from app.core.crypto import crypto_service


class HabitService:

    def _decrypt_habit(self, habit: Optional[Habit]) -> Optional[Habit]:
        if not habit:
            return None

        try:
            name = crypto_service.decrypt(habit.name) or ""
        except Exception:
            # Existing plaintext values continue to work
            name = habit.name or ""

        return Habit(
            id=habit.id,
            user_id=habit.user_id,
            name=name,
            description=habit.description,
            frequency=habit.frequency,
            created_at=habit.created_at,
            updated_at=habit.updated_at,
        )

    def create_habit(
        self,
        user_id: str,
        name: str,
        description: Optional[str] = None,
        frequency: str = "daily"
    ) -> Habit:

        habit = Habit(
            id=str(uuid.uuid4()),
            user_id=user_id,
            name=crypto_service.encrypt(name.strip()),
            description=description,
            frequency=frequency,
        )

        saved = habit_repo.create(habit)

        return self._decrypt_habit(saved)

    def get_habits(
        self,
        user_id: str
    ) -> list[Habit]:

        habits = habit_repo.get_all_by_user(user_id)

        return [
            self._decrypt_habit(habit)
            for habit in habits
            if habit
        ]

    def get_habit(
        self,
        user_id: str,
        habit_id: str
    ) -> Optional[Habit]:

        habit = habit_repo.get_by_id(
            user_id,
            habit_id
        )

        return self._decrypt_habit(habit)

    def update_habit(
        self,
        user_id: str,
        habit_id: str,
        **kwargs
    ) -> Optional[Habit]:

        # Encrypt only a newly supplied name.
        # Description remains unchanged.
        if "name" in kwargs and kwargs["name"] is not None:
            kwargs["name"] = crypto_service.encrypt(
                str(kwargs["name"]).strip()
            )

        updated = habit_repo.update(
            user_id,
            habit_id,
            **kwargs
        )

        return self._decrypt_habit(updated)

    def delete_habit(
        self,
        user_id: str,
        habit_id: str
    ) -> bool:

        return habit_repo.delete(
            user_id,
            habit_id
        )

    def complete_habit(
        self,
        user_id: str,
        habit_id: str,
        completed_date: Optional[datetime] = None
    ) -> Optional[HabitLog]:

        if completed_date is None:
            completed_date = datetime.utcnow()

        return habit_repo.add_log(
            user_id,
            habit_id,
            completed_date
        )

    def uncomplete_habit(
        self,
        user_id: str,
        habit_id: str,
        completed_date: Optional[datetime] = None
    ) -> bool:

        if completed_date is None:
            completed_date = datetime.utcnow()

        return habit_repo.remove_log(
            user_id,
            habit_id,
            completed_date
        )

    def get_logs(
        self,
        user_id: str,
        habit_id: str
    ) -> list[HabitLog]:

        return habit_repo.get_logs(
            user_id,
            habit_id
        )

    def get_current_streak(
        self,
        user_id: str,
        habit_id: str
    ) -> int:

        logs = habit_repo.get_logs(
            user_id,
            habit_id
        )

        if not logs:
            return 0

        completed_days = {
            log.completed_date.date()
            for log in logs
        }

        today = datetime.utcnow().date()

        if today in completed_days:
            current_day = today
        elif (today - timedelta(days=1)) in completed_days:
            current_day = today - timedelta(days=1)
        else:
            return 0

        streak = 0

        while current_day in completed_days:
            streak += 1
            current_day -= timedelta(days=1)

        return streak

    def is_completed_today(
        self,
        user_id: str,
        habit_id: str
    ) -> bool:

        logs = habit_repo.get_logs(
            user_id,
            habit_id
        )

        today = datetime.utcnow().date()

        return any(
            log.completed_date.date() == today
            for log in logs
        )


habit_service = HabitService()