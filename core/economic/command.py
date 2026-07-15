from pathlib import Path

import aiosqlite
from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, MessageEventResult

from ...utils.message import MessageTemplate
from .db import EconomicSystemDatabase


class EconomicSystem(EconomicSystemDatabase):
    """经济系统。"""

    _msg_template: MessageTemplate

    _currency_name: str

    @classmethod
    async def init(cls, plugin_data_path: Path, msg_template: MessageTemplate):  # pyright: ignore[reportIncompatibleMethodOverride]
        """初始化经济系统。"""
        self = await super().init(plugin_data_path)
        self._msg_template = msg_template
        self._currency_name = self._msg_template.get_msg_template(
            "EconomicSystem", "CurrencyName"
        )
        return self

    async def sign_up(self, event: AstrMessageEvent) -> MessageEventResult:
        """为给定的用户 ID 注册账户。

        Args:
            event (AstrMessageEvent): 消息事件对象，用户 ID 将从该事件获取。

        Returns:
            MessageEventResult: 消息事件结果，调用方应通过 `yield` 使 AstrBot 消费此结果。

        Examples:
            ```python
            yield sign_up(event)
            ```
        """
        try:
            await self.create_account(event.get_sender_id())
            logger.info(f"用户 {event.get_sender_id()} 注册了银行账户。")
            return event.plain_result(
                self._msg_template.get_msg_template("EconomicSystem", "SignUpSuccess")
            )
        except aiosqlite.IntegrityError:
            logger.info(f"用户 {event.get_sender_id()} 已注册银行账户，拒绝重复注册。")
            return event.plain_result(
                self._msg_template.get_msg_template(
                    "EconomicSystem", "DuplicateAccount"
                )
            )
        except Exception:
            logger.exception(f"注册用户 {event.get_sender_id()} 的银行账户时发生错误。")
            return event.plain_result(
                self._msg_template.get_msg_template("General", "UnknownError")
            )

    async def cancel(self, event: AstrMessageEvent) -> MessageEventResult:
        """注销银行账户。

        Args:
            event (AstrMessageEvent): 消息事件对象，用户 ID 将从该事件获取。

        Returns:
            MessageEventResult: 消息事件结果，调用方应通过 `yield` 使 AstrBot 消费此结果。

        Examples:
            ```python
            yield cancel(event)
            ```
        """
        try:
            balance = await self.get_balance(event.get_sender_id())
            if balance > 0:
                logger.info(
                    f"用户 {event.get_sender_id()} 银行账户内仍有余额，拒绝注销账户。"
                )
                return event.plain_result(
                    self._msg_template.get_msg_template(
                        "EconomicSystem",
                        "RejectCancelByBalance",
                        balance=str(balance),
                        currency_name=self._currency_name,
                    )
                )
            await self.delete_account(event.get_sender_id())
            logger.info(f"用户 {event.get_sender_id()} 注销了银行账户。")
            return event.plain_result(
                self._msg_template.get_msg_template("EconomicSystem", "CancelSuccess")
            )
        except KeyError:
            logger.info(f"用户 {event.get_sender_id()} 未注册银行账户，拒绝注销账户。")
            return event.plain_result(
                self._msg_template.get_msg_template(
                    "EconomicSystem", "SelfAccountNotFound"
                )
            )
        except Exception:
            logger.exception(f"注销用户 {event.get_sender_id()} 的银行账户时发生错误。")
            return event.plain_result(
                self._msg_template.get_msg_template("General", "UnknownError")
            )

    async def balance(self, event: AstrMessageEvent) -> MessageEventResult:
        """查询给定用户 ID 的余额。

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
                    "EconomicSystem",
                    "AccountBalance",
                    balance=str(balance),
                    currency_name=self._currency_name,
                )
            )
        except KeyError:
            logger.debug(
                f"用户 {event.get_sender_id()} 未注册银行账户，拒绝查询账户余额。"
            )
            return event.plain_result(
                self._msg_template.get_msg_template(
                    "EconomicSystem", "SelfAccountNotFound"
                )
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
            target_id (str): 目标用户 ID。
            amount (int): 转账金额。

        Returns:
            MessageEventResult: 消息事件结果，调用方应通过 `yield` 使 AstrBot 消费此结果。

        Examples:
            ```python
            yield transfer(event, target_id, amount)
            ```
        """
        try:
            await self._transfer(event.get_sender_id(), target_id, amount)
            logger.info(
                f"用户 {event.get_sender_id()} 向用户 {target_id} 转账了 {amount} {self._currency_name}。"
            )
            return event.plain_result(
                self._msg_template.get_msg_template(
                    "EconomicSystem",
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
                    "EconomicSystem", "InvalidTransferAmount"
                )
            )
        except KeyError:
            logger.info(
                f"用户 {event.get_sender_id()} 尝试向未注册银行账户的用户 {target_id} 转账，拒绝转账。"
            )
            return event.plain_result(
                self._msg_template.get_msg_template(
                    "EconomicSystem", "TargetAccountNotFound"
                )
            )
        except Exception:
            logger.exception(
                f"用户 {event.get_sender_id()} 向用户 {target_id} 转账时发生错误。"
            )
            return event.plain_result(
                self._msg_template.get_msg_template("General", "UnknownError")
            )

    async def deduction(
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
                f"扣款了用户 {target_id} 银行账户 {amount} {self._currency_name}。"
            )
            return event.plain_result(
                self._msg_template.get_msg_template(
                    "EconomicSystem",
                    "DeductionSuccess",
                    target_id=target_id,
                    amount=str(amount),
                    currency_name=self._currency_name,
                )
            )
        except ValueError:
            logger.info(f"尝试扣款用户 {target_id} 的金额 {amount} 无效，拒绝扣款。")
            return event.plain_result(
                self._msg_template.get_msg_template("EconomicSystem", "InvalidAmount")
            )
        except KeyError:
            logger.info(
                f"用户 {event.get_sender_id()} 尝试扣款未注册银行账户的用户 {target_id}，拒绝扣款。"
            )
            return event.plain_result(
                self._msg_template.get_msg_template(
                    "EconomicSystem", "TargetAccountNotFound"
                )
            )
        except Exception:
            logger.exception(f"扣款用户 {target_id} 时发生错误。")
            return event.plain_result(
                self._msg_template.get_msg_template("General", "UnknownError")
            )

    async def deposit(
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
            yield deposit(event, target_id, amount)
            ```
        """
        try:
            await self.increase_balance(target_id, amount)
            logger.info(
                f"入款了用户 {target_id} 银行账户 {amount} {self._currency_name}。"
            )
            return event.plain_result(
                self._msg_template.get_msg_template(
                    "EconomicSystem",
                    "DepositSuccess",
                    target_id=target_id,
                    amount=str(amount),
                    currency_name=self._currency_name,
                )
            )
        except ValueError:
            logger.info(f"尝试入款用户 {target_id} 的金额 {amount} 无效，拒绝入款。")
            return event.plain_result(
                self._msg_template.get_msg_template("EconomicSystem", "InvalidAmount")
            )
        except KeyError:
            logger.info(
                f"用户 {event.get_sender_id()} 尝试入款未注册银行账户的用户 {target_id}，拒绝入款。"
            )
            return event.plain_result(
                self._msg_template.get_msg_template(
                    "EconomicSystem", "TargetAccountNotFound"
                )
            )
        except Exception:
            logger.exception(f"入款用户 {target_id} 时发生错误。")
            return event.plain_result(
                self._msg_template.get_msg_template("General", "UnknownError")
            )
