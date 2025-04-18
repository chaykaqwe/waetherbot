from database.models import async_session
from database.models import User
from sqlalchemy import select


async def commit_user(data, tg_id):
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.tg_id == tg_id)
        )
        user = result.scalar_one_or_none()

        if user:
            user.city = data["your_city"]
            user.time = data["time"]
        else:
            user = User(
                tg_id=tg_id,
                city=data["your_city"],
                time=data["time"]
            )
            session.add(user)

        await session.commit()


async def giv_newletters(tg_id):
    async with async_session() as session:
        stmt = select(User).where(User.tg_id == tg_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()