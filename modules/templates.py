import streamlit as st

# Custom templates used to live in templates.json, one file on the
# server's disk shared by every visitor of this deployment — confirmed
# live: any visitor's saved template (name, description, and full
# prompt text — which can describe a real, potentially proprietary
# project) was visible to, and deletable by, every OTHER visitor too.
# Same root cause as the settings.json / API-key / history.db leaks
# fixed elsewhere this session. Custom templates now live entirely in
# st.session_state: private to each visitor, resets when they close
# their browser.
_CUSTOM_TEMPLATES_KEY = "custom_templates"

DEFAULT_TEMPLATES = [
    {
        "name": "Aerospace Frame",
        "description": "High-strength, lightweight — strength-to-weight ratio.",
        "prompt": "I need a lightweight, high-strength material for an aerospace frame. It should have excellent fatigue resistance and an outstanding strength-to-weight ratio. Low density is critical."
    },
    {
        "name": "CNC Machined Part",
        "description": "High machinability, tight tolerances, good surface finish.",
        "prompt": "I need a material that is highly machinable for CNC production. It should allow for tight tolerances, good surface finish, and minimal tool wear, while maintaining decent structural strength."
    },
    {
        "name": "Injection Molded Casing",
        "description": "Cost-effective polymer for high-volume consumer casings.",
        "prompt": "I need a cost-effective material suitable for injection molding a consumer electronics casing. It should have good impact resistance and aesthetic finish capabilities."
    },
    {
        "name": "High Temp Component",
        "description": "Retains strength at elevated temperatures.",
        "prompt": "I need a material for a component operating at elevated temperatures. It must retain high yield strength, resist thermal expansion, and offer good oxidation resistance."
    },
]

PRESETS = {
    "Drone Frame": (
        "I need a lightweight, high-strength material for a drone frame. "
        "It should be easy to machine, have good fatigue resistance, and be cost-effective. "
        "Low density is critical for flight performance."
    ),
    "Pressure Vessel": (
        "I need a material for a pressure vessel operating at elevated temperatures and pressures. "
        "It must have high yield strength, good weldability, and resistance to corrosion. "
        "Compliance with ASME standards is preferred."
    ),
    "Gear / Shaft": (
        "I need a tough, wear-resistant material for a gear or drive shaft. "
        "High yield strength, good fatigue life, and ease of heat treatment are important. "
        "The material should resist surface wear under cyclic loading."
    ),
    "Heat Exchanger": (
        "I need a material with excellent thermal conductivity and corrosion resistance "
        "for a heat exchanger application. It should withstand continuous exposure to "
        "moderate temperatures and potentially corrosive fluids."
    ),
    "Structural Bracket": (
        "I need a strong, cost-effective material for a load-bearing structural bracket. "
        "It should have adequate yield strength, be easy to fabricate (weld, drill, cut), "
        "and offer good value for money in production quantities."
    ),
    "Medical Implant": (
        "I need a biocompatible material with high fatigue strength for a medical implant. "
        "Corrosion resistance in bodily fluids, non-toxicity, and proven biocompatibility "
        "are absolute requirements. Lightweight is preferred."
    ),
    "Automotive Panel": (
        "I need a lightweight yet dent-resistant material for an automotive body panel. "
        "Good formability, paintability, and moderate cost are important. "
        "It should balance weight savings with crash energy absorption."
    ),
}

# Merge domain presets from PRESETS (dedupe by prompt text)
_PRESET_TEMPLATES = [
    {
        "name": name,
        "description": name + " preset",
        "prompt": prompt,
    }
    for name, prompt in PRESETS.items()
    if name not in {t["name"] for t in DEFAULT_TEMPLATES}
]

def load_templates():
    custom_templates = st.session_state.get(_CUSTOM_TEMPLATES_KEY, [])
    seen_prompts = set()
    merged = []
    for t in DEFAULT_TEMPLATES + _PRESET_TEMPLATES + custom_templates:
        key = t.get("prompt", "").strip()
        if key and key not in seen_prompts:
            seen_prompts.add(key)
            merged.append(t)
    return merged

def save_custom_template(name, description, prompt):
    custom_templates = st.session_state.get(_CUSTOM_TEMPLATES_KEY, [])
    custom_templates.append({
        "name": name,
        "description": description,
        "prompt": prompt,
        "is_custom": True
    })
    st.session_state[_CUSTOM_TEMPLATES_KEY] = custom_templates

def delete_custom_template(name):
    custom_templates = st.session_state.get(_CUSTOM_TEMPLATES_KEY, [])
    st.session_state[_CUSTOM_TEMPLATES_KEY] = [t for t in custom_templates if t["name"] != name]
