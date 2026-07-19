from pathlib import Path

from astrbot.api import AstrBotConfig

from .core import BankSystem, BanSystem
from .module import GroupRequestReview, SendLike
from .utils.message.msg import MessageTemplate


class GlobalEntry:
    """全局统一调用入口。"""

    @classmethod
    async def init(
        cls,
        plugin_data_path: Path,
        config: AstrBotConfig,
        msg_template: MessageTemplate,
    ):
        """初始化全局统一调用入口。

        Args:
            plugin_data_path (Path): 插件数据路径。
            config (AstrBotConfig): 插件配置。
            msg_template (MessageTemplate): 消息模板。
        """
        cls.ban = BanSystem(config, msg_template)
        cls.bank = await BankSystem.init(plugin_data_path, msg_template)
        if config["ModuleConfig"]["GroupRequestReview"]["Enable"]:
            cls.group_request_review = await GroupRequestReview.init(
                plugin_data_path,
                msg_template,
                config["ModuleConfig"]["GroupRequestReview"],
                cls.ban,
            )
        if config["ModuleConfig"]["EnableSendLike"]:
            cls.send_like = SendLike(msg_template)
        return cls
