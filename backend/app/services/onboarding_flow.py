from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.onboarding import OnboardingSession
from app.models.user_profile import UserProfile
from app.services import user_engagement


class OnboardingStep(str, Enum):
    WELCOME = "welcome"
    ASK_LANGUAGE = "ask_language"
    ASK_FOCUS = "ask_focus"
    COMPLETE = "complete"


async def start_onboarding(
    session: AsyncSession,
    *,
    external_id: str,
    channel: str,
    username: Optional[str] = None,
    display_name: Optional[str] = None,
) -> OnboardingSession:
    user = await user_engagement.get_or_create_user(
        session,
        external_id=external_id,
        channel=channel,
        username=username,
        display_name=display_name,
    )

    onboarding = OnboardingSession(
        user_id=user.id,
        channel=channel,
        state="started",
        answers={},
        started_at=datetime.utcnow(),
    )
    session.add(onboarding)
    await session.commit()
    await session.refresh(onboarding)

    return onboarding


async def next_step(session: AsyncSession, onboarding: OnboardingSession) -> OnboardingStep:
    del session  # session is unused in current flow but kept for API symmetry

    if onboarding.state == "started":
        return OnboardingStep.WELCOME
    if onboarding.state == "asked_language":
        return OnboardingStep.ASK_FOCUS
    if onboarding.state == "asked_focus":
        return OnboardingStep.COMPLETE

    return OnboardingStep.COMPLETE


async def apply_answer(
    session: AsyncSession,
    onboarding: OnboardingSession,
    step: OnboardingStep,
    answer: str,
) -> OnboardingSession:
    answers = onboarding.answers or {}
    user_profile = await session.get(UserProfile, onboarding.user_id)

    if step == OnboardingStep.ASK_LANGUAGE:
        answers["language"] = answer
        onboarding.state = "asked_language"
        if user_profile is not None:
            user_profile.language = answer

    elif step == OnboardingStep.ASK_FOCUS:
        answers["focus"] = answer
        onboarding.state = "completed"
        onboarding.completed_at = datetime.utcnow()
        if user_profile is not None:
            user_profile.tags = list(user_profile.tags or [])
            if answer not in user_profile.tags:
                user_profile.tags.append(answer)

    onboarding.answers = answers
    session.add(onboarding)
    await session.commit()
    await session.refresh(onboarding)

    return onboarding
