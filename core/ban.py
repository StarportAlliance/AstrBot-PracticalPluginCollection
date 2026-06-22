from astrbot.api import logger
from pathlib import Path
import aiosqlite
from datetime import datetime


class BanSystem:
    """封禁系统。"""

    db_path = None
    """数据库文件路径。"""

    def __init__(self, plugin_data_path: Path):
        """**请使用 BanSystem.init 方法初始化封禁系统。**"""
        self.plugin_data_path = plugin_data_path
        self.db_path = self.plugin_data_path / "core" / "ban.db"

    @classmethod
    async def init(cls, plugin_data_path: Path):
        """初始化封禁系统。

        Args:
            plugin_data_path (Path): 插件数据目录。

        Returns:
            BanSystem: 封禁系统实例。若初始化失败则返回 None。
        """
        try:
            ban_system = cls(plugin_data_path)
            async with aiosqlite.connect(ban_system.db_path) as db:
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS ban_list (
                        user_id TEXT PRIMARY KEY,
                        group_id TEXT NOT NULL DEFAULT '',
                        operator TEXT NOT NULL,
                        reason TEXT NOT NULL DEFAULT '',
                        duration INTEGER NOT NULL DEFAULT 0,
                        time TEXT NOT NULL
                    )
                """)
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS ban_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        group_id TEXT NOT NULL DEFAULT '',
                        operator TEXT NOT NULL,
                        reason TEXT NOT NULL DEFAULT '',
                        duration INTEGER NOT NULL DEFAULT 0,
                        time TEXT NOT NULL
                    )
                """)
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS action_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        action TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        operator TEXT NOT NULL,
                        time TEXT NOT NULL
                    )
                """)
                await db.commit()
            logger.info("封禁系统初始化完成。")
            return ban_system
        except Exception:
            logger.exception("初始化封禁系统时发生错误。")
            return None

    async def get_ban_list(self) -> list[dict]:
        """获取封禁列表。

        Returns:
            list[dict]: 封禁列表，每条记录格式为：
            ```
            {
                "user_id": "string",     // 被封禁的用户 ID
                "group_id": "string",    // 被哪个群聊封禁，私聊封禁则为空字符串
                "operator": "string",    // 封禁操作人 QQ 号
                "reason": "string",      // 封禁原因
                "duration": 0,           // 封禁持续时间，单位为分钟，0表示永久封禁
                "time": "2026-01-01 00:00:00"  // 封禁时间，格式为 YYYY-MM-DD HH:MM:SS
            }
            ```
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM ban_list")
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def add_ban(
        self,
        user_id: str,
        group_id: str,
        operator: str,
        reason: str = "",
        duration: int = 0,
    ) -> bool:
        """新增封禁。

        Args:
            user_id (str): 要被封禁的用户 ID。
            group_id (str): 被哪个群聊封禁，私聊封禁则为空字符串。
            operator (str): 封禁操作人 QQ 号。
            reason (str): 封禁原因，默认为空。
            duration (int): 封禁持续时间，单位为分钟，0表示永久封禁。

        Returns:
            bool: 如果封禁成功则返回 True，否则返回 False。
        """
        try:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """INSERT OR REPLACE INTO ban_list (user_id, group_id, operator, reason, duration, time)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (user_id, group_id, operator, reason, duration, now),
                )
                await db.execute(
                    """INSERT INTO ban_log (user_id, group_id, operator, reason, duration, time)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (user_id, group_id, operator, reason, duration, now),
                )
                await db.execute(
                    "INSERT INTO action_log (action, user_id, operator, time) VALUES ('ban', ?, ?, ?)",
                    (user_id, operator, now),
                )
                await db.commit()
            if duration > 0:
                logger.info(
                    f"用户 {user_id} 被 {operator} 封禁 {duration} 分钟，原因：{reason}。"
                )
            else:
                logger.info(f"用户 {user_id} 被 {operator} 永久封禁，原因：{reason}。")
            return True
        except Exception:
            logger.exception(f"封禁用户 {user_id} 时发生错误。")
            return False

    async def del_ban(self, user_id: str, operator: str) -> bool:
        """解除封禁。

        Args:
            user_id (str): 要被解封的用户 ID。
            operator (str): 解封操作人 QQ 号。
        """
        try:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "DELETE FROM ban_list WHERE user_id = ?",
                    (user_id,),
                )
                await db.execute(
                    "INSERT INTO action_log (action, user_id, operator, time) VALUES ('unban', ?, ?, ?)",
                    (user_id, operator, now),
                )
                await db.commit()
                logger.info(f"用户 {user_id} 被 {operator} 解除封禁。")
            return True
        except Exception:
            logger.exception(f"解除用户 {user_id} 的封禁时发生错误。")
            return False

    async def get_ban_log(self, user_id: str) -> list[dict]:
        """查询指定用户的封禁历史记录。

        Args:
            user_id (str): 要查询的用户 ID。

        Returns:
            list[dict]: 封禁历史记录列表，每条记录格式为：
            ```
            {
                "id": 0,                  // 自增 ID
                "user_id": "string",     // 被封禁的用户 ID
                "group_id": "string",    // 被哪个群聊封禁，私聊封禁则为空字符串
                "operator": "string",    // 封禁操作人 QQ 号
                "reason": "string",      // 封禁原因
                "duration": 0,           // 封禁持续时间，单位为分钟，0表示永久封禁
                "time": "2026-01-01 00:00:00"  // 封禁时间，格式为 YYYY-MM-DD HH:MM:SS
            }
            ```
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM ban_log WHERE user_id = ?",
                (user_id,),
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def check_user_is_banned(self, user_id: str) -> bool:
        """检查指定用户是否被封禁。

        Args:
            user_id (str): 要检查的用户 ID。

        Returns:
            bool: 如果用户被封禁则返回 True，否则返回 False。
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT * FROM ban_list WHERE user_id = ?",
                (user_id,),
            )
            row = await cursor.fetchone()
            return row is not None
