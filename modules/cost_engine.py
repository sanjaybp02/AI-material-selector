import requests
import os


def fetch_live_metal_price(material_name):
    """
    Fetch live metal price from MetalPriceAPI.

    Returns
    -------
    (price_per_kg_inr, error_message)
        price is float or None, error is str or None.
    """
    api_key = os.getenv("METALPRICE_API_KEY", "***REMOVED-METALPRICEAPI-KEY-REVOKED***")
    mat_lower = material_name.lower()
    symbol = None
    if "aluminum" in mat_lower or "alumin" in mat_lower:
        symbol = "ALU"
    elif "copper" in mat_lower:
        symbol = "COP"
    elif "steel" in mat_lower or "iron" in mat_lower:
        symbol = "STEEL"
    elif "titanium" in mat_lower:
        symbol = "TI"
    elif "zinc" in mat_lower or "zamak" in mat_lower:
        symbol = "ZNC"
    elif "lead" in mat_lower:
        symbol = "LEAD"
    elif "gold" in mat_lower:
        symbol = "XAU"
    elif "silver" in mat_lower:
        symbol = "XAG"
    elif "nickel" in mat_lower:
        symbol = "NI"
    elif "tungsten" in mat_lower:
        symbol = "W"

    if not symbol:
        return None, "Material not supported by MetalPrice API"

    url = f"https://api.metalpriceapi.com/v1/latest?api_key={api_key}&base=INR&currencies={symbol}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if data.get("success"):
            rate_key = f"INR{symbol}" if f"INR{symbol}" in data.get("rates", {}) else symbol
            rate = data.get("rates", {}).get(rate_key)
            if rate:
                price = 1 / float(rate)
                if symbol in ["ALU", "COP", "STEEL", "TI", "ZNC", "LEAD", "NI", "W"]:
                    price = price / 1000  # Convert from Metric Ton to Kg
                elif symbol in ["XAU", "XAG"]:
                    price = price / 0.0311035  # Convert from Troy Ounce to Kg
                return price, None
            else:
                return None, "Symbol not found in response rates"
        else:
            err = data.get("error", {}).get("message", "Unknown API error")
            return None, f"API Error: {err}"
    except Exception as e:
        return None, str(e)


def calculate_part_cost(matched_row, part_volume, cost_source, cost_per_kg_override=None):
    """
    Calculate part cost from a matched material row.

    Parameters
    ----------
    matched_row : pd.Series
        A single row from the materials DataFrame (Metric units).
    part_volume : float
        Part volume in cm³.
    cost_source : str
        One of the cost source options.
    cost_per_kg_override : float or None
        If provided, use this cost instead of CSV.

    Returns
    -------
    dict with keys: cost_per_kg, mass_kg, total_cost, source_label
    """
    density = float(matched_row["Density (g/cm³)"])
    mass_g = part_volume * density
    mass_kg = mass_g / 1000

    if cost_per_kg_override is not None:
        cost_per_kg = cost_per_kg_override
        source_label = "AI Estimated" if "AI" in cost_source else "Live API"
    else:
        cost_per_kg = float(matched_row["Cost per Kg (INR)"])
        source_label = "Database"

    total_cost = mass_kg * cost_per_kg

    return {
        "cost_per_kg": cost_per_kg,
        "mass_kg": mass_kg,
        "total_cost": total_cost,
        "source_label": source_label,
    }
