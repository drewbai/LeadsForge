from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subscription import Subscription, serialize_subscription

logger = logging.getLogger(__name__)


VALID_TARGET_TYPES = ("webhook", "email", "internal")


class SubscriptionValidationError(ValueError):
    pass


def _validate_target_type(target_type: str) -> None:
    if target_type not in VALID_TARGET_TYPES:
        raise SubscriptionValidationError(
            f"target_type must be one of {VALID_TARGET_TYPES}, got '{target_type}'"
        )


async def create_subscription(
    session: AsyncSession,
    event_type: str,
    target_type: str,
    target: str,
    is_active: bool = True,
) -> dict[str, Any]:
    if not event_type:
        raise SubscriptionValidationError("event_type is required")
    if not target:
        raise SubscriptionValidationError("target is required")
    _validate_target_type(target_type)

    subscription = Subscription(
        event_type=event_type,
        target_type=target_type,
        target=target,
        is_active=is_active,
    )
    session.add(subscription)
    await session.commit()
    await session.refresh(subscription)
    logger.info(
        "Created subscription %s event_type=%s target_type=%s",
        subscription.id,
        event_type,
        target_type,
    )
    return serialize_subscription(subscription)


async def get_subscriptions(
    session: AsyncSession,
    event_type: str | None = None,
    target_type: str | None = None,
    is_active: bool | None = True,
    limit: int = 100,
    offset: int = 0,
) -> list[dict[str, Any]]:
    stmt = select(Subscription)
    if event_type is not None:
        stmt = stmt.where(Subscription.event_type == event_type)
    if target_type is not None:
        _validate_target_type(target_type)
        stmt = stmt.where(Subscription.target_type == target_type)
    if is_active is not None:
        stmt = stmt.where(Subscription.is_active == is_active)
    stmt = stmt.order_by(Subscription.created_at.desc()).limit(limit).offset(offset)

    result = await session.execute(stmt)
    rows = result.scalars().all()
    return [serialize_subscription(row) for row in rows]


async def get_active_subscriptions_for_event(
    session: AsyncSession,
    event_type: str,
) -> list[Subscription]:
    stmt = (
        select(Subscription)
        .where(Subscription.event_type == event_type)
        .where(Subscription.is_active.is_(True))
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def deactivate_subscription(
    session: AsyncSession,
    subscription_id: UUID | str,
) -> dict[str, Any] | None:
    sid = UUID(str(subscription_id)) if not isinstance(subscription_id, UUID) else subscription_id
    stmt = (
        update(Subscription)
        .where(Subscription.id == sid)
        .values(is_active=False)
        .returning(Subscription)
    )
    result = await session.execute(stmt)
    row = result.scalar_one_or_none()
    if row is None:
        await session.commit()
        return None
    await session.commit()
    logger.info("Deactivated subscription %s", sid)
    return serialize_subscription(row)
