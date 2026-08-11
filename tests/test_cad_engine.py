import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from modules.cad_engine import CadEngineError, export_bytes, generate_specimen
from modules.cad_export import apply_material_metadata, generate_step_file


def test_generate_cube_specimen_produces_valid_step_and_stl():
    result = generate_specimen("cube", (10.0, 10.0, 10.0), "Aluminum 6061", {"Density (g/cm³)": 2.70})
    assert result.step_text.startswith("ISO-10303-21;")
    assert "PRODUCT" in result.step_text
    assert result.stl_bytes  # non-empty mesh bytes
    assert result.preview_available is True
    assert result.source == "generated"


def test_cube_with_unequal_dimensions_is_rejected():
    with pytest.raises(CadEngineError, match="equal length"):
        generate_specimen("cube", (10.0, 5.0, 10.0), "Steel")


def test_unknown_shape_is_rejected():
    with pytest.raises(CadEngineError, match="Unknown shape"):
        generate_specimen("sphere", (10.0, 10.0, 10.0), "Steel")


def test_negative_dimension_is_rejected():
    with pytest.raises(CadEngineError):
        generate_specimen("cube", (-5.0, -5.0, -5.0), "Steel")


def test_export_bytes_step_matches_step_text():
    result = generate_specimen("cube", (5.0, 5.0, 5.0), "Copper")
    step_bytes = export_bytes(result, fmt="step")
    assert step_bytes.decode("utf-8") == result.step_text


def test_export_bytes_stl_available_for_generated_specimen():
    result = generate_specimen("cube", (5.0, 5.0, 5.0), "Copper")
    stl_bytes = export_bytes(result, fmt="stl")
    assert stl_bytes == result.stl_bytes


def test_material_properties_are_embedded_in_step_output():
    step_text = generate_step_file("Titanium Ti-6Al-4V", {"Density (g/cm³)": 4.43, "Yield Strength (MPa)": 880})
    assert "Titanium Ti-6Al-4V" in step_text
    assert "4.43" in step_text


def test_apply_material_metadata_rejects_non_cad_text():
    with pytest.raises(ValueError, match="No PRODUCT"):
        apply_material_metadata("this is not a step file", "Steel")


def test_apply_material_metadata_works_on_generated_specimen_step():
    base_step = generate_step_file("Placeholder", {})
    tagged = apply_material_metadata(base_step, "Stainless Steel 316", {"Density (g/cm³)": 8.0})
    assert "Stainless Steel 316" in tagged
    assert "MATERIAL_DESIGNATION" in tagged
