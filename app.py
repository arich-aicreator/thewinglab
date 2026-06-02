import streamlit as st
import anthropic
import httpx
import json

st.set_page_config(page_title="Wing Lab 🍗", page_icon="🍗", layout="centered")

client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def load_recipes():
    try:
        r = httpx.get(
            f"{SUPABASE_URL}/rest/v1/recipes?order=created_at.desc",
            headers=HEADERS
        )
        return r.json() if r.status_code == 200 else []
    except:
        return []

def save_recipe(name, recipe, lbs, method, vibe):
    try:
        httpx.post(
            f"{SUPABASE_URL}/rest/v1/recipes",
            headers=HEADERS,
            json={"name": name, "recipe": recipe, "lbs": lbs, "method": method, "vibe": vibe}
        )
    except:
        pass

def delete_recipe(recipe_id):
    try:
        httpx.delete(
            f"{SUPABASE_URL}/rest/v1/recipes?id=eq.{recipe_id}",
            headers=HEADERS
        )
    except:
        pass

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

QUESTIONS = [
    {"id": "sauce_base", "text": "🔥 Sauce Bases", "subtext": "What sauce bases do you have?",
     "type": "multi", "options": [
        "Hot sauce (Frank's)", "Tabasco", "Sriracha", "Sambal oelek",
        "Soy sauce", "Tamari", "Fish sauce", "Oyster sauce",
        "Ketchup", "BBQ sauce", "Hoisin sauce", "Worcestershire sauce",
        "Buffalo sauce", "Sweet chili sauce", "Teriyaki sauce", "Honey",
        "Tomato paste", "Dijon mustard", "Yellow mustard", "None of these"]},
    {"id": "acids", "text": "🍋 Acids & Brightness", "subtext": "Any acids on hand?",
     "type": "multi", "options": [
        "White vinegar", "Apple cider vinegar", "Rice vinegar", "Balsamic vinegar",
        "Lemon juice", "Fresh lemon", "Lime juice", "Fresh lime",
        "Orange juice", "Fresh orange", "Pickle juice", "None of these"]},
    {"id": "fats", "text": "🧈 Fats & Dairy", "subtext": "What fats or dairy do you have?",
     "type": "multi", "options": [
        "Butter (unsalted)", "Butter (salted)", "Ghee",
        "Olive oil", "Vegetable oil", "Canola oil", "Avocado oil",
        "Sesame oil", "Coconut oil", "Heavy cream", "Sour cream",
        "Cream cheese", "Parmesan", "Blue cheese", "None of these"]},
    {"id": "aromatics", "text": "🧄 Aromatics", "subtext": "These make a huge difference!",
     "type": "multi", "options": [
        "Fresh garlic", "Garlic powder", "Garlic paste",
        "Fresh ginger", "Ground ginger", "Ginger paste",
        "Fresh onion", "Onion powder", "Shallots", "Scallions / green onions",
        "Fresh jalapeño", "Fresh cilantro", "Fresh parsley", "Fresh rosemary",
        "Fresh thyme", "Lemongrass", "None of these"]},
    {"id": "sweeteners", "text": "🍯 Sweeteners", "subtext": "Any sweeteners?",
     "type": "multi", "options": [
        "Honey", "Brown sugar", "White sugar", "Powdered sugar",
        "Maple syrup", "Agave", "Molasses", "Corn syrup",
        "Coconut sugar", "None of these"]},
    {"id": "dry_spices", "text": "🌶️ Dry Spices", "subtext": "Check everything you've got",
     "type": "multi", "options": [
        "Salt", "Black pepper", "White pepper", "Red pepper flakes",
        "Paprika", "Smoked paprika", "Cayenne", "Chili powder",
        "Cumin", "Coriander", "Turmeric", "Curry powder",
        "Garlic powder", "Onion powder", "Oregano", "Thyme",
        "Rosemary", "Sage", "Bay leaves", "Old Bay",
        "Cajun seasoning", "Italian seasoning", "Five spice", "Sumac",
        "Baking powder", "Cornstarch", "Flour", "Panko breadcrumbs", "None of these"]},
    {"id": "cooking_method", "text": "🍳 Cooking Method", "subtext": "How are you cooking these wings?",
     "type": "single", "options": [
        "Oven baked", "Air fryer", "Deep fried",
        "Smoked", "Charcoal grill", "Gas grill", "Pan fried", "Instant pot"]},
    {"id": "flavor_vibe", "text": "🎯 Flavor Vibe", "subtext": "What are you feeling?",
     "type": "single", "options": [
        "🔥 Classic Buffalo", "🍯 Sweet & Sticky", "🌶️ Spicy Asian",
        "🍋 Bright & Tangy", "🧄 Garlic Parmesan", "🍖 Dry Rub Only",
        "🥭 Tropical Fusion", "🫚 Extra Crispy Plain", "Surprise me!"]},
]

