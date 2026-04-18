from dataclasses import asdict, dataclass

from openai import OpenAI

from catalog import DEFAULT_MODEL, DEEPSEEK_BASE_URL
from prompt import build_messages, normalize_output, parse_output


@dataclass(frozen=True)
class ProductFormData:
    product_name: str
    main_category: str
    subcategory: str
    specs: str
    tags: list[str]
    group_price: str = ""
    original_price: str = ""
    audience: str = ""
    event_type: str = ""
    extra_notes: str = ""
    style: str = "种草风"
    generation_nonce: str = ""
    previous_output: str = ""

    def cleaned(self):
        return ProductFormData(
            product_name=self.product_name.strip(),
            main_category=self.main_category.strip(),
            subcategory=self.subcategory.strip(),
            specs=self.specs.strip(),
            tags=[tag.strip() for tag in self.tags if str(tag).strip()],
            group_price=self.group_price.strip(),
            original_price=self.original_price.strip(),
            audience=self.audience.strip(),
            event_type=self.event_type.strip(),
            extra_notes=self.extra_notes.strip(),
            style=self.style.strip() or "种草风",
            generation_nonce=self.generation_nonce.strip(),
            previous_output=self.previous_output.strip(),
        )

    def to_prompt_payload(self):
        return asdict(self.cleaned())


@dataclass(frozen=True)
class GeneratedCopy:
    activity_title: str
    product_title: str
    selling_points: list[str]
    detailed_description: list[str]
    labels: list[str]

    def combined_text(self):
        return (
            f"活动标题：{self.activity_title}\n\n"
            f"商品标题：{self.product_title}\n\n"
            f"卖点短句：\n" + "\n".join(self.selling_points) + "\n\n"
            f"卖点详细描述：\n" + "\n\n".join(self.detailed_description) + "\n\n"
            f"卖点标签：{'；'.join(self.labels)}"
        )


class CopyGenerationError(RuntimeError):
    def __init__(self, message, raw_response=""):
        super().__init__(message)
        self.raw_response = raw_response


def validate_product_form(data):
    cleaned = data.cleaned()
    errors = []

    if not cleaned.product_name:
        errors.append("商品名为必填项。")
    if not cleaned.main_category:
        errors.append("品类为必填项。")
    if not cleaned.subcategory:
        errors.append("二级品类为必填项。")
    if not cleaned.specs:
        errors.append("口味/规格为必填项。")
    if not cleaned.tags:
        errors.append("核心卖点标签为必填项，请至少选择一个。")
    if len(cleaned.tags) > 5:
        errors.append("最多只能选择 5 个核心卖点标签。")

    return errors


def _extract_response_text(response):
    message = response.choices[0].message
    content = getattr(message, "content", "")

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                text_parts.append(str(item.get("text", "")))
            elif hasattr(item, "text"):
                text_parts.append(str(item.text))
        return "".join(text_parts).strip()

    return str(content or "").strip()


def generate_copy(data, api_key, model=DEFAULT_MODEL):
    cleaned = data.cleaned()
    client = OpenAI(api_key=api_key, base_url=DEEPSEEK_BASE_URL)
    response = client.chat.completions.create(
        model=model,
        messages=build_messages(cleaned.to_prompt_payload()),
        temperature=0.85,
        response_format={"type": "json_object"},
    )

    response_text = _extract_response_text(response)
    if not response_text:
        raise CopyGenerationError("模型未返回任何文案内容。")

    parsed = parse_output(response_text)
    normalized = normalize_output(parsed)
    if not normalized:
        raise CopyGenerationError("模型输出不符合预期格式，请重新生成。", raw_response=response_text)

    return GeneratedCopy(**normalized), response_text
