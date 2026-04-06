import json
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from catalog import DEFAULT_MODEL, EVENT_TYPES, MAIN_CATEGORIES, get_available_tags
from generation import CopyGenerationError, ProductFormData, generate_copy, validate_product_form
from prompt import load_examples

load_dotenv(dotenv_path=Path(__file__).with_name(".env"), override=False)

FORM_DEFAULTS = {
    "product_name": "",
    "specs": "",
    "selected_tags": [],
    "group_price": "",
    "original_price": "",
    "audience": "",
    "event_type": "",
    "extra_notes": "",
    "style": "种草风",
}


def copy_button(text, label, uid):
    escaped = json.dumps(text, ensure_ascii=False)
    html = f"""
        <button id='copy-{uid}' style='margin-top:8px;padding:8px 16px;border:none;border-radius:999px;background:#2563EB;color:white;cursor:pointer;font-weight:600;'>
            {label}
        </button>
        <script>
        const btn{uid} = document.getElementById('copy-{uid}');
        if (btn{uid}) {{
            btn{uid}.addEventListener('click', () => {{
                navigator.clipboard.writeText({escaped});
                btn{uid}.innerText = '已复制';
                setTimeout(() => btn{uid}.innerText = '{label}', 1200);
            }});
        }}
        </script>
    """
    st.markdown(html, unsafe_allow_html=True)