COOKING_NOTES = {
    "Oven baked": "The user is OVEN BAKING. Include: preheat temp (425°F), wire rack on baking sheet, pat wings dry, bake time (45-50 min), flip halfway, broil last 3-5 min for extra crisp.",
    "Air fryer": "The user is using an AIR FRYER. Include: preheat to 380°F, single layer only, cook 24-28 min flipping halfway, finish at 400°F for 4 min to crisp. No overcrowding.",
    "Deep fried": "The user is DEEP FRYING. Include: oil temp 375°F, fry in batches 10-12 min, drain on rack not paper towel, double fry method for extra crisp.",
    "Smoked": "The user is SMOKING. Include: smoker temp 225-250°F, wood chip recommendation, 2-2.5 hr smoke time, then optional high heat finish for crispy skin.",
    "Charcoal grill": "The user is using a CHARCOAL GRILL. Include: two-zone fire setup, indirect heat first 20 min, then direct high heat to char and crisp, watch for flare-ups.",
    "Gas grill": "The user is using a GAS GRILL. Include: preheat to medium-high, indirect zone setup, cook 20-25 min indirect then 5-7 min direct, lid management tips.",
    "Pan fried": "The user is PAN FRYING. Include: heavy skillet or cast iron, oil depth, medium-high heat, cook in batches, 8-10 min per side, baste with sauce at end.",
    "Instant pot": "The user is using an INSTANT POT. Include: pressure cook 10 min with liquid, natural release, then broil or air fry lid finish for crispy skin. Specify liquid amount.",
}

SYSTEM_PROMPT = """You are a professional chef specializing in chicken wings.

The user will give you a list of ingredients they have, how many lbs of wings, and their cooking method.

RULES:
- SELECT only the ingredients that work well together — do NOT use everything listed
- Scale ALL measurements precisely to the exact lbs of wings provided
- Follow the cooking method instructions exactly — steps must match their equipment
- A great recipe uses 5-10 ingredients max
- Make it taste like something from a real restaurant

IMPORTANT SAUCE SCALING RULE:
- Always make 40% MORE sauce than needed to coat the wings
- This accounts for: pan residue, coating loss during tossing, and leaving enough for dipping on the side
- Explicitly state the total sauce yield in the recipe (e.g. "Makes ~1.5 cups — enough to coat and dip")
- Split the sauce into two uses in the instructions: 2/3 for tossing the wings, 1/3 reserved for dipping
- Never under-sauce. A dry wing is a failed wing.

Format using markdown:
### Recipe Name
Creative, appetizing name

### Ingredients You'll Need
Exact amounts scaled to their wing quantity — sauce ingredients scaled up 40%

### The Sauce / Dry Rub
How to make it with exact scaled measurements — include total yield

### Wing Prep & Coating
How to prep and coat the wings

### Cooking Instructions
Step-by-step SPECIFIC to their cooking method and equipment

### Pro Tips
2-3 tips specific to their cooking method

### Serving Suggestion
Simple dip or garnish using ingredients they already have"""

if "step" not in st.session_state:
    st.session_state.step = 0
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "recipe" not in st.session_state:
    st.session_state.recipe = ""
if "recipe_name" not in st.session_state:
    st.session_state.recipe_name = ""
if "saved_recipes" not in st.session_state:
    st.session_state.saved_recipes = []
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "builder"
if "wing_lbs" not in st.session_state:
    st.session_state.wing_lbs = 2.0
if "mystery_result" not in st.session_state:
    st.session_state.mystery_result = ""

# ── TAB NAV ────────────────────────────────────────────────────────────────────
saved_count = len(st.session_state.saved_recipes)
book_label = f"📒 Recipe Book ({saved_count})" if saved_count > 0 else "📒 Recipe Book"

