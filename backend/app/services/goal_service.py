import logging
import uuid
import re
import difflib
import math

from typing import Optional, Any
from datetime import datetime, timezone, date

from app.models.domain import Goal, Progress
from app.schemas.goal import GoalCreate, GoalUpdate
from app.repositories.postgres import goal_repo, progress_repo
from app.core.crypto import crypto_service


logger = logging.getLogger(__name__)


class GoalService:
    @staticmethod
    def _decrypt_value(value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        try:
            return crypto_service.decrypt(value)
        except Exception:
            # Existing plaintext database values remain usable
            return value

    def _decrypt_goal(
        self,
        goal: Optional[Goal]
    ) -> Optional[Goal]:

        if not goal:
            return None

        goal.title = self._decrypt_value(
            goal.title
        ) or ""

        goal.description = self._decrypt_value(
            goal.description
        )

        return goal

    def _decrypt_goals(
        self,
        goals: list[Goal]
    ) -> list[Goal]:

        return [
            self._decrypt_goal(goal)
            for goal in goals
            if goal
        ]

    @staticmethod
    def calculate_goal_priority(goal: Goal) -> str:
        """
        Classify goals into High Priority, Medium Priority, or Low Priority.

        Rules:
        - Completed goals -> Low Priority
        - Overdue + incomplete -> High Priority
        - Approaching deadline <= 7 days + progress < 50% -> High Priority
        - Stalled -> High Priority
        - Deadline within 30 days with moderate progress -> Medium Priority
        - Distant deadline or healthy progress -> Low Priority
        """

        status = (goal.status or "Active").capitalize()

        if status == "Completed" or (
            goal.progress_value and goal.progress_value >= 100
        ):
            return "Low Priority"

        val = goal.progress_value or 0

        now = datetime.now(timezone.utc)
        today = now.date()

        days_until_deadline: Optional[int] = None

        if goal.target_date:
            try:
                target_str = str(goal.target_date).split("T")[0]

                target_d = datetime.strptime(
                    target_str,
                    "%Y-%m-%d",
                ).date()

                days_until_deadline = (
                    target_d - today
                ).days

            except Exception:
                pass

        # 1. Overdue
        if (
            days_until_deadline is not None
            and days_until_deadline < 0
        ):
            return "High Priority"

        # 2. Deadline within 7 days and progress below 50%
        if (
            days_until_deadline is not None
            and days_until_deadline <= 7
            and val < 50
        ):
            return "High Priority"

        # 3. Stalled
        if status == "Stalled":
            return "High Priority"

        # 4. Deadline within 30 days
        if (
            days_until_deadline is not None
            and days_until_deadline <= 30
            and val < 75
        ):
            return "Medium Priority"

        # 5. Healthy progress / distant deadline
        if (
            val >= 75
            or (
                days_until_deadline is not None
                and days_until_deadline > 30
            )
        ):
            return "Low Priority"

        return "Medium Priority"

    def _enrich_goal(
        self,
        goal: Optional[Goal],
    ) -> Optional[Goal]:

        if not goal:
            return None

        # Sync latest progress record
        try:
            latest_progress = progress_repo.get_latest_by_goal(
                user_id=goal.user_id,
                goal_id=goal.id,
            )

            if (
                latest_progress
                and latest_progress.progress_value is not None
            ):
                goal.progress_value = max(
                    goal.progress_value or 0,
                    latest_progress.progress_value,
                )

        except Exception:
            pass

        val = goal.progress_value or 0

        # Completed goal
        if val >= 100:
            goal.status = "Completed"
            goal.progress_value = 100
            goal.estimated_days_remaining = 0

            if not goal.priority:
                goal.priority = "Low Priority"

            return goal

        if goal.status == "Completed":
            goal.progress_value = 100
            goal.estimated_days_remaining = 0

            if not goal.priority:
                goal.priority = "Low Priority"

            return goal

        # Calculate estimated completion time
        created_dt = (
            goal.created_at
            or datetime.now(timezone.utc)
        )

        if created_dt.tzinfo is None:
            created_dt = created_dt.replace(
                tzinfo=timezone.utc
            )

        days_active = max(
            1,
            (
                datetime.now(timezone.utc)
                - created_dt
            ).days,
        )

        velocity = max(
            val / days_active,
            2.0,
        )

        remaining_percentage = max(
            0,
            100 - val,
        )

        goal.estimated_days_remaining = math.ceil(
            remaining_percentage / velocity
        )

        # Preserve manual priority
        if not goal.priority:
            goal.priority = self.calculate_goal_priority(
                goal
            )

        return goal

    def list_goals(
        self,
        user_id: str,
        status: Optional[str] = None,
    ) -> list[Goal]:

        raw_goals = goal_repo.get_all_by_user(
            user_id=user_id,
            status=status,
        )

        decrypted_goals = self._decrypt_goals(
            raw_goals
        )

        return [
            self._enrich_goal(goal)
            for goal in decrypted_goals
            if goal
        ]

    def get_goal(
        self,
        user_id: str,
        goal_id: str,
    ) -> Optional[Goal]:

        goal = goal_repo.get_by_id(
            user_id=user_id,
            goal_id=goal_id,
        )

        goal = self._decrypt_goal(goal)

        return self._enrich_goal(goal)

    def create_goal(
        self,
        user_id: str,
        data: GoalCreate,
    ) -> Goal:

        prog_val = data.progress_value or 0

        init_status = (
            "Completed"
            if prog_val >= 100
            else (
                data.status.value
                if hasattr(data.status, "value")
                else str(data.status)
            )
        )

        temp_goal = Goal(
            id="",
            user_id=user_id,
            title=data.title.strip(),
            status=init_status,
            target_date=data.target_date,
            progress_value=prog_val,
        )

        init_priority = (
            data.priority
            or self.calculate_goal_priority(temp_goal)
        )

        goal = Goal(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=data.title.strip(),
            description=(
                data.description.strip()
                if data.description
                else None
            ),
            category=(
                data.category.strip()
                if data.category
                else None
            ),
            status=init_status,
            priority=init_priority,
            target_date=data.target_date,
            progress_value=prog_val,
        )

        storage_goal = Goal(
            id=goal.id,
            user_id=goal.user_id,
            title=crypto_service.encrypt(
                goal.title
            ),
            description=(
                crypto_service.encrypt(
                    goal.description
                )
                if goal.description is not None
                else None
            ),
            category=goal.category,
            status=goal.status,
            priority=goal.priority,
            target_date=goal.target_date,
            progress_value=goal.progress_value,
            latest_progress_note=goal.latest_progress_note,
            estimated_days_remaining=(
                goal.estimated_days_remaining
            ),
            google_event_id=goal.google_event_id,
            google_event_link=goal.google_event_link,
            calendar_synced=goal.calendar_synced,
            created_at=goal.created_at,
            updated_at=goal.updated_at,
        )

        saved = goal_repo.create(storage_goal)

        decrypted_saved = self._decrypt_goal(
            saved
        )

        return self._enrich_goal(
            decrypted_saved
        )

    def update_goal(
        self,
        user_id: str,
        goal_id: str,
        data: GoalUpdate,
    ) -> Optional[Goal]:

        updates = {}

        if data.title is not None:
            updates["title"] = crypto_service.encrypt(
                data.title.strip()
            )

        if data.description is not None:
            updates["description"] = (
                crypto_service.encrypt(
                    data.description.strip()
                )
            )

        if data.category is not None:
            updates["category"] = (
                data.category.strip()
            )

        if data.status is not None:
            updates["status"] = (
                data.status.value
                if hasattr(data.status, "value")
                else str(data.status)
            )

        if data.priority is not None:
            updates["priority"] = data.priority

        if data.target_date is not None:
            updates["target_date"] = data.target_date

        if data.progress_value is not None:
            updates["progress_value"] = (
                data.progress_value
            )

        # ---------------------------------------------------------
        # Goal completed
        # ---------------------------------------------------------
        if (
            updates.get("status") == "Completed"
            or updates.get("progress_value") == 100
        ):

            updates["status"] = "Completed"
            updates["progress_value"] = 100

            note = (
                data.latest_progress_note
                or "Goal marked as completed (100%)"
            )

            updates["latest_progress_note"] = note

            try:
                progress_repo.create(
                    Progress(
                        id=str(uuid.uuid4()),
                        goal_id=goal_id,
                        progress_value=100,
                        note=note,
                        created_at=datetime.utcnow(),
                    )
                )
            except Exception as e:
                logger.warning(
                    "Could not auto-create completed progress entry: %s",
                    e,
                )

        # ---------------------------------------------------------
        # Progress updated but goal is not completed
        # ---------------------------------------------------------
        elif data.progress_value is not None:

            note = (
                data.latest_progress_note
                or f"Progress updated to {data.progress_value}%"
            )

            updates["latest_progress_note"] = note

            try:
                progress_repo.create(
                    Progress(
                        id=str(uuid.uuid4()),
                        goal_id=goal_id,
                        progress_value=data.progress_value,
                        note=note,
                        created_at=datetime.utcnow(),
                    )
                )
            except Exception as e:
                logger.warning(
                    "Could not auto-create progress entry: %s",
                    e,
                )

        updated = goal_repo.update(
            user_id=user_id,
            goal_id=goal_id,
            **updates,
        )

        updated = self._decrypt_goal(
            updated
        )

        return self._enrich_goal(updated)

    def delete_goal(
        self,
        user_id: str,
        goal_id: str,
    ) -> bool:

        return goal_repo.delete(
            user_id=user_id,
            goal_id=goal_id,
        )

    def match_activity_to_existing_goal(
        self,
        activity_text: str,
        hint: Optional[Any],
        existing_goals: list[Goal],
    ) -> tuple[Optional[str], Optional[str]]:
        """
        Deterministically match an activity to one of
        the user's existing goals.

        Returns:
            (matched_goal_id, matched_goal_title)
        """

        if not existing_goals:
            return None, None

        # ---------------------------------------------------------
        # 1. Direct hint check
        # ---------------------------------------------------------
        if hint is not None:

            hint_clean = str(hint).strip().lower()

            if hint_clean:

                for goal in existing_goals:

                    goal_id = str(
                        goal.id
                    ).strip().lower()

                    goal_title = str(
                        goal.title or ""
                    ).strip().lower()

                    if (
                        goal_id == hint_clean
                        or (
                            goal_title
                            and goal_title in hint_clean
                        )
                        or (
                            goal_title
                            and hint_clean in goal_title
                        )
                    ):
                        return (
                            goal.id,
                            goal.title,
                        )

        # ---------------------------------------------------------
        # 2. Token overlap check
        # ---------------------------------------------------------

        activity_words = set(
            re.findall(
                r"\w+",
                activity_text.lower(),
            )
        )

        stop_words = {
            "the",
            "a",
            "an",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "and",
            "or",
            "my",
            "i",
            "was",
            "with",
        }

        activity_keywords = (
            activity_words - stop_words
        )

        best_match: Optional[Goal] = None
        highest_overlap = 0

        for goal in existing_goals:

            goal_words = set(
                re.findall(
                    r"\w+",
                    goal.title.lower(),
                )
            ) - stop_words

            overlap = len(
                activity_keywords & goal_words
            )

            if (
                overlap > 0
                and overlap > highest_overlap
            ):
                highest_overlap = overlap
                best_match = goal

        if (
            best_match
            and highest_overlap >= 1
        ):
            return (
                best_match.id,
                best_match.title,
            )

        return None, None

    def is_duplicate_goal(
        self,
        candidate_title: str,
        existing_goals: list[Goal],
        threshold: float = 0.60,
    ) -> Optional[Goal]:

        if not candidate_title or not existing_goals:
            return None

        candidate_norm = (
            candidate_title.strip().lower()
        )

        stop_words = {
            "to",
            "a",
            "an",
            "the",
            "in",
            "for",
            "on",
            "with",
            "my",
            "and",
            "learn",
            "complete",
            "finish",
        }

        cand_tokens = (
            set(
                re.findall(
                    r"\w+",
                    candidate_norm,
                )
            )
            - stop_words
        )

        for goal in existing_goals:

            existing_title = (
                goal.title.strip().lower()
            )

            if (
                candidate_norm == existing_title
                or candidate_norm in existing_title
                or existing_title in candidate_norm
            ):
                return goal

            exist_tokens = (
                set(
                    re.findall(
                        r"\w+",
                        existing_title,
                    )
                )
                - stop_words
            )

            if cand_tokens and exist_tokens:

                overlap = len(
                    cand_tokens & exist_tokens
                )

                if (
                    overlap >= 2
                    or (
                        len(cand_tokens) <= 2
                        and overlap == len(cand_tokens)
                    )
                ):
                    return goal

            ratio = difflib.SequenceMatcher(
                None,
                candidate_norm,
                existing_title,
            ).ratio()

            if ratio >= threshold:
                return goal

        return None

    def auto_create_goals_from_journal(
        self,
        user_id: str,
        extracted_goals: list[dict],
        existing_goals: list[Goal],
    ) -> list[Goal]:

        created = []

        for g_data in extracted_goals:

            if (
                not g_data.get("is_new", True)
                or g_data.get("confidence", 1.0) < 0.65
            ):
                continue

            title = (
                g_data.get("title")
                or g_data.get("text")
                or ""
            ).strip()

            if not title or len(title) < 3:
                continue

            duplicate = self.is_duplicate_goal(
                title,
                existing_goals,
            )

            if duplicate:

                g_data["is_new"] = False

                g_data[
                    "matched_existing_goal_id"
                ] = duplicate.id

                g_data[
                    "matched_existing_goal_title"
                ] = duplicate.title

                logger.info(
                    "Auto-goal skipped duplicate: "
                    "'%s' matched with '%s'",
                    title,
                    duplicate.title,
                )

                continue

            raw_prog = (
                g_data.get(
                    "progress_value",
                    0,
                )
                or 0
            )

            raw_status = str(
                g_data.get(
                    "status",
                    "Active",
                )
            )

            if (
                raw_prog >= 100
                or raw_status.lower() == "completed"
            ):
                initial_status = "Completed"
                initial_prog = 100
            else:
                initial_status = "Active"
                initial_prog = raw_prog

            new_goal_dto = GoalCreate(
                title=title,
                description=(
                    g_data.get("description")
                    or "Auto-generated from journal entry."
                ),
                category=(
                    g_data.get("category")
                    or "Personal"
                ),
                status=initial_status,
                target_date=g_data.get(
                    "target_date"
                ),
                progress_value=initial_prog,
            )

            new_goal = self.create_goal(
                user_id=user_id,
                data=new_goal_dto,
            )

            created.append(new_goal)
            existing_goals.append(new_goal)

            g_data["is_new"] = True
            g_data[
                "auto_created_goal_id"
            ] = new_goal.id

            logger.info(
                "Auto-created goal '%s' "
                "(ID: %s) for user %s",
                new_goal.title,
                new_goal.id,
                user_id,
            )

        return created

    @staticmethod
    def categorize_goal_deadline(
        goal: Any,
    ) -> str:
        """
        Categorize goals into:
        Completed, Overdue, Due Today,
        Upcoming, or No Target Date.
        """

        status = (
            getattr(goal, "status", None)
            if hasattr(goal, "status")
            else (
                goal.get("status")
                if isinstance(goal, dict)
                else ""
            )
        )

        is_completed = (
            getattr(goal, "completed", False)
            if hasattr(goal, "completed")
            else (
                goal.get("completed", False)
                if isinstance(goal, dict)
                else False
            )
        )

        progress = (
            getattr(
                goal,
                "progress_value",
                0,
            )
            if hasattr(goal, "progress_value")
            else (
                goal.get(
                    "progress_value",
                    0,
                )
                if isinstance(goal, dict)
                else 0
            )
        )

        if (
            str(status).lower() == "completed"
            or is_completed
            or (
                progress
                and progress >= 100
            )
        ):
            return "Completed"

        target_date = (
            getattr(
                goal,
                "target_date",
                None,
            )
            if hasattr(goal, "target_date")
            else (
                goal.get("target_date")
                if isinstance(goal, dict)
                else None
            )
        )

        if not target_date:
            return "No Target Date"

        today = date.today()

        if isinstance(target_date, str):

            try:
                target_date = date.fromisoformat(
                    target_date.split("T")[0]
                )

            except ValueError:
                return "Upcoming"

        elif isinstance(target_date, datetime):

            target_date = target_date.date()

        if target_date < today:
            return "Overdue"

        elif target_date == today:
            return "Due Today"

        else:
            return "Upcoming"

    def get_focus_next_recommendation(
        self,
        user_id: str,
    ) -> Optional[dict]:
        """
        Determine the top priority goal for the user
        and provide a contextual reason and next action.
        """

        uid = user_id or "default_user"

        all_goals = self.list_goals(
            user_id=uid
        )

        active_goals = [
            goal
            for goal in all_goals
            if (
                (goal.status or "").lower()
                != "completed"
                and (goal.progress_value or 0)
                < 100
            )
        ]

        if not active_goals:
            return None

        today = (
            datetime.now(timezone.utc).date()
        )

        def goal_urgency_score(
            goal: Goal,
        ) -> tuple[int, int, int]:

            # Priority rank
            p_score = (
                3
                if "High" in (
                    goal.priority or ""
                )
                else (
                    2
                    if "Medium" in (
                        goal.priority or ""
                    )
                    else 1
                )
            )

            # Deadline proximity
            days_left = 9999

            if goal.target_date:

                try:

                    clean_date = str(
                        goal.target_date
                    ).split("T")[0]

                    target_d = datetime.strptime(
                        clean_date,
                        "%Y-%m-%d",
                    ).date()

                    days_left = (
                        target_d - today
                    ).days

                except Exception:
                    pass

            progress = (
                goal.progress_value or 0
            )

            return (
                p_score,
                -days_left,
                -progress,
            )

        target_goal = max(
            active_goals,
            key=goal_urgency_score,
        )

        # ---------------------------------------------------------
        # Generate contextual reason
        # ---------------------------------------------------------

        days_left_num = None

        if target_goal.target_date:

            try:

                clean_date = str(
                    target_goal.target_date
                ).split("T")[0]

                days_left_num = (
                    datetime.strptime(
                        clean_date,
                        "%Y-%m-%d",
                    ).date()
                    - today
                ).days

            except Exception:
                pass

        reasons = [
            target_goal.priority
            or "Medium Priority"
        ]

        if days_left_num is not None:

            if days_left_num < 0:

                reasons.append(
                    f"overdue by "
                    f"{abs(days_left_num)} "
                    f"day"
                    f"{'s' if abs(days_left_num) > 1 else ''}"
                )

            elif days_left_num == 0:

                reasons.append("due today")

            elif days_left_num == 1:

                reasons.append("due tomorrow")

            else:

                reasons.append(
                    f"due in {days_left_num} days"
                )

        reasons.append(
            f"currently at "
            f"{target_goal.progress_value or 0}% progress"
        )

        reason_text = (
            ", ".join(reasons) + "."
        )

        # ---------------------------------------------------------
        # Generate next action
        # ---------------------------------------------------------

        prog = (
            target_goal.progress_value or 0
        )

        if prog == 0:

            next_action_text = (
                f"Draft the initial outline "
                f"and finish step 1 for "
                f"'{target_goal.title}'."
            )

        elif prog < 50:

            next_action_text = (
                "Dedicate a 45-minute focus "
                "sprint to push progress "
                "beyond 50%."
            )

        elif prog < 85:

            next_action_text = (
                "Review remaining milestones "
                "and tackle final deliverables today."
            )

        else:

            next_action_text = (
                f"Finalize last deliverables "
                f"and mark '{target_goal.title}' "
                f"as completed."
            )

        return {
            "goal_id": target_goal.id,
            "title": target_goal.title,
            "category": (
                target_goal.category
                or "General"
            ),
            "priority": (
                target_goal.priority
                or "High Priority"
            ),
            "target_date": target_goal.target_date,
            "progress_value": (
                target_goal.progress_value
                or 0
            ),
            "reason": reason_text,
            "next_action": next_action_text,
        }


goal_service = GoalService()