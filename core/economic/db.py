from datetime import datetime
from pathlib import Path

import aiosqlite
from astrbot.api import logger


class EconomicSystem:
    """经济系统。"""

    _db_path: Path
    """数据库文件路径。"""

    class InvalidTradingObjectError(ValueError):
        """交易对象无效。

        交易双方任意一方或双方无效，这可能是交易双方都为空、其中一方/双方未注册银行账户导致的。
        """

        def __init__(self, reason: str = ""):
            self.reason = reason

        def __str__(self):
            return self.reason

    class AmountInvalidError(ValueError):
        """交易金额无效。"""

        def __init__(self, reason: str = ""):
            """
            Args:
                reason (str, optional): 引发该异常的可选补充描述。
            """
            self.reason = reason

        def __str__(self):
            return self.reason

    class BalanceInsufficientError(ValueError):
        """余额不足。"""

        def __init__(self, reason: str = ""):
            self.reason = reason

        def __str__(self):
            return self.reason

    def __init__(self, plugin_data_path: Path):
        """初始化经济系统静态资源。

        **请使用 EconomicSystem.init 方法初始化完整经济系统。**

        Args:
            plugin_data_path (Path): 插件数据目录。
        """
        self.plugin_data_path = plugin_data_path
        self._db_path = self.plugin_data_path / "core" / "economic.db"
        logger.debug("经济系统静态资源初始化完成。")

    @classmethod
    async def init(cls, plugin_data_path: Path):
        """初始化经济系统。

        Args:
            plugin_data_path (Path): 插件数据目录。

        Returns:
            EconomicSystem: 经济系统实例。

        Raises:
            Exception: 如果初始化时发生了未知错误。
        """
        economic_system = cls(plugin_data_path)
        async with aiosqlite.connect(economic_system._db_path) as db:
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
        return economic_system

    async def create_account(self, user_id: str):
        """新增账户。

        Args:
            user_id (str): 要注册的用户 ID。

        Raises:
            aiosqlite.IntegrityError: 如果用户 ID 已拥有银行账户。
        """
        async with aiosqlite.connect(self._db_path) as db:
            sql = "INSERT INTO account (user_id, balance) VALUES (?, 0)"
            await db.execute(
                sql,
                (user_id,),
            )
            await db.commit()

    async def delete_account(self, user_id: str) -> bool:
        """删除账户。

        Args:
            user_id (str): 要删除的账户的用户 ID。

        Returns:
            bool: 若进行了删除操作则返回 True，否则返回 False。<br>
                目前，不进行删除操作仅可能是因为目标 ID 不存在银行账户导致的。

        Raises:
            Exception: 如果删除账户时发生未知错误。
        """
        async with aiosqlite.connect(self._db_path) as db:
            sql = "DELETE FROM account WHERE user_id = ?"
            cursor = await db.execute(
                sql,
                (user_id,),
            )
            await db.commit()
            if cursor.rowcount == 0:
                return False
        return True

    async def transfer(
        self,
        payer: str | None,
        payee: str | None,
        amount: int,
    ):
        """交易，将付款方的余额转给收款方。

        付款方和收款方可以有一方为空，但不能都为空。

        Args:
            payer (str | None): 付款方用户 ID。
            payee (str | None): 收款方用户 ID。
            amount (int): 交易金额。
        Raises:
            InvalidTradingObjectError: 如果付款方和收款方都为空。
            AmountInvalidError: 如果交易金额无效（≤ 0）。
            Exception: 如果交易时发生未知错误。
        """
        if payer is None and payee is None:
            raise self.InvalidTradingObjectError("付款方和收款方都为空")
        if amount <= 0:
            raise self.AmountInvalidError(f"交易金额 {amount} 无效")

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        async with aiosqlite.connect(self._db_path) as db:
            if payer is not None:
                cursor = await db.execute(
                    "SELECT balance FROM account WHERE user_id = ?",
                    (payer,),
                )
                row = await cursor.fetchone()
                if row is None:
                    raise self.InvalidTradingObjectError(f"付款方 {payer} 不存在")
                if row[0] < amount:
                    raise self.BalanceInsufficientError(f"付款方 {payer} 余额不足")
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
                    raise self.InvalidTradingObjectError(f"收款方 {payee} 不存在")
                await db.execute(
                    "UPDATE account SET balance = balance + ? WHERE user_id = ?",
                    (amount, payee),
                )
            await db.execute(
                "INSERT INTO record (payer, payee, amount, time) VALUES (?, ?, ?, ?)",
                (payer, payee, amount, now),
            )
            await db.commit()

    async def get_balance(self, user_id: str) -> int:
        """查询指定用户的账户余额。

        Args:
            user_id (str): 要查询的用户 ID。

        Returns:
            int: 账户余额。如果账户不存在则返回 -1。

        """
        async with aiosqlite.connect(self._db_path) as db:
            cursor = await db.execute(
                "SELECT balance FROM account WHERE user_id = ?",
                (user_id,),
            )
            row = await cursor.fetchone()
            return row[0] if row else -1

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
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM record WHERE payer = ? OR payee = ?",
                (user_id, user_id),
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