st.markdown("""
<div class="wl-header">
  <div class="wl-header-left">
    <div class="wl-icon">🍗</div>
    <div>
      <div class="wl-title">Wing Lab</div>
      <div class="wl-sub">Your personal wing recipe builder</div>
    </div>
  </div>
  <div class="wl-header-tag">Chef's Kitchen</div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([2, 1.2, 1.2])
with col1:
    if st.button("🍗 Wing Builder", key="tab_builder",
                 type="primary" if st.session_state.active_tab == "builder" else "secondary"):
        st.session_state.active_tab = "builder"
        st.rerun()
with col2:
    if st.button("🎲 Mystery Wing", key="tab_mystery",
                 type="primary" if st.session_state.active_tab == "mystery" else "secondary"):
        st.session_state.active_tab = "mystery"
        st.rerun()
with col3:
    if st.button(book_label, key="tab_book",
                 type="primary" if st.session_state.active_tab == "book" else "secondary"):
        st.session_state.active_tab = "book"
        st.rerun()

st.markdown('<div class="wl-tab-divider"></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB: WING BUILDER
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.active_tab == "builder":
    step = st.session_state.step

    if step == 0:
        st.markdown("""
        <div class="wl-intro-grid">
          <div class="wl-intro-main">
            <div class="wl-intro-label">Welcome to the Lab</div>
            <div class="wl-intro-title">Build your perfect wing recipe from what's already in your kitchen.</div>
            <div class="wl-intro-body">
              No grocery run needed. Answer 8 simple questions about your pantry
              and we'll craft a restaurant-quality recipe just for you.
            </div>
            <div class="wl-intro-stats">
              <div class="wl-stat"><span>8</span>Questions</div>
              <div class="wl-stat"><span>100%</span>Custom</div>
              <div class="wl-stat"><span>∞</span>Variations</div>
            </div>
          </div>
          <div class="wl-intro-side">
            <div class="wl-tip-card">
              <div class="wl-tip-title">💡 Chef's Tip</div>
              <div class="wl-tip-body">The secret to crispy wings is baking powder in the dry rub — we'll tell you exactly how much.</div>
            </div>
            <div class="wl-tip-card" style="margin-top:1rem">
              <div class="wl-tip-title">🔥 Did you know?</div>
              <div class="wl-tip-body">Buffalo wings were invented in 1964 at the Anchor Bar in Buffalo, NY — by accident.</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="wl-section-divider">
          <span>🍗 Before we start</span>
        </div>
        """, unsafe_allow_html=True)

        wing_lbs = st.slider("How many lbs of wings do you have?",
                             min_value=0.5, max_value=10.0, value=2.0, step=0.5,
                             key="lbs_slider")
        st.session_state.wing_lbs = wing_lbs
        servings = int(wing_lbs / 0.5)
        st.markdown(f'<div class="wl-lbs-est">~ {servings} servings · {wing_lbs} lbs</div>', unsafe_allow_html=True)

        if st.button("Let's build my wings →"):
            st.session_state.step = 1
            st.rerun()

    elif 1 <= step <= len(QUESTIONS):
        q = QUESTIONS[step - 1]
        is_last = step == len(QUESTIONS)
        pct = int((step / len(QUESTIONS)) * 100)

        st.markdown(f"""
        <div class="wl-progress-wrap">
          <div class="wl-progress-track">
            <div class="wl-progress-fill" style="width:{pct}%"></div>
          </div>
          <div class="wl-progress-meta">
            <span class="wl-progress-label">Question {step} of {len(QUESTIONS)}</span>
            <span class="wl-progress-pct">{pct}%</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="wl-q-header">
          <div class="wl-q-number">Q{step}</div>
          <div>
            <div class="wl-q-title">{q["text"]}</div>
            <div class="wl-q-sub">{q["subtext"]}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        if q["type"] == "multi":
            selected = []
            cols = st.columns(2)
            for i, opt in enumerate(q["options"]):
                with cols[i % 2]:
                    if st.checkbox(opt, key=f"q{step}_{opt}"):
                        selected.append(opt)

            custom_placeholders = {
                1: "e.g. gochujang, miso paste, buffalo sauce, peri peri...",
                2: "e.g. yuzu juice, tamarind, pomegranate molasses...",
                3: "e.g. duck fat, bacon grease, tahini, mascarpone...",
                4: "e.g. lemongrass paste, galangal, dried chili flakes, chives...",
                5: "e.g. date syrup, palm sugar, condensed milk, honey powder...",
                6: "e.g. sumac, za'atar, berbere, ras el hanout, msg, nutritional yeast...",
            }

            custom = st.text_input(
                "✏️ Anything else not listed? Add it here:",
                key=f"custom_{step}",
                placeholder=custom_placeholders.get(step, "e.g. anything extra you have...")
            )

            if custom.strip():
                selected.append(custom.strip())

            st.markdown('<div class="wl-nav-row">', unsafe_allow_html=True)
            col_back, col_next = st.columns([1, 2])
            with col_back:
                if step > 1:
                    if st.button("← Go back", key=f"back_{step}"):
                        st.session_state.step -= 1
                        st.rerun()
            with col_next:
                btn_label = "Build my recipe 🔥" if is_last else f"Next → ({step}/{len(QUESTIONS)})"
                if st.button(btn_label, disabled=len(selected) == 0, key=f"next_{step}"):
                    st.session_state.answers[q["id"]] = selected
                    st.session_state.step = 9 if is_last else step + 1
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        else:
            for opt in q["options"]:
                if st.button(opt, key=f"opt_{step}_{opt}"):
                    st.session_state.answers[q["id"]] = [opt]
                    st.session_state.step = 9 if is_last else step + 1
                    st.rerun()

            if step > 1:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("← Go back", key=f"back_single_{step}"):
                    st.session_state.step -= 1
                    st.rerun()

    elif step == 9:
        if not st.session_state.recipe:
            with st.spinner("🔥 Your recipe is being crafted..."):
                ingredient_summary = "\n".join(
                    f"{k.replace('_', ' ')}: {', '.join(v)}"
                    for k, v in st.session_state.answers.items()
                )
                cooking_method = st.session_state.answers.get("cooking_method", ["Oven baked"])[0]
                cooking_note = COOKING_NOTES.get(cooking_method, "")
                full_prompt = (
                    f"Wing quantity: {st.session_state.wing_lbs} lbs\n"
                    f"Cooking method note: {cooking_note}\n\n"
                    f"Available ingredients:\n{ingredient_summary}\n\n"
                    "Create the best possible chicken wing recipe. Scale all measurements to the exact lbs provided."
                )
                try:
                    message = client.messages.create(
                        model="claude-sonnet-4-6",
                        max_tokens=1200,
                        system=SYSTEM_PROMPT,
                        messages=[{"role": "user", "content": full_prompt}],
                    )
                    st.session_state.recipe = message.content[0].text
                    first_line = st.session_state.recipe.split("\n")[0]
                    st.session_state.recipe_name = first_line.replace("###", "").replace("Recipe Name", "").strip() or "My Wing Recipe"
                except Exception as e:
                    st.session_state.recipe = f"❌ Error: {e}"

        st.markdown('<div class="wl-recipe-wrap">', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="wl-recipe-top">
          <div class="wl-recipe-badge">Chef's Recipe · {st.session_state.wing_lbs} lbs</div>
          <div class="wl-recipe-header">Your Custom Wing Recipe 🍗</div>
          <div class="wl-recipe-sub">Built from your pantry · Crafted by AI</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(st.session_state.recipe)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1.5, 1.5, 2])
        with col1:
            if st.button("⟵ Start over"):
                st.session_state.step = 0
                st.session_state.answers = {}
                st.session_state.recipe = ""
                st.session_state.recipe_name = ""
                st.rerun()
        with col2:
            if st.button("💾 Save to Recipe Book"):
                if st.session_state.recipe and not st.session_state.recipe.startswith("❌"):
                    save_recipe(
                        name=st.session_state.recipe_name,
                        recipe=st.session_state.recipe,
                        lbs=st.session_state.wing_lbs,
                        method=st.session_state.answers.get("cooking_method", ["?"])[0],
                        vibe=st.session_state.answers.get("flavor_vibe", ["?"])[0],
                    )
                    st.success("✅ Saved to your Recipe Book!")

