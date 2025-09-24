#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
水印模板管理模块
支持保存、加载和管理水印配置模板
"""

import json
import os
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class WatermarkTemplate:
    """水印模板类"""
    
    def __init__(self, name, config, description="", created_at=None):
        """
        初始化水印模板
        
        Args:
            name (str): 模板名称
            config (dict): 水印配置
            description (str): 模板描述
            created_at (str): 创建时间
        """
        self.name = name
        self.config = config
        self.description = description
        self.created_at = created_at or datetime.now().isoformat()
    
    def to_dict(self):
        """转换为字典"""
        return {
            'name': self.name,
            'config': self.config,
            'description': self.description,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建模板"""
        return cls(
            name=data['name'],
            config=data['config'],
            description=data.get('description', ''),
            created_at=data.get('created_at')
        )


class TemplateManager:
    """模板管理器"""
    
    def __init__(self, templates_dir=None):
        """
        初始化模板管理器
        
        Args:
            templates_dir (str): 模板存储目录
        """
        if templates_dir:
            self.templates_dir = Path(templates_dir)
        else:
            # 默认使用用户主目录下的.watermark_templates
            self.templates_dir = Path.home() / '.watermark_templates'
        
        # 确保模板目录存在
        self.templates_dir.mkdir(exist_ok=True)
        self.templates_file = self.templates_dir / 'templates.json'
        
        # 加载现有模板
        self.templates = self._load_templates()
    
    def _load_templates(self):
        """加载模板文件"""
        if not self.templates_file.exists():
            return {}
        
        try:
            with open(self.templates_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {name: WatermarkTemplate.from_dict(template_data) 
                       for name, template_data in data.items()}
        except Exception as e:
            logger.error(f"加载模板文件失败: {e}")
            return {}
    
    def _save_templates(self):
        """保存模板到文件"""
        try:
            data = {name: template.to_dict() 
                   for name, template in self.templates.items()}
            
            with open(self.templates_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"模板已保存到: {self.templates_file}")
            return True
        except Exception as e:
            logger.error(f"保存模板文件失败: {e}")
            return False
    
    def save_template(self, name, config, description="", overwrite=False):
        """
        保存水印模板
        
        Args:
            name (str): 模板名称
            config (dict): 水印配置
            description (str): 模板描述
            overwrite (bool): 是否覆盖已存在的模板
            
        Returns:
            bool: 是否保存成功
        """
        if name in self.templates and not overwrite:
            logger.warning(f"模板 '{name}' 已存在，使用 overwrite=True 来覆盖")
            return False
        
        # 验证配置
        if not self._validate_config(config):
            logger.error("无效的水印配置")
            return False
        
        # 创建模板
        template = WatermarkTemplate(name, config, description)
        self.templates[name] = template
        
        # 保存到文件
        return self._save_templates()
    
    def load_template(self, name):
        """
        加载水印模板
        
        Args:
            name (str): 模板名称
            
        Returns:
            dict: 水印配置，如果模板不存在返回None
        """
        if name not in self.templates:
            logger.warning(f"模板 '{name}' 不存在")
            return None
        
        return self.templates[name].config.copy()
    
    def delete_template(self, name):
        """
        删除水印模板
        
        Args:
            name (str): 模板名称
            
        Returns:
            bool: 是否删除成功
        """
        if name not in self.templates:
            logger.warning(f"模板 '{name}' 不存在")
            return False
        
        del self.templates[name]
        return self._save_templates()
    
    def list_templates(self):
        """
        列出所有模板
        
        Returns:
            list: 模板信息列表
        """
        return [
            {
                'name': template.name,
                'description': template.description,
                'created_at': template.created_at,
                'config_summary': self._get_config_summary(template.config)
            }
            for template in self.templates.values()
        ]
    
    def _validate_config(self, config):
        """
        验证水印配置
        
        Args:
            config (dict): 水印配置
            
        Returns:
            bool: 配置是否有效
        """
        required_fields = ['font_size', 'font_color', 'position', 'opacity']
        
        for field in required_fields:
            if field not in config:
                logger.error(f"缺少必需的配置字段: {field}")
                return False
        
        # 验证数值范围
        if not (1 <= config['font_size'] <= 200):
            logger.error("字体大小必须在1-200之间")
            return False
        
        if not (0 <= config['opacity'] <= 100):
            logger.error("透明度必须在0-100之间")
            return False
        
        # 验证颜色格式
        font_color = config['font_color']
        if not (isinstance(font_color, (list, tuple)) and len(font_color) == 3 and
                all(0 <= c <= 255 for c in font_color)):
            logger.error("字体颜色必须是RGB格式的三元组")
            return False
        
        return True
    
    def _get_config_summary(self, config):
        """
        获取配置摘要
        
        Args:
            config (dict): 水印配置
            
        Returns:
            str: 配置摘要
        """
        summary_parts = []
        
        # 字体信息
        summary_parts.append(f"字体: {config['font_size']}px")
        
        # 颜色信息
        color = config['font_color']
        summary_parts.append(f"颜色: RGB({color[0]},{color[1]},{color[2]})")
        
        # 位置信息
        summary_parts.append(f"位置: {config['position']}")
        
        # 透明度
        summary_parts.append(f"透明度: {config['opacity']}%")
        
        # 输出格式
        if 'output_format' in config:
            summary_parts.append(f"格式: {config['output_format']}")
        
        return " | ".join(summary_parts)
    
    def export_template(self, name, export_path):
        """
        导出单个模板到文件
        
        Args:
            name (str): 模板名称
            export_path (str): 导出文件路径
            
        Returns:
            bool: 是否导出成功
        """
        if name not in self.templates:
            logger.error(f"模板 '{name}' 不存在")
            return False
        
        try:
            template_data = self.templates[name].to_dict()
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"模板 '{name}' 已导出到: {export_path}")
            return True
        except Exception as e:
            logger.error(f"导出模板失败: {e}")
            return False
    
    def import_template(self, import_path, overwrite=False):
        """
        从文件导入模板
        
        Args:
            import_path (str): 导入文件路径
            overwrite (bool): 是否覆盖已存在的模板
            
        Returns:
            bool: 是否导入成功
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
            
            template = WatermarkTemplate.from_dict(template_data)
            
            if template.name in self.templates and not overwrite:
                logger.warning(f"模板 '{template.name}' 已存在，使用 overwrite=True 来覆盖")
                return False
            
            # 验证配置
            if not self._validate_config(template.config):
                logger.error("导入的模板配置无效")
                return False
            
            self.templates[template.name] = template
            return self._save_templates()
            
        except Exception as e:
            logger.error(f"导入模板失败: {e}")
            return False


def main():
    """命令行工具主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='水印模板管理工具')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 列出模板
    list_parser = subparsers.add_parser('list', help='列出所有模板')
    
    # 保存模板
    save_parser = subparsers.add_parser('save', help='保存新模板')
    save_parser.add_argument('name', help='模板名称')
    save_parser.add_argument('--font-size', type=int, default=30, help='字体大小')
    save_parser.add_argument('--color', default='white', help='字体颜色')
    save_parser.add_argument('--position', default='bottom-right', help='水印位置')
    save_parser.add_argument('--opacity', type=int, default=80, help='透明度')
    save_parser.add_argument('--format', default='JPEG', help='输出格式')
    save_parser.add_argument('--quality', type=int, default=95, help='JPEG质量')
    save_parser.add_argument('--description', default='', help='模板描述')
    save_parser.add_argument('--overwrite', action='store_true', help='覆盖已存在的模板')
    
    # 删除模板
    delete_parser = subparsers.add_parser('delete', help='删除模板')
    delete_parser.add_argument('name', help='模板名称')
    
    # 导出模板
    export_parser = subparsers.add_parser('export', help='导出模板')
    export_parser.add_argument('name', help='模板名称')
    export_parser.add_argument('output', help='输出文件路径')
    
    # 导入模板
    import_parser = subparsers.add_parser('import', help='导入模板')
    import_parser.add_argument('input', help='输入文件路径')
    import_parser.add_argument('--overwrite', action='store_true', help='覆盖已存在的模板')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 创建模板管理器
    manager = TemplateManager()
    
    if args.command == 'list':
        templates = manager.list_templates()
        if not templates:
            print("没有找到任何模板")
        else:
            print(f"找到 {len(templates)} 个模板:")
            print("-" * 80)
            for template in templates:
                print(f"名称: {template['name']}")
                print(f"描述: {template['description'] or '无描述'}")
                print(f"创建时间: {template['created_at']}")
                print(f"配置: {template['config_summary']}")
                print("-" * 80)
    
    elif args.command == 'save':
        # 解析颜色
        from photo_watermark import parse_color
        font_color = parse_color(args.color)
        
        config = {
            'font_size': args.font_size,
            'font_color': font_color,
            'position': args.position,
            'opacity': args.opacity,
            'output_format': args.format,
            'jpeg_quality': args.quality
        }
        
        if manager.save_template(args.name, config, args.description, args.overwrite):
            print(f"✅ 模板 '{args.name}' 保存成功")
        else:
            print(f"❌ 模板 '{args.name}' 保存失败")
    
    elif args.command == 'delete':
        if manager.delete_template(args.name):
            print(f"✅ 模板 '{args.name}' 删除成功")
        else:
            print(f"❌ 模板 '{args.name}' 删除失败")
    
    elif args.command == 'export':
        if manager.export_template(args.name, args.output):
            print(f"✅ 模板 '{args.name}' 导出成功")
        else:
            print(f"❌ 模板 '{args.name}' 导出失败")
    
    elif args.command == 'import':
        if manager.import_template(args.input, args.overwrite):
            print("✅ 模板导入成功")
        else:
            print("❌ 模板导入失败")


if __name__ == '__main__':
    main()