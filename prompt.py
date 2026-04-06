import json
import re
from functools import lru_cache
from pathlib import Path

from catalog import STYLE_HINTS

EXAMPLES_PATH = Path(__file__).parent / "examples.json"

SYSTEM_PROMPT = (
    "你是快团团食品饮料类目资深文案策划。"
    "你只输出一个合法 JSON 对象，不输出 Markdown、解释、标题或额外说明。"
)


@lru_cache(maxsize=1)
def load_examples():
    if not EXAMPLES_PATH.exists():
        return []
    try:
        return json.loads(EXAMPLES_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def build_prompt(payload):
    lines = [
        "请根据以下结构化产品信息，生成可直接复制到快团团开团页面的文案。",
        "输出必须严格为 JSON，对象键名固定为：activity_title、product_title、selling_points、detailed_description、labels。",
        "字段要求：activity_title 为 1 条；product_title 为 1 条；selling_points 必须恰好 3 条；detailed_description 为 3 到 5 段；labels 为 3 到 5 个关键词。",
        "字数要求：activity_title 30 字以内；product_title 8 到 30 字；selling_points 每条 15 字以内；detailed_description 总字数 500 字以内。",
        "商品标题优先包含品牌、品名、规格；若输入中没有品牌，不得虚构品牌。",
        "不要使用绝对化词汇，例如：最健康、纯天然、第一。",
        "健康功能描述不得夸大；涉及减肥表达时改写为控卡，涉及排毒表达时改写为轻体。",
        "不要使用平台违禁词，不要编造成分、产地、认证、销量或功效。",
        "如果补充说明中提到了过敏原、品牌、产地、认证或物流信息，应优先体现在文案里。",
        "文案要符合快团团团长与经销商的使用场景，读起来像可以直接开团发布的成品。",
        f"本次文案风格：{payload.get('style', '种草风')}。{STYLE_HINTS.get(payload.get('style', '种草风'), '')}",
        "",
        "产品信息：",
        f"商品名：{payload.get('product_name', '')}",
        f"品类：{payload.get('main_category', '')} / {payload.get('subcategory', '')}",
        f"口味/规格：{payload.get('specs', '')}",
    ]

    tags = payload.get("tags", [])
    if tags:
        lines.append(f"核心卖点标签：{', '.join(tags)}")
    if payload.get("group_price"):
        lines.append(f"团购价：{payload.get('group_price')}")
    if payload.get("original_price"):
        lines.append(f"原价：{payload.get('original_price')}")
    if payload.get("audience"):
        lines.append(f"目标人群：{payload.get('audience')}")
    if payload.get("event_type"):
        lines.append(f"活动类型：{payload.get('event_type')}")
    if payload.get("extra_notes"):
        lines.append(f"补充说明：{payload.get('extra_notes')}")

    examples = load_examples()
    if examples:
        lines.extend(["", "参考示例："])
        for example in examples[:2]:
            lines.append(f"商品名：{example.get('product_name', '')}")
            lines.append(f"品类：{example.get('category', '')}")
            lines.append(f"口味/规格：{example.get('specs', '')}")
            if example.get("tags"):
                lines.append(f"核心卖点标签：{', '.join(example.get('tags', []))}")
            lines.append("示例输出：")
            lines.append(json.dumps(example.get("output", {}), ensure_ascii=False))
            lines.append("---")

    lines.extend(
        [
            "",
            "请直接输出以下 JSON 结构，不要追加说明：",
            json.dumps(
                {
                    "activity_title": "",
                    "product_title": "",
                    "selling_points": ["", "", ""],
                    "detailed_description": ["", "", ""],
                    "labels": ["", "", ""],
                },
                ensure_ascii=False,
            ),
        ]
    )

    return "\n".join(lines)


def build_messages(payload):
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_prompt(payload)},
    ]


def parse_output(response_text):
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        start = response_text.find("{")
        end = response_text.rfind("}")
        if start != -1 and end != -1:
            try:
                return json.loads(response_text[start : end + 1])
            except json.JSONDecodeError:
                return None
        return None


def _clean_text(value):
    text = str(value or "")
    text = text.replace("\u3000", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip(" \n\t-•")


def _coerce_list(value, pattern):
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        parts = re.split(pattern, value)
        return [item for item in parts if item and item.strip()]
    return []


def _unique(items):
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            result.append(item)
            seen.add(item)
    return result


def _trim_text(text, limit):
    cleaned = _clean_text(text)
    return cleaned[:limit].strip()


def _trim_descriptions(items):
    cleaned_items = [_clean_text(item) for item in items if _clean_text(item)]
    if not cleaned_items:
        return []

    trimmed = []
    remaining = 500
    for item in cleaned_items[:5]:
        if remaining <= 0:
            break
        piece = item[:remaining].strip()
        if piece:
            trimmed.append(piece)
            remaining -= len(piece)
    return trimmed


def normalize_output(payload):
    if not isinstance(payload, dict):
        return None

    activity_title = _trim_text(payload.get("activity_title", ""), 30)
    product_title = _trim_text(payload.get("product_title", ""), 30)

    selling_points = [
        _trim_text(item, 15)
        for item in _coerce_list(payload.get("selling_points", []), r"\n{2,}|\n|；|;|，|,|、")
        if _clean_text(item)
    ][:3]

    descriptions = _trim_descriptions(
        _coerce_list(payload.get("detailed_description", []), r"\n{2,}|\n")
    )
    labels = _unique(
        [
            _clean_text(item)
            for item in _coerce_list(payload.get("labels", []), r"\n{2,}|\n|；|;|，|,|、")
            if _clean_text(item)
        ]
    )[:5]

    if not activity_title or not product_title:
        return None
    if len(product_title) < 8:
        return None
    if len(selling_points) < 3:
        return None
    if len(descriptions) < 3:
        return None
    if len(labels) < 3:
        return None

    return {
        "activity_title": activity_title,
        "product_title": product_title,
        "selling_points": selling_points,
        "detailed_description": descriptions,
        "labels": labels,
    }
