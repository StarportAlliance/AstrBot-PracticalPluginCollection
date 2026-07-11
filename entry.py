from pathlib import Path

from astrbot.api import AstrBotConfig

from .core import BanSystem, EconomicSystem
from .module import GroupRequestReview, SendLike
from .utils.message.msg import MessageTemplate


class GlobalEntry:
    """全局统一调用入口。"""

    @classmethod
    async def init(  # type: ignore
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
        cls.economic = await EconomicSystem.init(plugin_data_path)
        cls.group_request_review = await GroupRequestReview.initialize(
            plugin_data_path,
            msg_template,
            config["ModuleConfig"]["GroupRequestReview"],
            cls.ban,
        )
        cls.send_like = SendLike(msg_template)
        return cls