# ══════════════════════════════════════════════════════════════════════════════
# TAB: MYSTERY WING
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.active_tab == "mystery":
    st.markdown("""
    <div class="wl-mystery-header">
      <div class="wl-intro-label">Mystery Wing Creator</div>
      <div class="wl-intro-title">Describe your dream wing. We'll make it happen.</div>
      <div class="wl-intro-body">
        No ingredient list needed. Just tell us what you're craving — a flavor, a feeling,
        a memory, a vibe — and our chef AI will design the perfect wing recipe for it.
      </div>
    </div>
    """, unsafe_allow_html=True)

    dream = st.text_area(
        "✨ Describe your dream wing:",
        placeholder="e.g. 'Something smoky and sweet like a BBQ joint in Nashville' or 'Crispy Korean-style with a sticky glaze and sesame' or 'Remind me of a beach vacation, tropical and spicy'",
        height=120,
        key="mystery_input"
    )

    col1, col2 = st.columns([1, 3])
    with col1:
        mystery_lbs = st.number_input("Lbs of wings:", min_value=0.5, max_value=10.0,
                                      value=2.0, step=0.5, key="mystery_lbs")
    with col2:
        mystery_method = st.selectbox("Cooking method:",
                                      ["Oven baked", "Air fryer", "Deep fried", "Smoked",
                                       "Charcoal grill", "Gas grill", "Pan fried", "Instant pot"],
                                      key="mystery_method")

    if st.button("🎲 Generate My Mystery Recipe", disabled=not dream.strip()):
        with st.spinner("🎲 Conjuring your dream wings..."):
            cooking_note = COOKING_NOTES.get(mystery_method, "")
            mystery_prompt = (
                f"The user wants: {dream}\n"
                f"Wing quantity: {mystery_lbs} lbs\n"
                f"Cooking method: {mystery_method}\n"
                f"Cooking method note: {cooking_note}\n\n"
                "Design a complete chicken wing recipe that matches their description perfectly. "
                "Create a shopping list of ingredients needed, then the full recipe. "
                "Scale everything to the exact lbs provided."
            )
            mystery_system = """You are a creative professional chef specializing in chicken wings.
The user will describe their dream wing. Your job is to design the perfect recipe to match that vision.

IMPORTANT SAUCE SCALING RULE:
- Always make 40% MORE sauce than needed to coat the wings
- Accounts for pan residue, coating loss, and extra for dipping
- Split into 2/3 for tossing, 1/3 reserved for dipping
- State total sauce yield clearly (e.g. "Makes ~1.5 cups")
- Never under-sauce. A dry wing is a failed wing.

Format using markdown:
### Recipe Name
Creative name that captures the vibe

### What You'll Need to Buy / Have Ready
Full shopping list with exact amounts scaled to their wing quantity — sauce ingredients scaled up 40%

### The Sauce / Dry Rub
How to make it with exact scaled measurements — include total yield

### Wing Prep & Coating
How to prep and coat the wings

### Cooking Instructions
Step-by-step SPECIFIC to their cooking method

### Pro Tips
2-3 tips to nail this recipe

### The Vibe
One sentence describing what makes this recipe special"""

            try:
                message = client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=1200,
                    system=mystery_system,
                    messages=[{"role": "user", "content": mystery_prompt}],
                )
                st.session_state.mystery_result = message.content[0].text
            except Exception as e:
                st.session_state.mystery_result = f"❌ Error: {e}"

    if st.session_state.mystery_result:
        st.markdown('<div class="wl-recipe-wrap">', unsafe_allow_html=True)
        st.markdown("""
        <div class="wl-recipe-top">
          <div class="wl-recipe-badge">🎲 Mystery Creation</div>
          <div class="wl-recipe-header">Your Dream Wing Recipe 🍗</div>
          <div class="wl-recipe-sub">Designed from your imagination</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(st.session_state.mystery_result)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2 = st.columns([1.5, 2])
        with col1:
            if st.button("🔄 Try another"):
                st.session_state.mystery_result = ""
                st.rerun()
        with col2:
            if st.button("💾 Save to Recipe Book", key="save_mystery"):
                first_line = st.session_state.mystery_result.split("\n")[0]
                name = first_line.replace("###", "").replace("Recipe Name", "").strip() or "Mystery Recipe"
                save_recipe(
                    name=name,
                    recipe=st.session_state.mystery_result,
                    lbs=mystery_lbs,
                    method=mystery_method,
                    vibe="🎲 Mystery",
                )
                st.success("✅ Saved to your Recipe Book!")

# ══════════════════════════════════════════════════════════════════════════════
# TAB: RECIPE BOOK
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.active_tab == "book":
    st.markdown("""
    <div class="wl-book-header">
      <div class="wl-intro-label">Your Collection</div>
      <div class="wl-intro-title">📒 Recipe Book</div>
      <div class="wl-intro-body">All your saved wing recipes in one place.</div>
    </div>
    """, unsafe_allow_html=True)

    recipes = load_recipes()
    if not recipes:
        st.markdown("""
        <div class="wl-empty-book">
          <div class="wl-empty-icon">📭</div>
          <div class="wl-empty-title">No recipes saved yet</div>
          <div class="wl-empty-body">Generate a recipe in Wing Builder or Mystery Wing, then hit Save to add it here.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for saved in recipes:
            with st.expander(f"🍗 {saved['name']} — {saved['method']} · {saved['lbs']} lbs · {saved['vibe']}"):
                st.markdown(saved["recipe"])
                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button("🗑️ Remove", key=f"delete_{saved['id']}"):
                        delete_recipe(saved["id"])
                        st.rerun()
