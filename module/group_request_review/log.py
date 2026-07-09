from datetime import datetime
from pathlib import Path
from typing import TypedDict

import aiosqlite
from astrbot.api import logger


class GroupRequestLog:
    """加群请求记录。"""

    _db_path: Path
    """数据库文件路径。"""

    class RequestRecord(TypedDict):
        """加群请求记录。"""

        id: int
        request_time: str
        user_id: str

    def __init__(self, plugin_data_path: Path):
        """初始化加群请求记录数据库静态资源。

        **请使用 GroupRequestLog.init 方法初始化完整加群请求记录数据库。**

        Args:
            plugin_data_path (Path): 插件数据目录。
        """
        self.plugin_data_path = plugin_data_path
        self._db_path = (
            self.plugin_data_path / "module" / "group_request_review" / "log.db"
        )
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        logger.debug("加群请求记录数据库静态资源初始化完成。")

    @classmethod
    async def init(cls, plugin_data_path: Path):
        """初始化加群请求记录数据库。

        Args:
            plugin_data_path (Path): 插件数据目录。

        Returns:
            GroupRequestLog: 加群请求记录数据库实例。
        """
        log = cls(plugin_data_path)
        async with aiosqlite.connect(log._db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS request_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_time TEXT NOT NULL,
                    user_id TEXT NOT NULL
                )
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_request_log_user_id
                ON request_log(user_id)
            """)
            await db.commit()
        logger.debug("加群请求记录数据库初始化完成。")
        return log

    async def add_request(self, user_id: str):
        """写入加群请求记录。

        Args:
            user_id (str): 加群者 ID。
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                "INSERT INTO request_log (request_time, user_id) VALUES (?, ?)",
                (now, user_id),
            )
            await db.commit()

    async def get_requests(
        self, user_id: str, since: str | None = None
    ) -> list[RequestRecord]:
        """查询指定用户自某个时间点以来的加群请求记录。

        Args:
            user_id (str): 要查询的用户 ID。
            since (str | None): 可选。基于给定的起始时间查询请求记录，格式为 YYYY-MM-DD HH:MM:SS。

        Returns:
            list[RequestRecord]: 加群请求记录列表，每条记录格式为：
            ```
            {
                "id": 0,                    // 自增 ID
                "request_time": "string",   // 请求时间，格式为 YYYY-MM-DD HH:MM:SS
                "user_id": "string"         // 加群者 ID
            }
            ```
        """
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM request_log WHERE user_id = ? AND request_time >= ?",
                (user_id, since),
            )
            rows = await cursor.fetchall()
            return [
                self.RequestRecord(
                    id=row["id"],
                    request_time=row["request_time"],
                    user_id=row["user_id"],
                )
                for row in rows
            ]

    async def del_request(self, user_id: str):
        """删除指定用户的所有加群请求记录。

        Args:
            user_id (str): 要删除的用户 ID。
        """
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                "DELETE FROM request_log WHERE user_id = ?",
                (user_id,),
            )
            await db.commit()
