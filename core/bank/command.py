from pathlib import Path

import aiosqlite
from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, MessageEventResult

from ...utils.message import MessageTemplate
from .db import BankSystemDatabase


class BankSystem(BankSystemDatabase):
    """银行系统。"""

    _msg_template: MessageTemplate

    _currency_name: str

    @classmethod
    async def init(cls, plugin_data_path: Path, msg_template: MessageTemplate):  # pyright: ignore[reportIncompatibleMethodOverride]
        """初始化银行系统。"""
        bank = await super().init(plugin_data_path)
        bank._msg_template = msg_template
        bank._currency_name = bank._msg_template.get_msg_template(
            "BankSystem", "CurrencyName"
        )
        logger.info("银行系统初始化完成。")
        return bank

    async def create(self, event: AstrMessageEvent) -> MessageEventResult:
        """创建银行账户。

        Args:
            event (AstrMessageEvent): 消息事件对象，用户 ID 将从该事件获取。

        Returns:
            MessageEventResult: 消息事件结果，调用方应通过 `yield` 使 AstrBot 消费此结果。

        Examples:
            ```python
            yield create(event)
            ```
        """
        try:
            await self.create_account(event.get_sender_id())
            logger.info(f"用户 {event.get_sender_id()} 创建了银行账户。")
            return event.plain_result(
                self._msg_template.get_msg_template("BankSystem", "SignUpSuccess")
            )
        except aiosqlite.IntegrityError:
            logger.info(f"用户 {event.get_sender_id()} 已创建银行账户，拒绝重复创建。")
            return event.plain_result(
                self._msg_template.get_msg_template("BankSystem", "DuplicateAccount")
            )
        except Exception:
            logger.exception(f"创建用户 {event.get_sender_id()} 的银行账户时发生错误。")
            return event.plain_result(
                self._msg_template.get_msg_template("General", "UnknownError")
            )

    async def delete(self, event: AstrMessageEvent) -> MessageEventResult:
        """删除银行账户。

        Args:
            event (AstrMessageEvent): 消息事件对象，用户 ID 将从该事件获取。

        Returns:
            MessageEventResult: 消息事件结果，调用方应通过 `yield` 使 AstrBot 消费此结果。

        Examples:
            ```python
            yield delete(event)
            ```
        """
        try:
            balance = await self.get_balance(event.get_sender_id())
            if balance > 0:
                logger.info(
                    f"用户 {event.get_sender_id()} 银行账户内仍有余额，拒绝删除账户。"
                )
                return event.plain_result(
                    self._msg_template.get_msg_template(
                        "BankSystem",
                        "RejectDeleteByBalance",
                        balance=str(balance),
                        currency_name=self._currency_name,
                    )
                )
            if not await self.delete_account(event.get_sender_id()):
                logger.info(
                    f"用户 {event.get_sender_id()} 未创建银行账户，拒绝删除账户。"
                )
                return event.plain_result(
                    self._msg_template.get_msg_template(
                        "BankSystem", "SelfAccountNotFound"
                    )
                )
            logger.info(f"用户 {event.get_sender_id()} 删除了银行账户。")
            return event.plain_result(
                self._msg_template.get_msg_template("BankSystem", "DeleteSuccess")
            )
        except Exception:
            logger.exception(f"删除用户 {event.get_sender_id()} 的银行账户时发生错误。")
            return event.plain_result(
                self._msg_template.get_msg_template("General", "UnknownError")
            )

    async def balance(self, event: AstrMessageEvent) -> MessageEventResult:
        """查询银行账户余额。

        Args:
            event (AstrMessageEvent): 消息事件对象，用户 ID 将从该事件获取。

        Returns:
            MessageEventResult: 消息事件结果，调用方应通过 `yield` 使 AstrBot 消费此结果。

        Examples:
            ```python
            yield balance(event)
            ```
        """
        try:
            balance = await self.get_balance(event.get_sender_id())
            return event.plain_result(
                self._msg_template.get_msg_template(
                    "BankSystem",
                    "AccountBalance",
                    balance=str(balance),
                    currency_name=self._currency_name,
                )
            )
        except KeyError:
            logger.debug(
                f"用户 {event.get_sender_id()} 未创建银行账户，拒绝查询账户余额。"
            )
            return event.plain_result(
                self._msg_template.get_msg_template("BankSystem", "SelfAccountNotFound")
            )
        except Exception:
            logger.exception(f"查询用户 {event.get_sender_id()} 的余额时发生错误。")
            return event.plain_result(
                self._msg_template.get_msg_template("General", "UnknownError")
            )

    async def transfer(
        self, event: AstrMessageEvent, target_id: str, amount: int
    ) -> MessageEventResult:
        """转账。

        Args:
            event (AstrMessageEvent): 消息事件对象，付款方 ID 将从该事件获取。
            target_id (str): 目标收款方 ID。
            amount (int): 转账金额。

        Returns:
            MessageEventResult: 消息事件结果，调用方应通过 `yield` 使 AstrBot 消费此结果。

        Examples:
            ```python
            yield transfer(event, target_id, amount)
            ```
        """
        try:
            await self.transfer_balance(event.get_sender_id(), target_id, amount)
            logger.info(
                f"用户 {event.get_sender_id()} 向用户 {target_id} 转账了 {amount} {self._currency_name}。"
            )
            return event.plain_result(
                self._msg_template.get_msg_template(
                    "BankSystem",
                    "TransferSuccess",
                    target_id=target_id,
                    amount=str(amount),
                    currency_name=self._currency_name,
                )
            )
        except ValueError:
            logger.info(
                f"用户 {event.get_sender_id()} 尝试向用户 {target_id} 转账的金额 {amount} 无效，拒绝转账。"
            )
            return event.plain_result(
                self._msg_template.get_msg_template(
                    "BankSystem", "InvalidTransferAmount"
                )
            )
        except KeyError:
            logger.info(
                f"用户 {event.get_sender_id()} 尝试向未创建银行账户的用户 {target_id} 转账，拒绝转账。"
            )
            return event.plain_result(
                self._msg_template.get_msg_template(
                    "BankSystem", "TargetAccountNotFound"
                )
            )
        except Exception:
            logger.exception(
                f"用户 {event.get_sender_id()} 向用户 {target_id} 转账时发生错误。"
            )
            return event.plain_result(
                self._msg_template.get_msg_template("General", "UnknownError")
            )

    async def minus(
        self, event: AstrMessageEvent, target_id: str, amount: int
    ) -> MessageEventResult:
        """从给定用户 ID 减少余额。

        Args:
            event (AstrMessageEvent): 消息事件对象
            target_id (str): 目标用户 ID。
            amount (int): 减少的金额。

        Returns:
            MessageEventResult: 消息事件结果，调用方应通过 `yield` 使 AstrBot 消费此结果。

        Examples:
            ```python
            yield deduction(event, target_id, amount)
            ```
        """
        try:
            await self.reduce_balance(target_id, amount)
            logger.info(
                f"用户 {event.get_sender_id()} 扣除了用户 {target_id} 银行账户余额 {amount} {self._currency_name}。"
            )
            return event.plain_result(
                self._msg_template.get_msg_template(
                    "BankSystem",
                    "MinusSuccess",
                    target_id=target_id,
                    amount=str(amount),
                    currency_name=self._currency_name,
                )
            )
        except ValueError:
            logger.info(
                f"用户 {event.get_sender_id()} 尝试扣除用户 {target_id} 的金额 {amount} 无效，拒绝扣除。"
            )
            return event.plain_result(
                self._msg_template.get_msg_template("BankSystem", "InvalidAmount")
            )
        except KeyError:
            logger.info(
                f"用户 {event.get_sender_id()} 尝试扣款未创建银行账户的用户 {target_id}，拒绝扣款。"
            )
            return event.plain_result(
                self._msg_template.get_msg_template(
                    "BankSystem", "TargetAccountNotFound"
                )
            )
        except Exception:
            logger.exception(
                f"用户 {event.get_sender_id()} 扣除用户 {target_id} 的银行账户余额时发生错误。"
            )
            return event.plain_result(
                self._msg_template.get_msg_template("General", "UnknownError")
            )

    async def add(
        self, event: AstrMessageEvent, target_id: str, amount: int
    ) -> MessageEventResult:
        """增加给定用户 ID 的余额。

        Args:
            event (AstrMessageEvent): 消息事件对象
            target_id (str): 目标用户 ID。
            amount (int): 增加的金额。

        Returns:
            MessageEventResult: 消息事件结果，调用方应通过 `yield` 使 AstrBot 消费此结果。

        Examples:
            ```python
            yield add(event, target_id, amount)
            ```
        """
        try:
            await self.increase_balance(target_id, amount)
            logger.info(
                f"用户 {event.get_sender_id()} 增加了用户 {target_id} 银行账户余额 {amount} {self._currency_name}。"
            )
            return event.plain_result(
                self._msg_template.get_msg_template(
                    "BankSystem",
                    "AddSuccess",
                    target_id=target_id,
                    amount=str(amount),
                    currency_name=self._currency_name,
                )
            )
        except ValueError:
            logger.info(
                f"用户 {event.get_sender_id()} 尝试增加用户 {target_id} 的金额 {amount} 无效，拒绝增加。"
            )
            return event.plain_result(
                self._msg_template.get_msg_template("BankSystem", "InvalidAmount")
            )
        except KeyError:
            logger.info(
                f"用户 {event.get_sender_id()} 尝试增加未创建银行账户的用户 {target_id}，拒绝增加。"
            )
            return event.plain_result(
                self._msg_template.get_msg_template(
                    "BankSystem", "TargetAccountNotFound"
                )
            )
        except Exception:
            logger.exception(
                f"用户 {event.get_sender_id()} 增加用户 {target_id} 的银行账户余额时发生错误。"
            )
            return event.plain_result(
                self._msg_template.get_msg_template("General", "UnknownError")
            )
