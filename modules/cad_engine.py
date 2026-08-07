"""
CAD Studio engine — the single server-side entry point for every CAD Studio
operation: generating parametric specimens, ingesting user-uploaded STEP
files, applying material properties, tessellating a preview mesh, and
exporting to a requested format. Every caller (generate or upload) goes
through the same CadResult contract, regardless of where the geometry
originated.

This module is dependency-free by design: it works in any deployment
environment with no geometry kernel installed. A cadquery-backed engine can
later implement the same CadResult contract to add real arbitrary-STEP
parsing, IGES support, and full 3D preview of uploaded files, without
changing any caller in app.py — see the module docstring in cad_export.py
for the size/scope tradeoffs behind that decision.
"""

import re
from dataclasses import dataclass
from typing import Optional, Tuple

from modules.cad_export import apply_material_metadata, generate_step_file

MAX_UPLOAD_BYTES = 15 * 1024 * 1024  # 15MB — generous headroom for a single-part STEP file
ALLOWED_UPLOAD_EXTENSIONS = (".stp", ".step")
VALID_SHAPES = ("cube", "box", "plate")
DIM_MIN_MM = 1.0
DIM_MAX_MM = 500.0


class CadEngineError(ValueError):
    """User-facing error: the CAD Studio UI should show str(e) directly
    rather than a stack trace."""


@dataclass
class CadResult:
    step_text: Optional[str] = None
    stl_bytes: Optional[bytes] = None
    preview_available: bool = False
    preview_note: str = ""
    source: str = ""  # "generated" | "uploaded"
    filename_stub: str = "specimen"


def cadquery_available() -> bool:
    """Whether the optional cadquery geometry engine is importable in this
    environment. Used by the UI to proactively label features that need it
    (e.g. non-uniform box dimensions) rather than let the user hit an error
    after filling in a form."""
    try:
        import cadquery  # noqa: F401
        return True
    except Exception:
        return False


def _slug(value) -> str:
    return re.sub(r"[^a-zA-Z0-9]", "_", str(value)).strip("_") or "model"


def _validate_dim(value, label) -> float:
    try:
        value = float(value)
    except (TypeError, ValueError):
        raise CadEngineError(f"{label} must be a number.")
    if not (DIM_MIN_MM <= value <= DIM_MAX_MM):
        raise CadEngineError(
            f"{label} must be between {DIM_MIN_MM:g}mm and {DIM_MAX_MM:g}mm "
            f"(got {value:g}mm)."
        )
    return value


def _mesh_box_stl(length: float, width: float, height: float, name: str = "specimen") -> bytes:
    """Hand-rolled ASCII STL for an axis-aligned box — used only to feed the
    in-browser preview viewer, not for manufacturing. No geometry library
    required. Triangle winding is best-effort (the viewer renders both
    sides), since the exported STEP file is the dimensionally authoritative
    output, not this mesh."""
    hx, hy, hz = length / 2.0, width / 2.0, height / 2.0
    v = {
        0: (-hx, -hy, -hz), 1: (hx, -hy, -hz), 2: (hx, hy, -hz), 3: (-hx, hy, -hz),
        4: (-hx, -hy, hz), 5: (hx, -hy, hz), 6: (hx, hy, hz), 7: (-hx, hy, hz),
    }
    faces = [
        ((0, 0, -1), (0, 1, 2), (0, 2, 3)),  # bottom
        ((0, 0, 1), (4, 6, 5), (4, 7, 6)),   # top
        ((0, -1, 0), (0, 1, 5), (0, 5, 4)),  # front
        ((0, 1, 0), (2, 3, 7), (2, 7, 6)),   # back
        ((-1, 0, 0), (0, 3, 7), (0, 7, 4)),  # left
        ((1, 0, 0), (1, 2, 6), (1, 6, 5)),   # right
    ]
    safe_name = _slug(name)
    lines = [f"solid {safe_name}"]
    for normal, tri1, tri2 in faces:
        for tri in (tri1, tri2):
            lines.append(f"  facet normal {normal[0]:g} {normal[1]:g} {normal[2]:g}")
            lines.append("    outer loop")
            for idx in tri:
                x, y, z = v[idx]
                lines.append(f"      vertex {x:g} {y:g} {z:g}")
            lines.append("    endloop")
            lines.append("  endfacet")
    lines.append(f"endsolid {safe_name}")
    return ("\n".join(lines) + "\n").encode("ascii")