def inject_styles():
    st.markdown(
        """
        <style>
        :root {
            --ink: #1f2937;
            --muted: #5b6474;
            --line: rgba(31, 41, 55, 0.12);
            --panel: #ffffff;
            --panel-soft: #f8fafc;
            --brand: #2563eb;
            --brand-deep: #0f172a;
            --accent: #f59e0b;
            --success: #0f766e;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(37, 99, 235, 0.08), transparent 34%),
                radial-gradient(circle at top right, rgba(245, 158, 11, 0.10), transparent 28%),
                linear-gradient(180deg, #fffdf8 0%, #f8fafc 45%, #ffffff 100%);
        }

        .main .block-container {
            max-width: 1180px;
            padding-top: 2rem;
            padding-bottom: 4rem;
        }

        .hero-card {
            border-radius: 28px;
            padding: 1.8rem 1.8rem 1.9rem;
            background:
                radial-gradient(circle at 80% 15%, rgba(255,255,255,0.22), transparent 18%),
                linear-gradient(135deg, #0f172a 0%, #1d4ed8 56%, #f59e0b 140%);
            color: #ffffff;
            box-shadow: 0 24px 60px rgba(15, 23, 42, 0.18);
            margin-bottom: 1rem;
        }

        .hero-kicker {
            display: inline-flex;
            font-size: 0.78rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            padding: 0.35rem 0.7rem;
            border-radius: 999px;
            background: rgba(255,255,255,0.14);
            margin-bottom: 0.9rem;
        }

        .hero-title {
            font-size: 2.2rem;
            line-height: 1.08;
            font-weight: 800;
            margin: 0 0 0.7rem 0;
        }

        .hero-desc {
            max-width: 700px;
            color: rgba(255,255,255,0.9);
            line-height: 1.7;
            font-size: 1rem;
            margin-bottom: 0;
        }

        .mini-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 0.8rem;
            margin: 1rem 0 1.2rem;
        }

        .mini-card {
            background: rgba(255,255,255,0.8);
            border: 1px solid rgba(255,255,255,0.55);
            border-radius: 20px;
            padding: 0.95rem 1rem;
            box-shadow: 0 12px 30px rgba(15, 23, 42, 0.06);
        }

        .mini-card strong {
            display: block;
            color: var(--brand-deep);
            font-size: 1.15rem;
            margin-bottom: 0.18rem;
        }

        .mini-card span {
            color: var(--muted);
            font-size: 0.92rem;
        }

        .section-note {
            color: var(--muted);
            font-size: 0.94rem;
            margin: 0.2rem 0 0.9rem;
        }

        .tags-wrap {
            display: flex;
            flex-wrap: wrap;
            gap: 0.45rem;
            margin-top: 0.4rem;
        }

        .tag-pill {
            display: inline-flex;
            align-items: center;
            padding: 0.34rem 0.72rem;
            border-radius: 999px;
            background: #eef4ff;
            border: 1px solid rgba(37, 99, 235, 0.14);
            color: #1d4ed8;
            font-size: 0.84rem;
            font-weight: 600;
        }

        .muted-box {
            border-radius: 18px;
            padding: 0.95rem 1rem;
            background: var(--panel-soft);
            border: 1px solid var(--line);
            color: var(--muted);
            font-size: 0.92rem;
        }

        .output-card textarea {
            font-size: 0.96rem !important;
            line-height: 1.6 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def initialize_state():
    first_category = next(iter(MAIN_CATEGORIES))
    defaults = {
        "show_form": False,
        "main_category": first_category,
        "subcategory": MAIN_CATEGORIES[first_category][0],
        "generated_copy": None,
        "last_payload": None,
        "raw_response": "",
        "generation_error": "",
    }
    defaults.update(FORM_DEFAULTS)

    for key, value in defaults.items():
        st.session_state.setdefault(key, value)

    sync_category_fields()


def reset_form_fields(hide_form=False):
    first_category = next(iter(MAIN_CATEGORIES))
    st.session_state["main_category"] = first_category
    st.session_state["subcategory"] = MAIN_CATEGORIES[first_category][0]

    for key, value in FORM_DEFAULTS.items():
        st.session_state[key] = value if not isinstance(value, list) else list(value)

    st.session_state["generated_copy"] = None
    st.session_state["last_payload"] = None
    st.session_state["raw_response"] = ""
    st.session_state["generation_error"] = ""
    st.session_state["show_form"] = not hide_form


def apply_example(example):
    category_text = example.get("category", "")
    category_parts = [part.strip() for part in category_text.split("/", 1)]
    main_category = category_parts[0] if category_parts and category_parts[0] in MAIN_CATEGORIES else next(iter(MAIN_CATEGORIES))
    subcategories = MAIN_CATEGORIES.get(main_category, [])
    subcategory = category_parts[1] if len(category_parts) > 1 and category_parts[1] in subcategories else subcategories[0]

    st.session_state["show_form"] = True
    st.session_state["main_category"] = main_category
    st.session_state["subcategory"] = subcategory
    st.session_state["product_name"] = example.get("product_name", "")
    st.session_state["specs"] = example.get("specs", "")
    st.session_state["selected_tags"] = example.get("tags", [])[:5]
    st.session_state["group_price"] = ""
    st.session_state["original_price"] = ""
    st.session_state["audience"] = ""
    st.session_state["event_type"] = ""
    st.session_state["extra_notes"] = ""
    st.session_state["style"] = "种草风"
    st.session_state["generated_copy"] = None
    st.session_state["last_payload"] = None
    st.session_state["raw_response"] = ""
    st.session_state["generation_error"] = ""
    sync_category_fields()


def sync_category_fields():
    category = st.session_state.get("main_category")
    subcategories = MAIN_CATEGORIES.get(category, [])
    if subcategories and st.session_state.get("subcategory") not in subcategories:
        st.session_state["subcategory"] = subcategories[0]

    valid_tags = set(get_available_tags(category))
    selected_tags = st.session_state.get("selected_tags", [])
    st.session_state["selected_tags"] = [tag for tag in selected_tags if tag in valid_tags]


def build_form_data():
    return ProductFormData(
        product_name=st.session_state.get("product_name", ""),
        main_category=st.session_state.get("main_category", ""),
        subcategory=st.session_state.get("subcategory", ""),
        specs=st.session_state.get("specs", ""),
        tags=st.session_state.get("selected_tags", []),
        group_price=st.session_state.get("group_price", ""),
        original_price=st.session_state.get("original_price", ""),
        audience=st.session_state.get("audience", ""),
        event_type=st.session_state.get("event_type", ""),
        extra_notes=st.session_state.get("extra_notes", ""),
        style=st.session_state.get("style", "种草风"),
    )


def resolve_api_key():
    return os.getenv("DEEPSEEK_API_KEY", "").strip()


def get_generation_requirements():
    payload = build_form_data().cleaned()
    return [
        ("商品名", bool(payload.product_name)),
        ("品类", bool(payload.main_category)),
        ("二级品类", bool(payload.subcategory)),
        ("口味/规格", bool(payload.specs)),
        ("核心卖点标签", bool(payload.tags)),
    ]


def get_missing_requirements():
    return [label for label, ready in get_generation_requirements() if not ready]


def is_generation_ready():
    return not get_missing_requirements()


def has_unsaved_changes():
    last_payload = st.session_state.get("last_payload")
    if last_payload is None:
        return False
    return build_form_data().cleaned() != last_payload


def render_tag_pills(tags, empty_text="尚未选择"):
    if not tags:
        st.markdown(f"<div class='muted-box'>{empty_text}</div>", unsafe_allow_html=True)
        return

    pills = "".join(f"<span class='tag-pill'>{tag}</span>" for tag in tags)
    st.markdown(f"<div class='tags-wrap'>{pills}</div>", unsafe_allow_html=True)


def render_output_rules():
    st.markdown(
        """
        <div class="mini-grid">
            <div class="mini-card"><strong>30 字内</strong><span>活动标题</span></div>
            <div class="mini-card"><strong>8-30 字</strong><span>商品标题</span></div>
            <div class="mini-card"><strong>3 条短句</strong><span>每条 15 字内</span></div>
            <div class="mini-card"><strong>3-5 段</strong><span>详细描述总计 500 字内</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def run_generation(data=None):
    payload = data or build_form_data()
    st.session_state["generation_error"] = ""
    st.session_state["raw_response"] = ""
    errors = validate_product_form(payload)
    if errors:
        st.session_state["generated_copy"] = None
        st.session_state["generation_error"] = "\n".join(errors)
        return

    api_key = resolve_api_key()
    if not api_key:
        st.session_state["generated_copy"] = None
        st.session_state["generation_error"] = "当前服务暂不可用，请稍后再试。"
        return

    try:
        generated_copy, raw_response = generate_copy(payload, api_key=api_key, model=DEFAULT_MODEL)
    except CopyGenerationError as exc:
        st.session_state["generated_copy"] = None
        st.session_state["generation_error"] = f"生成失败：{exc}"
        st.session_state["raw_response"] = exc.raw_response
        return
    except Exception as exc:
        st.session_state["generated_copy"] = None
        st.session_state["generation_error"] = f"生成失败：{exc}"
        return

    st.session_state["generated_copy"] = generated_copy
    st.session_state["last_payload"] = payload.cleaned()
    st.session_state["raw_response"] = raw_response
    st.session_state["generation_error"] = ""


def render_intro():
    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-kicker">KUAITUANTUAN COPY STUDIO</div>
            <h1 class="hero-title">把商品信息填进去，直接拿到能开团的成品文案</h1>
            <p class="hero-desc">
                面向快团团团长与食品饮料经销商，保留结构化表单输入，重点解决“不会喂 AI”和“生成后还得重改”这两个问题。
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_output_rules()

    action_col, demo_col = st.columns([1.2, 1], gap="large")
    with action_col:
        st.markdown("**开始方式**")
        st.caption("从空白表单开始，按商品信息逐项填写。")
        if st.button("开始生成", type="primary", use_container_width=True, key="intro_start"):
            st.session_state["show_form"] = True
            st.rerun()

    with demo_col:
        st.markdown("**快速试填**")
        st.caption("先载入一个真实示例，直接查看填写方式和生成效果。")
        examples = load_examples()[:2]
        for index, example in enumerate(examples):
            label = f"试填：{example.get('product_name', '示例商品')}"
            if st.button(label, use_container_width=True, key=f"intro_example_{index}"):
                apply_example(example)
                st.rerun()

    step_cols = st.columns(3)
    steps = [
        ("1", "填商品信息", "商品名、品类、规格、卖点标签"),
        ("2", "选表达风格", "种草风、促销风、节日风"),
        ("3", "复制去开团", "逐项复制或一键复制全部"),
    ]
    for col, (num, title, desc) in zip(step_cols, steps):
        with col:
            st.markdown(
                f"""
                <div class="mini-card">
                    <strong>{num}. {title}</strong>
                    <span>{desc}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_page_header():
    st.markdown(
        """
        <div class="hero-card" style="padding:1.35rem 1.45rem 1.4rem; margin-bottom:1rem;">
            <div class="hero-kicker">WRITE FASTER</div>
            <h1 class="hero-title" style="font-size:1.7rem;">同一页面完成填写、生成、复制和重新生成</h1>
            <p class="hero-desc" style="font-size:0.97rem; max-width:780px;">
                表单保持单页形态，右侧会实时显示准备度和示例入口；移动端会自动按顺序堆叠。
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_top_toolbar():
    left, middle, right = st.columns([1, 1, 1], gap="small")

    with left:
        if st.button("返回欢迎页", use_container_width=True, key="back_to_intro"):
            st.session_state["show_form"] = False
            st.rerun()

    with middle:
        if st.button("清空表单", use_container_width=True, key="clear_form"):
            reset_form_fields()
            st.rerun()

    with right:
        examples = load_examples()
        demo_label = "试填示例"
        if examples:
            demo_label = f"试填：{examples[0].get('product_name', '示例商品')}"
        if st.button(demo_label, use_container_width=True, key="toolbar_example"):
            if examples:
                apply_example(examples[0])
                st.rerun()


def render_summary_panel():
    requirements = get_generation_requirements()
    done_count = sum(1 for _, done in requirements if done)
    total_count = len(requirements)
    progress = done_count / total_count

    with st.container(border=True):
        st.markdown("**操作面板**")
        st.progress(progress, text=f"生成准备度 {done_count}/{total_count}")

        missing = get_missing_requirements()
        if missing:
            st.caption(f"还差这些项才能生成：{'、'.join(missing)}")
        else:
            st.success("必填项已就绪，可以直接生成。")

        if has_unsaved_changes() and st.session_state.get("generated_copy") is not None:
            st.warning("你已经修改了表单，当前结果基于旧输入，建议重新生成。")

        stat_cols = st.columns(2)
        with stat_cols[0]:
            st.metric("已选标签", len(st.session_state.get("selected_tags", [])))
        with stat_cols[1]:
            st.metric("当前风格", st.session_state.get("style", "种草风"))

        st.markdown("**当前选中的卖点标签**")
        render_tag_pills(st.session_state.get("selected_tags", []), empty_text="选择 3-5 个标签，Prompt 会更稳定。")

        if st.button(
            "一键生成",
            type="primary",
            use_container_width=True,
            disabled=not is_generation_ready(),
            key="generate_from_panel",
        ):
            with st.spinner("正在生成，请稍候... 最多20秒"):
                run_generation()
            st.rerun()

        if st.button(
            "重新生成一版",
            use_container_width=True,
            disabled=st.session_state.get("last_payload") is None,
            key="regenerate_from_panel",
        ):
            with st.spinner("正在重新生成，请稍候..."):
                run_generation(st.session_state.get("last_payload"))
            st.rerun()


def render_example_panel():
    examples = load_examples()
    if not examples:
        return

    with st.container(border=True):
        st.markdown("**示例试填**")
        st.caption("不想从空白开始，可以直接套一个真实商品样本。")
        for index, example in enumerate(examples):
            category = example.get("category", "")
            label = f"{example.get('product_name', '示例商品')} | {category}"
            if st.button(label, use_container_width=True, key=f"side_example_{index}"):
                apply_example(example)
                st.rerun()


def render_form():
    st.markdown("## 产品信息")
    st.markdown("<p class='section-note'>把素材填细一些，生成结果会更接近可直接开团发布的成品。</p>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("**1. 商品基础信息**")
        basic_left, basic_right = st.columns(2, gap="medium")
        with basic_left:
            st.text_input("商品名（必填）", key="product_name", placeholder="例如：每日坚果混合装")
            st.selectbox(
                "品类（必填）",
                options=list(MAIN_CATEGORIES.keys()),
                key="main_category",
                on_change=sync_category_fields,
            )
            st.selectbox(
                "二级品类（必填）",
                options=MAIN_CATEGORIES[st.session_state["main_category"]],
                key="subcategory",
            )
        with basic_right:
            st.text_input("口味/规格（必填）", key="specs", placeholder="例如：500ml*12瓶 / 10袋装，每袋25g")
            st.text_input("目标人群（选填）", key="audience", placeholder="例如：宝妈 / 上班族 / 学生")
            st.selectbox("活动类型（选填）", options=EVENT_TYPES, key="event_type")

    with st.container(border=True):
        st.markdown("**2. 卖点与价格**")
        st.multiselect(
            "核心卖点标签（必填，最多5个）",
            options=get_available_tags(st.session_state["main_category"]),
            key="selected_tags",
            help="切换品类后会自动刷新标签选项。",
            placeholder="先选最重要的 3-5 个卖点",
        )
        price_left, price_right = st.columns(2, gap="medium")
        with price_left:
            st.text_input("团购价（选填）", key="group_price", placeholder="例如：29.9元")
        with price_right:
            st.text_input("原价（选填）", key="original_price", placeholder="例如：39.9元")

    with st.container(border=True):
        st.markdown("**3. 风格与补充说明**")
        st.radio("文案风格", ["种草风", "促销风", "节日风"], key="style", horizontal=True)
        st.text_area(
            "补充说明（选填，可填写过敏原 / 产地 / 认证 / 物流 / 适用场景等）",
            key="extra_notes",
            height=140,
            placeholder="例如：含坚果过敏原；江浙沪次日达；礼盒装适合中秋送礼",
        )

    st.markdown(
        "<div class='muted-box'>填好以后，在右侧操作面板点击“一键生成”。移动端会显示在表单下方。</div>",
        unsafe_allow_html=True,
    )


def render_messages():
    error_message = st.session_state.get("generation_error")
    if error_message:
        st.error(error_message)


def render_result_field(title, value, key, uid, copy_label, height, caption):
    with st.container(border=True):
        st.markdown(f"**{title}**")
        st.caption(caption)
        st.markdown("<div class='output-card'>", unsafe_allow_html=True)
        st.text_area("", value=value, height=height, key=key)
        st.markdown("</div>", unsafe_allow_html=True)
        copy_button(value, copy_label, uid)


def render_results():
    generated_copy = st.session_state.get("generated_copy")
    if not generated_copy:
        return

    combined_text = generated_copy.combined_text()
    description_text = "\n\n".join(generated_copy.detailed_description)
    selling_points_text = "\n".join(generated_copy.selling_points)
    labels_text = "；".join(generated_copy.labels)

    st.markdown("## 生成结果")
    st.success("文案生成完成，可以直接复制，也可以继续修改表单后重新生成。")

    stat_cols = st.columns(4)
    stats = [
        ("活动标题", f"{len(generated_copy.activity_title)}/30"),
        ("商品标题", f"{len(generated_copy.product_title)}/30"),
        ("卖点短句", f"{len(generated_copy.selling_points)} 条"),
        ("卖点标签", f"{len(generated_copy.labels)} 个"),
    ]
    for col, (label, value) in zip(stat_cols, stats):
        with col:
            st.metric(label, value)

    preview_tab, field_tab, raw_tab = st.tabs(["整段预览", "逐项复制", "模型原始返回"])

    with preview_tab:
        action_left, action_right = st.columns([1, 1], gap="small")
        with action_left:
            copy_button(combined_text, "一键复制全部", "copy_all_preview")
        with action_right:
            if st.button("基于当前输入重新生成", use_container_width=True, key="regenerate_from_result"):
                with st.spinner("正在重新生成，请稍候..."):
                    run_generation(build_form_data())
                st.rerun()

        render_result_field(
            "完整开团文案",
            combined_text,
            "result_combined",
            "copy_all_bundle",
            "复制整段成品",
            420,
            "适合直接复制到快团团对应字段，再做少量人工微调。",
        )

    with field_tab:
        left, right = st.columns([1, 1], gap="large")

        with left:
            render_result_field(
                "活动标题",
                generated_copy.activity_title,
                "result_activity_title",
                "activity",
                "复制活动标题",
                84,
                "吸睛但不过度夸张，控制在 30 字内。",
            )
            render_result_field(
                "商品标题",
                generated_copy.product_title,
                "result_product_title",
                "product",
                "复制商品标题",
                84,
                "尽量包含品名和规格，符合快团团标题结构。",
            )
            render_result_field(
                "卖点标签",
                labels_text,
                "result_labels",
                "labels",
                "复制卖点标签",
                100,
                "3-5 个关键词，可直接粘贴为商品标签。",
            )

        with right:
            render_result_field(
                "卖点短句",
                selling_points_text,
                "result_selling_points",
                "selling_points",
                "复制卖点短句",
                150,
                "共 3 条，每条尽量短而有力。",
            )
            render_result_field(
                "卖点详细描述",
                description_text,
                "result_detailed_description",
                "detailed_description",
                "复制详细描述",
                280,
                "3-5 段，总体控制在 500 字内。",
            )

    with raw_tab:
        if st.session_state.get("raw_response"):
            st.code(st.session_state["raw_response"], language="json")
        else:
            st.caption("当前没有可展示的原始返回。")


def render_help():
    with st.expander("使用说明", expanded=False):
        st.write(
            "1. 从欢迎页开始，或直接试填示例。\n"
            "2. 按顺序填写商品基础信息、卖点标签和补充说明。\n"
            "3. 右侧操作面板会实时显示缺失项和准备度。\n"
            "4. 生成后可以按字段复制，也可以整段复制。\n"
            "5. 修改表单后，建议重新生成，避免继续使用旧结果。"
        )


def main():
    st.set_page_config(page_title="快团团 AI 文案生成器", page_icon="✍️", layout="wide")
    inject_styles()
    initialize_state()

    if not st.session_state["show_form"]:
        render_intro()
        render_help()
        return

    render_page_header()
    render_top_toolbar()

    form_col, panel_col = st.columns([1.75, 1], gap="large")
    with form_col:
        render_form()
        render_messages()
    with panel_col:
        render_summary_panel()
        render_example_panel()

    render_results()
    render_help()


if __name__ == "__main__":
    main()
