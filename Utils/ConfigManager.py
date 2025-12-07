# Utils/ConfigManager.py
import json
import os
from typing import Dict, Any

class ConfigManager:
    def __init__(self, path: str = "config.json"):
        self.path = path

    def load(self) -> Dict[str, Any]:
        """读取配置文件"""
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"配置文件读取失败：{e}")
                return {}
        return {}

    def save(self, data: Dict[str, Any]) -> None:
        """保存配置文件"""
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"配置文件保存失败：{e}")