from contextlib import asynccontextmanager
from pathlib import Path

import aiosqlite
from astrbot.api import logger


class EconomicSystem:
    """经济系统。"""

    _db_path: Path
    """数据库文件路径。"""

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
            await db.commit()
        return economic_system

    @asynccontextmanager
    async def _get_db(self, db_connection: aiosqlite.Connection | None = None):
        """检查传入的数据库连接是否有效，若无效则创建新连接。

        传入的数据库连接不会因此而关闭。

        Args:
            db_connection (aiosqlite.Connection | None, optional): 一个*薛定谔的*数据库连接。

        Yields:
            aiosqlite.Connection: 数据库连接。

        Examples:
            ```python
            async with self._get_db(db_connection) as db:
                pass
            ```
        """
        if db_connection is None:
            async with aiosqlite.connect(self._db_path) as db:
                yield db
        else:
            yield db_connection

    async def create_account(self, user_id: str):
        """新增账户。

        Args:
            user_id (str): 要注册的用户 ID。

        Raises:
            aiosqlite.IntegrityError: 如果用户 ID 已拥有银行账户。
        """
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                "INSERT INTO account (user_id, balance) VALUES (?, 0)",
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
        payer: str,
        payee: str,
        amount: int,
    ):
        """转账。

        Args:
            payer (str): 付款方用户 ID。
            payee (str): 收款方用户 ID。
            amount (int): 转账金额。
        Raises:
            ValueError: 如果转账金额无效（≤ 0）。
        """
        if amount <= 0:
            raise ValueError(f"转账金额 {amount} 无效")
        async with aiosqlite.connect(self._db_path) as db:
            await self.reduce_balance(payer, amount, db, True)
            await self.increase_balance(payee, amount, db, True)
            await db.commit()
        logger.info(f"用户 {payer} 向用户 {payee} 转账了 {amount}。")

    async def increase_balance(
        self,
        user_id: str,
        amount: int,
        db_connection: aiosqlite.Connection | None = None,
        no_commit: bool = False,
    ):
        """为给定账户增加余额。

        Args:
            user_id (str): 要增加余额的用户 ID。
            amount (int): 增加的金额。
            db_connection (aiosqlite.Connection | None, optional): **内部参数**。数据库连接对象，可选，若不提供则方法将自行初始化。
            no_commit (bool, optional): **内部参数**。是否不提交事务。

        Raises:
            ValueError: 如果目标用户不存在 / 增加金额无效（≤ 0）。
        """
        if amount <= 0:
            raise ValueError(f"增加金额 {amount} 无效")
        async with self._get_db(db_connection) as db:
            # 如果目标账户不存在，get_balance 会抛 KeyError，这里不需要二次处理
            await self.get_balance(user_id, db)
            await db.execute(
                "UPDATE account SET balance = balance + ? WHERE user_id = ?",
                (amount, user_id),
            )
            if not no_commit:
                await db.commit()
            logger.info(f"为用户 {user_id} 增加了余额 {amount}。")

    async def reduce_balance(
        self,
        user_id: str,
        amount: int,
        db_connection: aiosqlite.Connection | None = None,
        no_commit: bool = False,
    ):
        """为给定账户减少余额。

        Args:
            user_id (str): 要减少余额的用户 ID。
            amount (int): 减少的金额。
            db_connection (aiosqlite.Connection | None, optional): **内部参数**。数据库连接对象，可选，若不提供则方法将自行初始化。
            no_commit (bool, optional): **内部参数**。是否不提交事务。

        Raises:
            ValueError: 如果目标用户不存在 / 减少金额无效（≤ 0）。
        """
        if amount <= 0:
            raise ValueError(f"减少金额 {amount} 无效")
        async with self._get_db(db_connection) as db:
            if await self.get_balance(user_id, db) < amount:
                raise ValueError("目标用户余额不足")
            await db.execute(
                "UPDATE account SET balance = balance - ? WHERE user_id = ?",
                (amount, user_id),
            )
            if not no_commit:
                await db.commit()
            logger.info(f"为用户 {user_id} 减少了余额 {amount}。")

    async def get_balance(
        self, user_id: str, db_connection: aiosqlite.Connection | None = None
    ) -> int:
        """查询指定用户的账户余额。

        Args:
            user_id (str): 要查询的用户 ID。
            db_connection (aiosqlite.Connection | None, optional): **内部参数**。数据库连接对象，可选，若不提供则方法将自行初始化。

        Returns:
            int: 账户余额。

        Raises:
            KeyError: 如果账户不存在。
        """
        async with self._get_db(db_connection) as db:
            cursor = await db.execute(
                "SELECT balance FROM account WHERE user_id = ?",
                (user_id,),
            )
            row = await cursor.fetchone()
            if row:
                return row[0]
            else:
                raise KeyError(f"用户 {user_id} 不存在")
