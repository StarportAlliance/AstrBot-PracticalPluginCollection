from datetime import datetime
from pathlib import Path
from random import randint

import aiosqlite
from astrbot.api import logger


class DailyLuckDataBase:
    """今日人品数据库。"""

    _db_path: Path
    """数据库文件路径。"""

    @classmethod
    async def init(cls, plugin_data_path: Path):
        """初始化今日人品数据库。

        Args:
            plugin_data_path (Path): 插件数据目录。
        """
        ins = cls()
        ins._db_path = plugin_data_path / "module" / "daily_luck" / "data.db"
        ins._db_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiosqlite.connect(ins._db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS daily_luck (
                    user_id TEXT PRIMARY KEY,
                    luck INTEGER NOT NULL DEFAULT 0,
                    time TEXT NOT NULL DEFAULT ''
                )
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_daily_luck_user_id
                ON daily_luck(user_id)
            """)
            await db.commit()
        logger.debug("今日人品数据库初始化完成。")
        return ins

    async def try_get_luck(self, user_id: str) -> int:
        """尝试获取用户今日幸运值，不存在则自动抽取一次。

        Args:
            user_id (str): 用户 ID。

        Returns:
            int: 用户今日幸运值。
        """
        async with aiosqlite.connect(self._db_path) as db:
            async with db.cursor() as cur:
                try:
                    await cur.execute(
                        "SELECT * FROM daily_luck WHERE user_id = ?", (user_id,)
                    )
                    row = await cur.fetchone()
                    assert row
                    # 比较时间是否为今天
                    now = datetime.now().strftime("%Y-%m-%d")
                    assert row[2] == now
                    return row[1]
                # 如果获取不到或过期就抽取
                except AssertionError:
                    luck = randint(0, 100)
                    now = datetime.now().strftime("%Y-%m-%d")
                    await cur.execute(
                        "INSERT OR REPLACE INTO daily_luck (user_id, luck, time) VALUES (?, ?, ?)",
                        (user_id, luck, now),
                    )
                    await db.commit()
                    return luck
