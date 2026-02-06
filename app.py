"""
🍽️ School Meal Image Generator — AI-Powered Demo
Uses Pollinations.ai (free, no API key) to generate realistic food images
for school meal menu systems.
"""

import streamlit as st
import requests
import urllib.parse
import io
import time
import base64
from PIL import Image
from datetime import datetime

# ─── Page Config ───
st.set_page_config(
    page_title="School Meal Image Generator",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Playfair+Display:wght@700&display=swap');

    .stApp {
        font-family: 'DM Sans', sans-serif;
    }

    .main-header {
        font-family: 'Playfair Display', serif;
        font-size: 2.4rem;
        font-weight: 700;
        background: linear-gradient(135deg, #2d6a4f, #40916c, #52b788);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
        line-height: 1.2;
    }

    .sub-header {
        color: #6c757d;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
        font-weight: 400;
    }

    .image-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 10px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        border: 1px solid #e9ecef;
    }

    .image-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.12);
    }

    .image-card img {
        border-radius: 8px;
        width: 100%;
    }

    .how-it-works {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #e9ecef;
    }

    div[data-testid="stHorizontalBlock"] > div {
        padding: 4px;
    }

    .stDownloadButton > button {
        background-color: #40916c !important;
        color: white !important;
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

# ─── Constants ───
IMAGE_SIZE = 200
REQUEST_TIMEOUT = 120

MEAL_CATEGORIES = {
    "🥗 Main Course": [
        "Chicken curry with steamed rice",
        "Spaghetti Bolognese with garlic bread",
        "Fish fingers with chips and peas",
        "Roast chicken with roast potatoes and gravy",
        "Beef lasagne with salad",
        "Vegetable stir fry with noodles",
        "Shepherd's pie with green beans",
        "Macaroni cheese with sweetcorn",
    ],
    "🥪 Light Meals": [
        "Ham and cheese sandwich on wholemeal bread",
        "Jacket potato with baked beans and cheese",
        "Cheese and tomato pizza slice",
        "Chicken wrap with lettuce and mayo",
        "Tuna pasta salad",
        "Vegetable soup with crusty bread roll",
    ],
    "🍰 Desserts": [
        "Chocolate sponge cake with custard",
        "Fresh fruit salad with yoghurt",
        "Apple crumble with custard",
        "Rice pudding with jam",
        "Strawberry jelly with ice cream",
        "Flapjack bar",
        "Carrot cake slice",
    ],
    "🥤 Sides & Drinks": [
        "Garden salad with dressing",
        "Steamed broccoli and carrots",
        "Fresh orange juice",
        "Fruit smoothie",
        "Coleslaw",
        "Garlic bread slice",
    ],
}

STYLE_PRESETS = {
    "📸 Realistic Photo": "professional food photography, realistic, natural lighting, appetizing, shot from above on a white school dinner plate, clean background, UK school canteen setting",
    "🎨 Illustrated": "digital illustration of food, clean vector style, appetizing colors, friendly cartoon style suitable for children, on a simple plate",
    "🍽️ Menu Card": "professional menu card food photo, centered on plate, white background, soft studio lighting, high resolution, appetizing presentation, clean and minimal",
    "👶 Kid-Friendly": "colorful fun food presentation for children, bright cheerful plate, playful arrangement, appealing to kids, cartoon-style background elements",
}

QUALITY_ENHANCERS = [
    "highly detailed",
    "appetizing",
    "vibrant colors",
    "professional food styling",
    "clean composition",
    "200x200 square format",
    "centered on plate",
]


# ─── Helper Functions ───
def build_prompt(food_description: str, style_prompt: str, extra_details: str = "", reference_description: str = "") -> str:
    """Assemble the full generation prompt from components."""
    parts = [
        f"A realistic photo of {food_description}",
        style_prompt,
        ", ".join(QUALITY_ENHANCERS),
    ]
    if extra_details.strip():
        parts.append(extra_details.strip())
    if reference_description.strip():
        parts.append(f"Similar style to: {reference_description}")
    parts.append("Do NOT include any text, words, letters, or watermarks in the image")
    return ", ".join(parts)


def generate_image_pollinations(prompt: str, seed: int, width: int = IMAGE_SIZE, height: int = IMAGE_SIZE) -> tuple:
    """
    Generate an image using Pollinations.ai free API.
    Returns (image_or_none, status_message, debug_info) tuple.
    """
    encoded = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&seed={seed}&nologo=true&enhance=true"

    debug = {"url": url[:200] + "...", "seed": seed}

    try:
        resp = requests.get(url, timeout=REQUEST_TIMEOUT, allow_redirects=True)
        content_type = resp.headers.get("content-type", "unknown")
        content_length = len(resp.content)
        debug["status_code"] = resp.status_code
        debug["content_type"] = content_type
        debug["content_length"] = content_length

        if resp.status_code == 200 and "image" in content_type and content_length > 500:
            img = Image.open(io.BytesIO(resp.content))
            return img, "✅ Success", debug
        elif resp.status_code == 200:
            # Got 200 but not an image — might be HTML error page
            text_preview = resp.content[:300].decode("utf-8", errors="replace")
            debug["response_preview"] = text_preview
            return None, f"❌ Got HTTP 200 but content is not an image (type: {content_type}, size: {content_length}B)", debug
        else:
            return None, f"❌ HTTP {resp.status_code}: {resp.reason}", debug

    except requests.exceptions.Timeout:
        return None, f"⏱️ Timed out after {REQUEST_TIMEOUT}s — service may be overloaded", debug
    except requests.exceptions.ConnectionError as e:
        return None, f"🔌 Connection failed: {str(e)[:150]}", debug
    except Exception as e:
        return None, f"❌ {type(e).__name__}: {str(e)[:150]}", debug


def get_image_download(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def describe_uploaded_image(filename: str) -> str:
    name = filename.rsplit(".", 1)[0].replace("_", " ").replace("-", " ")
    return f"food item resembling {name}" if name else ""


# ─── Session State Init ───
if "generated_images" not in st.session_state:
    st.session_state.generated_images = []
if "generation_count" not in st.session_state:
    st.session_state.generation_count = 0
if "debug_logs" not in st.session_state:
    st.session_state.debug_logs = []


# ─── Sidebar ───
with st.sidebar:
    st.markdown("### ⚙️ Generation Settings")

    num_variations = st.slider(
        "Number of variations", 1, 6, 3,
        help="How many image variations to generate per request",
    )

    selected_style = st.selectbox(
        "Image style preset", list(STYLE_PRESETS.keys()), index=0,
    )
    style_prompt = STYLE_PRESETS[selected_style]

    st.markdown("---")
    st.markdown("### 📋 How It Works")
    st.markdown("""
    <div class="how-it-works">
    <strong>1.</strong> Pick a meal or type your own<br>
    <strong>2.</strong> Optionally upload a reference image<br>
    <strong>3.</strong> Add extra details if needed<br>
    <strong>4.</strong> Click <em>Generate</em> 🚀<br>
    <strong>5.</strong> Download your favourites!
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📊 Session Stats")
    st.metric("Images Generated", st.session_state.generation_count)

    st.markdown("---")
    show_debug = st.checkbox("🐛 Show debug logs", value=False)

    st.markdown("---")
    st.caption("Powered by [Pollinations.ai](https://pollinations.ai) — free & open AI image generation.")
    st.caption("⚠️ First generation may take **30–90 seconds** as the model warms up.")


# ─── Main Content ───
st.markdown('<div class="main-header">🍽️ School Meal Image Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Generate realistic 200×200 menu images for your school meal system — powered by AI</div>', unsafe_allow_html=True)

# ─── Input Section ───
col_input, col_upload = st.columns([3, 2], gap="large")

with col_input:
    st.markdown("#### 🍕 Select or Describe Your Meal")

    selected_category = st.selectbox("Meal category", list(MEAL_CATEGORIES.keys()), index=0)
    preset_meals = MEAL_CATEGORIES[selected_category]

    selected_meal = st.selectbox(
        "Choose a predefined meal",
        ["— Type your own below —"] + preset_meals,
        index=0,
    )

    custom_description = st.text_area(
        "Or describe your meal item",
        placeholder="e.g. Crispy golden fish fingers with thick-cut chips, garden peas and a slice of lemon on a white plate",
        height=100,
    )

    extra_details = st.text_input(
        "Additional details (optional)",
        placeholder="e.g. extra cheese on top, served in a red bowl, with a side of ketchup",
    )

with col_upload:
    st.markdown("#### 📷 Reference Image (Optional)")
    uploaded_file = st.file_uploader(
        "Upload a reference image of how the meal should look",
        type=["png", "jpg", "jpeg", "webp"],
        help="This helps guide the style of the generated image",
    )

    if uploaded_file:
        ref_image = Image.open(uploaded_file)
        st.image(ref_image, caption="Reference image", use_container_width=True)
        ref_description = st.text_input(
            "Describe the reference image",
            value=describe_uploaded_image(uploaded_file.name),
            help="Tell the AI what aspects of this reference to use",
        )
    else:
        ref_description = ""
        st.markdown("""
        <div style="border: 2px dashed #ccc; border-radius: 12px; padding: 40px 20px;
                    text-align: center; color: #aaa; margin-top: 10px;">
            <div style="font-size: 2rem; margin-bottom: 8px;">📸</div>
            <div>Upload a reference photo to guide<br>the AI generation style</div>
        </div>
        """, unsafe_allow_html=True)

# ─── Determine final food description ───
if selected_meal != "— Type your own below —":
    food_desc = selected_meal
elif custom_description.strip():
    food_desc = custom_description.strip()
else:
    food_desc = ""

# ─── Prompt Preview ───
if food_desc:
    with st.expander("🔍 Preview assembled prompt", expanded=False):
        full_prompt = build_prompt(food_desc, style_prompt, extra_details, ref_description)
        st.code(full_prompt, language=None)
        st.caption(f"Prompt length: {len(full_prompt)} characters")

# ─── Generate Button ───
st.markdown("")
col_btn, col_clear, _ = st.columns([2, 1, 4])

with col_btn:
    generate_clicked = st.button(
        "🚀 Generate Images",
        type="primary",
        use_container_width=True,
        disabled=not food_desc,
    )

with col_clear:
    if st.button("🗑️ Clear All", use_container_width=True):
        st.session_state.generated_images = []
        st.session_state.generation_count = 0
        st.session_state.debug_logs = []
        st.rerun()

if not food_desc and generate_clicked:
    st.warning("Please select a meal or type a description first.")

# ─── Generation Logic (inside st.status for visible progress) ───
if generate_clicked and food_desc:
    full_prompt = build_prompt(food_desc, style_prompt, extra_details, ref_description)

    st.markdown("---")

    generated_batch = []
    batch_logs = []

    with st.status(
        f"🍳 Generating {num_variations} image(s) for: **{food_desc}**",
        expanded=True,
    ) as status:

        st.markdown(f"**Meal:** {food_desc}")
        st.markdown(f"**Style:** {selected_style}")
        st.caption(f"Prompt: {full_prompt[:150]}...")
        st.markdown("---")

        st.warning(
            "⏳ **Please wait patiently** — Pollinations.ai is a free service and each image "
            "can take **30–90 seconds**. The page will update automatically. "
            "**Do NOT close or refresh this page.**"
        )

        progress_bar = st.progress(0, text="Initialising...")

        for i in range(num_variations):
            progress_text = f"⏳ Generating variation {i + 1} of {num_variations}... (may take up to 90s)"
            progress_bar.progress(i / num_variations, text=progress_text)

            seed = int(time.time() * 1000) % 999999 + i * 1337
            start_time = time.time()

            st.write(f"🔄 **Variation {i + 1}/{num_variations}** — Sending request (seed: `{seed}`)...")

            img, status_msg, debug_info = generate_image_pollinations(full_prompt, seed=seed)
            elapsed = time.time() - start_time

            log_entry = {
                "time": datetime.now().strftime("%H:%M:%S"),
                "variation": i + 1,
                "status": status_msg,
                "elapsed": f"{elapsed:.1f}s",
                "debug": debug_info,
            }
            batch_logs.append(log_entry)

            if img:
                st.write(f"✅ **Variation {i + 1}** — Done in {elapsed:.1f}s")
                # Show a small preview immediately
                st.image(img, width=120, caption=f"Variation {i + 1}")
                generated_batch.append({
                    "image": img,
                    "prompt": full_prompt,
                    "food": food_desc,
                    "style": selected_style,
                    "seed": seed,
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "elapsed": f"{elapsed:.1f}s",
                })
                st.session_state.generation_count += 1
            else:
                st.error(f"⚠️ **Variation {i + 1}** failed ({elapsed:.1f}s): {status_msg}")

        progress_bar.progress(1.0, text="✅ All done!")

        success_count = len(generated_batch)
        fail_count = num_variations - success_count

        st.markdown("---")
        if success_count > 0:
            st.success(f"🎉 **{success_count}/{num_variations}** images generated successfully!")
        if fail_count > 0:
            st.warning(
                f"⚠️ {fail_count} image(s) failed. Enable '🐛 Show debug logs' "
                "in the sidebar for details."
            )
        if success_count == 0:
            st.error(
                "❌ All generations failed. This usually means Pollinations.ai is "
                "overloaded or temporarily down. Please try again in a few minutes, "
                "or try with just 1 variation."
            )

        # Update status label
        if success_count > 0:
            status.update(
                label=f"✅ Done — {success_count}/{num_variations} images generated!",
                state="complete",
                expanded=False,
            )
        else:
            status.update(
                label=f"❌ Failed — 0/{num_variations} images generated",
                state="error",
                expanded=True,
            )

    # Save logs and images to session
    st.session_state.debug_logs = batch_logs + st.session_state.debug_logs
    st.session_state.generated_images = generated_batch + st.session_state.generated_images

# ─── Debug Logs ───
if show_debug and st.session_state.debug_logs:
    with st.expander("🐛 Debug Logs", expanded=True):
        for log in st.session_state.debug_logs:
            st.markdown(
                f"**[{log['time']}] Var {log['variation']}** — "
                f"{log['status']} — {log['elapsed']}"
            )
            if "debug" in log:
                st.json(log["debug"])

# ─── Results Grid ───
st.markdown("---")
st.markdown("### 🖼️ Generated Images")

images = st.session_state.generated_images

if not images:
    placeholder_cols = st.columns(4)
    for i, pc in enumerate(placeholder_cols):
        with pc:
            st.markdown(f"""
            <div style="
                background: #f8f9fa;
                border: 2px dashed #dee2e6;
                border-radius: 12px;
                width: 100%;
                aspect-ratio: 1;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #adb5bd;
                font-size: 0.85rem;
                text-align: center;
                padding: 20px;
            ">
                <div>
                    <div style="font-size: 1.8rem; margin-bottom: 6px;">🍽️</div>
                    Slot {i + 1}<br><span style="font-size: 0.75rem;">awaiting generation</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    st.info("☝️ Select a meal and click **Generate Images** to see results here.")
else:
    cols_per_row = 4 if len(images) >= 4 else max(len(images), 1)
    for row_start in range(0, len(images), cols_per_row):
        row_images = images[row_start:row_start + cols_per_row]
        cols = st.columns(cols_per_row)
        for idx, col in enumerate(cols):
            with col:
                if idx < len(row_images):
                    item = row_images[idx]
                    img = item["image"]

                    st.markdown('<div class="image-card">', unsafe_allow_html=True)
                    st.image(img, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                    st.caption(
                        f"**{item['food'][:40]}**  \n"
                        f"{item['style']} · {item['timestamp']} · {item.get('elapsed', '')}"
                    )

                    img_bytes = get_image_download(img)
                    st.download_button(
                        "⬇ Download",
                        data=img_bytes,
                        file_name=f"meal_{item['seed']}.png",
                        mime="image/png",
                        use_container_width=True,
                        key=f"dl_{row_start}_{idx}_{item['seed']}",
                    )

# ─── Troubleshooting ───
with st.expander("🔧 Troubleshooting — Images not generating?"):
    st.markdown("""
    **Common issues and fixes:**

    1. **Slow generation (30–90s)** — Normal for Pollinations.ai free tier. First request is slowest.

    2. **Timeout errors** — Service may be overloaded. Try again in a few minutes with just 1 variation.

    3. **Connection errors** — Check your internet. Corporate firewalls/VPNs may block `image.pollinations.ai`.

    4. **Images look wrong** — Try "Realistic Photo" preset and be more specific in description.

    5. **For production** — Upgrade to paid APIs:
       - **OpenAI DALL·E 3** — ~$0.04/image, high quality
       - **Stability AI** — Stable Diffusion, cost-effective
       - **Flux Pro** — excellent photorealism
    """)

# ─── Footer ───
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #adb5bd; font-size: 0.82rem; padding: 10px 0 20px 0;">
    <strong>School Meal Image Generator</strong> — Demo for AI-powered menu image generation<br>
    Uses <a href="https://pollinations.ai" target="_blank" style="color: #40916c;">Pollinations.ai</a> · Built with Streamlit<br>
    Images are 200×200px · Optimised for school meal display systems
</div>
""", unsafe_allow_html=True)
