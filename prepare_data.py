# prepare_data.py
import re
import json
from pathlib import Path
from typing import List, Dict, Optional


def extract_episode_number(filename: str) -> int:
    """从文件名中提取集数（支持中文和数字格式）"""
    match = re.search(r'第([一二三四五六七八九十零\d]+)集', filename)
    if not match:
        return 0

    num_str = match.group(1)
    chinese_num_map = {
        '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
        '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
        '零': 0
    }

    if num_str.isdigit():
        return int(num_str)
    elif num_str in chinese_num_map:
        return chinese_num_map[num_str]
    else:
        if '十' in num_str:
            parts = num_str.split('十')
            if len(parts) == 2:
                return (chinese_num_map.get(parts[0], 1) * 10 + chinese_num_map.get(parts[1], 0))
        return 0


def parse_scene(scene_text: str) -> Optional[Dict[str, any]]:
    """解析单个场景内容（精确提取人物名称）"""
    lines = [line.strip() for line in scene_text.split('\n') if line.strip()]
    if not lines or not lines[0].startswith("第") and "幕" in lines[0]:
        return None

    # 提取场景编号（第一行）
    scene_num = re.match(r'^第([一二三四五六七八九十\d]+)幕', lines[0]).group(1)

    # 第二行必须是地点（括号内容）
    location = ""
    content_start = 1  # 默认从第2行开始是内容
    if len(lines) > 1 and lines[1].startswith("（") and lines[1].endswith("）"):
        location = lines[1][1:-1]  # 去除括号
        content_start = 2

    # 提取人物和对话内容
    characters = set()
    content_lines = []

    for line in lines[content_start:]:
        # 处理人物对话行
        if "：" in line:
            # 分割出人物部分和对话部分
            parts = line.split("：", 1)
            raw_character = parts[0].strip()
            dialogue = parts[1].strip()

            # 从人物部分提取真实人物名称（去除动作描述）
            character = re.sub(r'（.*?）', '', raw_character).strip()
            if character:  # 确保不是空字符串
                characters.add(character)
                content_lines.append(f"{character}：{dialogue}")
            else:
                content_lines.append(line)
        # 动作描述（括号内容）
        elif line.startswith("（") and line.endswith("）"):
            content_lines.append(line)
        # 其他内容
        else:
            content_lines.append(f"（{line}）")

    return {
        "scene_number": scene_num,
        "location": location,
        "characters": sorted(list(characters)),
        "content": "\n".join(content_lines)
    }

def process_episode_script(content: str, episode_num: int) -> Dict:
    """处理单集剧本（修改场景分割逻辑）"""
    lines = content.split('\n')
    scenes = []
    current_scene = []
    in_scene = False

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 检测新场景开始
        if re.match(r'^第[一二三四五六七八九十\d]+幕', line):
            if current_scene:  # 保存上一个场景
                scenes.append("\n".join(current_scene))
            current_scene = [line]  # 开始新场景
            in_scene = True
        elif in_scene:
            current_scene.append(line)

    # 添加最后一个场景
    if current_scene:
        scenes.append("\n".join(current_scene))

    # 解析所有场景
    processed_scenes = []
    for scene_text in scenes:
        scene_data = parse_scene(scene_text)
        if scene_data:
            processed_scenes.append(scene_data)

    return {
        "episode_number": episode_num,
        "episode_title": f"第{episode_num}集",
        "scenes": processed_scenes
    }


def process_scripts(input_dir="scripts_raw", output_dir="processed"):
    """处理所有剧本文件"""
    Path(output_dir).mkdir(exist_ok=True)

    for script_file in Path(input_dir).glob("*.txt"):
        with open(script_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 基础清洗
        content = re.sub(r'\n{2,}', '\n', content)
        content = re.sub(r'[ \t\u3000]+', ' ', content)

        # 提取集数
        episode_num = extract_episode_number(script_file.name)
        if episode_num == 0:
            print(f"警告: 无法从文件名中提取集数: {script_file.name}")
            continue

        # 处理单集剧本
        episode_data = process_episode_script(content, episode_num)

        # 保存JSON文件
        output_file = Path(output_dir) / f"episode_{episode_num:02d}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(episode_data, f, ensure_ascii=False, indent=2)
        print(f"已处理: {script_file.name} -> {output_file.name}")


if __name__ == "__main__":
    process_scripts()