def load_uploaded_step(file_bytes: bytes, filename: str) -> str:
    """Validate and decode a user-uploaded STEP file. Raises CadEngineError
    with a UI-friendly message for anything that isn't a plausible STEP
    file, instead of letting a cryptic exception reach the user."""
    if not str(filename).lower().endswith(ALLOWED_UPLOAD_EXTENSIONS):
        raise CadEngineError(
            f"Unsupported file type '{filename}'. Upload a STEP file "
            f"(.stp or .step) — applying material properties needs real "
            f"ISO-10303 CAD data, not a mesh format."
        )
    if not file_bytes:
        raise CadEngineError("Uploaded file is empty.")
    if len(file_bytes) > MAX_UPLOAD_BYTES:
        raise CadEngineError(
            f"File is {len(file_bytes) / 1e6:.1f}MB, which exceeds the "
            f"{MAX_UPLOAD_BYTES // (1024 * 1024)}MB limit for this environment."
        )
    try:
        text = file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        try:
            text = file_bytes.decode("latin-1")
        except UnicodeDecodeError:
            raise CadEngineError(
                "Couldn't decode this file as text — it may be a binary CAD "
                "format rather than an ASCII STEP file."
            )
    stripped = text.lstrip("﻿ \t\r\n")
    if not stripped.upper().startswith("ISO-10303-21"):
        raise CadEngineError(
            "This doesn't look like a valid STEP file (missing the "
            "ISO-10303-21 header) — it may be corrupted or a different "
            "format renamed to .stp."
        )
    if "ENDSEC;" not in text.upper() or "DATA;" not in text.upper():
        raise CadEngineError(
            "This STEP file is missing required sections (DATA/ENDSEC) and "
            "appears to be incomplete or corrupted."
        )
    return text


def generate_specimen(
    shape: str,
    dimensions: Tuple[float, float, float],
    material_name: str,
    properties: Optional[dict] = None,
) -> CadResult:
    """
    shape: 'cube' (equal dimensions, always available) | 'box' / 'plate'
           (independent length/width/height, needs the optional cadquery
           engine — raises CadEngineError with a clear explanation if it
           isn't installed).
    dimensions: (length, width, height) in mm.
    """
    if shape not in VALID_SHAPES:
        raise CadEngineError(f"Unknown shape '{shape}'.")

    labels = ("Length", "Width", "Height")
    length, width, height = (_validate_dim(d, label) for d, label in zip(dimensions, labels))

    if shape == "cube" and not (abs(length - width) < 1e-6 and abs(length - height) < 1e-6):
        raise CadEngineError(
            "A cube requires equal length, width, and height. Choose 'Box' "
            "for independent proportions."
        )

    try:
        step_text = generate_step_file(material_name, properties, dimensions=(length, width, height))
    except ValueError as e:
        raise CadEngineError(str(e)) from e

    stl_bytes = _mesh_box_stl(length, width, height, name=_slug(material_name))
    stub = f"{_slug(material_name)}_{length:g}x{width:g}x{height:g}mm"

    return CadResult(
        step_text=step_text,
        stl_bytes=stl_bytes,
        preview_available=True,
        source="generated",
        filename_stub=stub,
    )


def apply_properties_to_upload(
    file_bytes: bytes,
    filename: str,
    material_name: str,
    properties: Optional[dict] = None,
) -> CadResult:
    """Ingest a user-uploaded STEP file and embed the given material's
    properties into it, through the same generic injector used for
    generated specimens. No live 3D preview is available for uploads in
    this dependency-free engine (there's no geometry kernel to tessellate
    arbitrary BREP into a mesh) — `preview_note` explains that to the UI so
    it can show a clear message instead of a blank viewer; the STEP
    download itself is fully valid regardless."""
    step_text = load_uploaded_step(file_bytes, filename)
    try:
        tagged = apply_material_metadata(step_text, material_name, properties)
    except ValueError as e:
        raise CadEngineError(str(e)) from e

    stub = _slug(str(filename).rsplit(".", 1)[0]) + "_with_material"

    return CadResult(
        step_text=tagged,
        stl_bytes=None,
        preview_available=False,
        preview_note=(
            "3D preview isn't available for uploaded files in this "
            "environment yet — the download below is still fully valid and "
            "will open correctly with the applied material properties in "
            "SolidWorks, FreeCAD, ANSYS, and similar tools."
        ),
        source="uploaded",
        filename_stub=stub,
    )


def export_bytes(result: CadResult, fmt: str = "step") -> bytes:
    fmt = fmt.lower().lstrip(".")
    if fmt in ("step", "stp"):
        if not result.step_text:
            raise CadEngineError("No STEP data available to export.")
        return result.step_text.encode("utf-8")
    if fmt == "stl":
        if not result.stl_bytes:
            raise CadEngineError(
                "STL export isn't available for this model in the current "
                "environment (uploaded STEP files need the optional "
                "cadquery engine to convert to mesh formats)."
            )
        return result.stl_bytes
    raise CadEngineError(f"Unsupported export format '{fmt}'.")
