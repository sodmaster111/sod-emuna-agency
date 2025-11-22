from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.nft_amulet import NFTAmulet, NFTAmuletCollection

if TYPE_CHECKING:  # pragma: no cover - only for type hints
    from app.models.user_profile import UserProfile


async def create_collection(
    session: AsyncSession,
    *,
    code: str,
    title: str,
    description: str,
    chain: str,
    base_uri: str | None = None,
    metadata: dict | None = None,
) -> NFTAmuletCollection:
    collection = NFTAmuletCollection(
        code=code,
        title=title,
        description=description,
        chain=chain,
        base_uri=base_uri,
        metadata=metadata or {},
    )
    session.add(collection)
    await session.commit()
    await session.refresh(collection)
    return collection


async def issue_amulet_to_user(
    session: AsyncSession,
    *,
    collection: NFTAmuletCollection,
    user: "UserProfile",
    rarity: str | None = None,
    source: str = "mission_reward",
    metadata: dict | None = None,
) -> NFTAmulet:
    amulet = NFTAmulet(
        collection_id=collection.id,
        user_id=user.id,
        rarity=rarity,
        metadata=metadata or {},
        source=source,
        status="unminted",
    )
    session.add(amulet)
    await session.commit()
    await session.refresh(amulet)
    return amulet


async def link_onchain_nft(
    session: AsyncSession,
    *,
    amulet: NFTAmulet,
    ton_nft_address: str,
    token_id: str,
) -> NFTAmulet:
    amulet.ton_nft_address = ton_nft_address
    amulet.token_id = token_id
    amulet.status = "minted"
    session.add(amulet)
    await session.commit()
    await session.refresh(amulet)
    return amulet


async def get_user_amulets(
    session: AsyncSession,
    *,
    user: "UserProfile",
    chain: str | None = None,
) -> list[NFTAmulet]:
    stmt = select(NFTAmulet).where(NFTAmulet.user_id == user.id)
    if chain:
        stmt = stmt.join(NFTAmuletCollection).where(NFTAmuletCollection.chain == chain)

    result = await session.execute(stmt)
    return list(result.scalars().all())
