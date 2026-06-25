from astrbot.api import logger
from pathlib import Path
import aiosqlite
from datetime import datetime


class EconomicSystem:
    """经济系统。"""

    db_path = None
    """数据库文件路径。"""

    def __init__(self, plugin_data_path: Path):
        """**请使用 EconomicSystem.init 方法初始化经济系统。**"""
        self.plugin_data_path = plugin_data_path
        self.db_path = self.plugin_data_path / "core" / "economic.db"

    @classmethod
    async def init(cls, plugin_data_path: Path):
        """初始化经济系统。

        Args:
            plugin_data_path (Path): 插件数据目录。

        Returns:
            EconomicSystem: 经济系统实例。若初始化失败则返回 None。
        """
        try:
            economic_system = cls(plugin_data_path)
            async with aiosqlite.connect(economic_system.db_path) as db:
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS account (
                        user_id TEXT PRIMARY KEY,
                        balance INTEGER NOT NULL DEFAULT 0
                    )
                """)
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS record (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        payer TEXT,
                        payee TEXT,
                        amount INTEGER NOT NULL,
                        time TEXT NOT NULL
                    )
                """)
                await db.commit()
            logger.info("经济系统初始化完成。")
            return economic_system
        except Exception:
            logger.exception("初始化经济系统时发生错误。")
            return None

    async def create_account(self, user_id: str) -> bool:
        """新增账户。

        Args:
            user_id (str): 要注册的用户 ID。

        Returns:
            bool: 如果注册成功则返回 True，否则返回 False。
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "INSERT INTO account (user_id, balance) VALUES (?, 0)",
                    (user_id,),
                )
                await db.commit()
            logger.info(f"用户 {user_id} 注册了银行账户。")
            return True
        except aiosqlite.IntegrityError:
            logger.warning(f"用户 {user_id} 已经注册过银行账户。")
            return False
        except Exception:
            logger.exception(f"注册用户 {user_id} 的银行账户时发生错误。")
            return False

    async def delete_account(self, user_id: str) -> bool:
        """删除账户。

        Args:
            user_id (str): 要删除的账户的用户 ID。

        Returns:
            bool: 如果删除成功则返回 True，否则返回 False。
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "DELETE FROM account WHERE user_id = ?",
                    (user_id,),
                )
                await db.commit()
            logger.info(f"用户 {user_id} 的银行账户已删除。")
            return True
        except Exception:
            logger.exception(f"删除用户 {user_id} 的银行账户时发生错误。")
            return False

    async def transfer(
        self,
        payer: str | None,
        payee: str | None,
        amount: int,
    ) -> bool:
        """交易，将付款方的余额转给收款方。

        付款方和收款方可以有一方为空，但不能都为空。

        Args:
            payer (str | None): 付款方用户 ID，可为空。
            payee (str | None): 收款方用户 ID，可为空。
            amount (int): 交易金额，必须为正整数。

        Returns:
            bool: 如果交易成功则返回 True，否则返回 False。
        """
        if payer is None and payee is None:
            logger.warning("交易失败：付款方和收款方不能同时为空。")
            return False
        if amount <= 0:
            logger.warning(f"交易失败：交易金额必须为正整数，当前值为 {amount}。")
            return False

        try:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            async with aiosqlite.connect(self.db_path) as db:
                if payer is not None:
                    cursor = await db.execute(
                        "SELECT balance FROM account WHERE user_id = ?",
                        (payer,),
                    )
                    row = await cursor.fetchone()
                    if row is None:
                        logger.warning(f"交易失败：付款方 {payer} 的账户不存在。")
                        return False
                    if row[0] < amount:
                        logger.warning(
                            f"交易失败：付款方 {payer} 余额不足（当前 {row[0]}，需要 {amount}）。"
                        )
                        return False
                    await db.execute(
                        "UPDATE account SET balance = balance - ? WHERE user_id = ?",
                        (amount, payer),
                    )
                if payee is not None:
                    cursor = await db.execute(
                        "SELECT balance FROM account WHERE user_id = ?",
                        (payee,),
                    )
                    row = await cursor.fetchone()
                    if row is None:
                        logger.warning(f"交易失败：收款方 {payee} 的账户不存在。")
                        return False
                    await db.execute(
                        "UPDATE account SET balance = balance + ? WHERE user_id = ?",
                        (amount, payee),
                    )
                await db.execute(
                    "INSERT INTO record (payer, payee, amount, time) VALUES (?, ?, ?, ?)",
                    (payer, payee, amount, now),
                )
                await db.commit()
            logger.info(
                f"交易完成：{payer or '系统'} -> {payee or '系统'}，金额 {amount}。"
            )
            return True
        except Exception:
            logger.exception("执行交易时发生错误。")
            return False

    async def get_balance(self, user_id: str) -> int | None:
        """查询指定用户的账户余额。

        Args:
            user_id (str): 要查询的用户 ID。

        Returns:
            int | None: 账户余额，若账户不存在则返回 None。
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    "SELECT balance FROM account WHERE user_id = ?",
                    (user_id,),
                )
                row = await cursor.fetchone()
                return row[0] if row else None
        except Exception:
            logger.exception(f"查询用户 {user_id} 的余额时发生错误。")
            return None

    async def get_records(self, user_id: str) -> list[dict]:
        """查询指定用户的交易记录。

        Args:
            user_id (str): 要查询的用户 ID。

        Returns:
            list[dict]: 交易记录列表，每条记录格式为：
            ```
            {
                "id": 0,              // 自增 ID
                "payer": "string",    // 付款方用户 ID，可能为空
                "payee": "string",    // 收款方用户 ID，可能为空
                "amount": 100,        // 交易金额
                "time": "2026-01-01 00:00:00"  // 交易时间，格式为 YYYY-MM-DD HH:MM:SS
            }
            ```
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM record WHERE payer = ? OR payee = ?",
                (user_id, user_id),
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
