import json
import os

TEMPLATES_FILE = "templates.json"

DEFAULT_TEMPLATES = [
    {
        "name": "🛩️ Aerospace Frame",
        "description": "High-strength, lightweight material suitable for aerospace applications.",
        "prompt": "I need a lightweight, high-strength material for an aerospace frame. It should have excellent fatigue resistance and an outstanding strength-to-weight ratio. Low density is critical."
    },
    {
        "name": "⚙️ CNC Machined Part",
        "description": "Material optimized for high machinability and tight tolerances.",
        "prompt": "I need a material that is highly machinable for CNC production. It should allow for tight tolerances, good surface finish, and minimal tool wear, while maintaining decent structural strength."
    },
    {
        "name": "💉 Injection Molded Casing",
        "description": "Polymer or easily moldable material for high-volume casing.",
        "prompt": "I need a cost-effective material suitable for injection molding a consumer electronics casing. It should have good impact resistance and aesthetic finish capabilities."
    },
    {
        "name": "🔥 High Temp Component",
        "description": "Material that retains strength at elevated temperatures.",
        "prompt": "I need a material for a component operating at elevated temperatures. It must retain high yield strength, resist thermal expansion, and offer good oxidation resistance."
    }
]

def load_templates():
    custom_templates = []
    if os.path.exists(TEMPLATES_FILE):
        try:
            with open(TEMPLATES_FILE, "r", encoding="utf-8") as f:
                custom_templates = json.load(f)
        except Exception:
            pass
    return DEFAULT_TEMPLATES + custom_templates

def save_custom_template(name, description, prompt):
    custom_templates = []
    if os.path.exists(TEMPLATES_FILE):
        try:
            with open(TEMPLATES_FILE, "r", encoding="utf-8") as f:
                custom_templates = json.load(f)
        except Exception:
            pass
            
    custom_templates.append({
        "name": name,
        "description": description,
        "prompt": prompt,
        "is_custom": True
    })
    
    with open(TEMPLATES_FILE, "w", encoding="utf-8") as f:
        json.dump(custom_templates, f, indent=4)

def delete_custom_template(name):
    if not os.path.exists(TEMPLATES_FILE):
        return
        
    try:
        with open(TEMPLATES_FILE, "r", encoding="utf-8") as f:
            custom_templates = json.load(f)
    except Exception:
        return
        
    custom_templates = [t for t in custom_templates if t["name"] != name]
    
    with open(TEMPLATES_FILE, "w", encoding="utf-8") as f:
        json.dump(custom_templates, f, indent=4)
