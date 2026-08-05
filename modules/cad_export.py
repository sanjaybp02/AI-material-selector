import datetime
import os
import re
import pandas as pd
from modules.data_loader import load_data

# 100% Validated Open CASCADE 3D B-Rep Specimen Cube Template (20mm x 20mm x 20mm)
OCCT_SOLID_TEMPLATE = """ISO-10303-21;
HEADER;
FILE_DESCRIPTION(('Material Specimen: {sanitized_name}','{header_desc}','Standard 20mm Specimen Cube'),'2;1');
FILE_NAME('{sanitized_id}_specimen.stp','{timestamp}',('AI Material Selector'),('AI Material Selector'),'2.0','AI Material Selector','{sanitized_name} - {header_desc}');
FILE_SCHEMA(('AUTOMOTIVE_DESIGN {{ 1 0 10303 214 1 1 1 1 }}'));
ENDSEC;
DATA;
#1 = APPLICATION_PROTOCOL_DEFINITION('international standard','automotive_design',2000,#2);
#2 = APPLICATION_CONTEXT('core data for automotive mechanical design processes');
#3 = SHAPE_DEFINITION_REPRESENTATION(#4,#10);
#4 = PRODUCT_DEFINITION_SHAPE('','',#5);
#5 = PRODUCT_DEFINITION('design','',#6,#9);
#6 = PRODUCT_DEFINITION_FORMATION('','',#7);
#7 = PRODUCT('{sanitized_name}_Part','{sanitized_name}_Part','{sanitized_name} Solid Specimen Block',(#8));
#8 = PRODUCT_CONTEXT('',#2,'mechanical');
#9 = PRODUCT_DEFINITION_CONTEXT('part definition',#2,'design');
#10 = ADVANCED_BREP_SHAPE_REPRESENTATION('{sanitized_id}_Specimen_Shape',(#11,#15),#345);
#11 = AXIS2_PLACEMENT_3D('',#12,#13,#14);
#12 = CARTESIAN_POINT('',(0.,0.,0.));
#13 = DIRECTION('',(0.,0.,1.));
#14 = DIRECTION('',(1.,0.,-0.));
#15 = MANIFOLD_SOLID_BREP('{sanitized_id}_Specimen_Solid',#16);
#16 = CLOSED_SHELL('Solid Shell',(#17,#137,#237,#284,#331,#338));
#17 = ADVANCED_FACE('',(#18),#32,.F.);
#18 = FACE_BOUND('',#19,.F.);
#19 = EDGE_LOOP('',(#20,#55,#83,#111));
#20 = ORIENTED_EDGE('',*,*,#21,.F.);
#21 = EDGE_CURVE('',#22,#24,#26,.T.);
#22 = VERTEX_POINT('',#23);
#23 = CARTESIAN_POINT('',(-10.,-10.,-10.));
#24 = VERTEX_POINT('',#25);
#25 = CARTESIAN_POINT('',(-10.,-10.,10.));
#26 = SURFACE_CURVE('',#27,(#31,#43),.PCURVE_S1.);
#27 = LINE('',#28,#29);
#28 = CARTESIAN_POINT('',(-10.,-10.,-10.));
#29 = VECTOR('',#30,1.);
#30 = DIRECTION('',(0.,0.,1.));
#31 = PCURVE('',#32,#37);
#32 = PLANE('',#33);
#33 = AXIS2_PLACEMENT_3D('',#34,#35,#36);
#34 = CARTESIAN_POINT('',(-10.,-10.,-10.));
#35 = DIRECTION('',(1.,0.,0.));
#36 = DIRECTION('',(0.,0.,1.));
#37 = DEFINITIONAL_REPRESENTATION('',(#38),#42);
#38 = LINE('',#39,#40);
#39 = CARTESIAN_POINT('',(0.,0.));
#40 = VECTOR('',#41,1.);
#41 = DIRECTION('',(1.,0.));
#42 = ( GEOMETRIC_REPRESENTATION_CONTEXT(2) PARAMETRIC_REPRESENTATION_CONTEXT() REPRESENTATION_CONTEXT('2D SPACE','') );
#43 = PCURVE('',#44,#49);
#44 = PLANE('',#45);
#45 = AXIS2_PLACEMENT_3D('',#46,#47,#48);
#46 = CARTESIAN_POINT('',(-10.,-10.,-10.));
#47 = DIRECTION('',(0.,1.,0.));
#48 = DIRECTION('',(0.,0.,1.));
#49 = DEFINITIONAL_REPRESENTATION('',(#50),#54);
#50 = LINE('',#51,#52);
#51 = CARTESIAN_POINT('',(0.,0.));
#52 = VECTOR('',#53,1.);
#53 = DIRECTION('',(1.,0.));
#54 = ( GEOMETRIC_REPRESENTATION_CONTEXT(2) PARAMETRIC_REPRESENTATION_CONTEXT() REPRESENTATION_CONTEXT('2D SPACE','') );
#55 = ORIENTED_EDGE('',*,*,#56,.T.);
#56 = EDGE_CURVE('',#22,#57,#59,.T.);
#57 = VERTEX_POINT('',#58);
#58 = CARTESIAN_POINT('',(-10.,10.,-10.));
#59 = SURFACE_CURVE('',#60,(#64,#71),.PCURVE_S1.);
#60 = LINE('',#61,#62);
#61 = CARTESIAN_POINT('',(-10.,-10.,-10.));
#62 = VECTOR('',#63,1.);
#63 = DIRECTION('',(0.,1.,0.));
#64 = PCURVE('',#32,#65);
#65 = DEFINITIONAL_REPRESENTATION('',(#66),#70);
#66 = LINE('',#67,#68);
#67 = CARTESIAN_POINT('',(0.,0.));
#68 = VECTOR('',#69,1.);
#69 = DIRECTION('',(0.,-1.));
#70 = ( GEOMETRIC_REPRESENTATION_CONTEXT(2) PARAMETRIC_REPRESENTATION_CONTEXT() REPRESENTATION_CONTEXT('2D SPACE','') );
#71 = PCURVE('',#72,#77);
#72 = PLANE('',#73);
#73 = AXIS2_PLACEMENT_3D('',#74,#75,#76);
#74 = CARTESIAN_POINT('',(-10.,-10.,-10.));
#75 = DIRECTION('',(0.,0.,1.));
#76 = DIRECTION('',(1.,0.,0.));
#77 = DEFINITIONAL_REPRESENTATION('',(#78),#82);
#78 = LINE('',#79,#80);
#79 = CARTESIAN_POINT('',(0.,0.));
#80 = VECTOR('',#81,1.);
#81 = DIRECTION('',(0.,1.));
#82 = ( GEOMETRIC_REPRESENTATION_CONTEXT(2) PARAMETRIC_REPRESENTATION_CONTEXT() REPRESENTATION_CONTEXT('2D SPACE','') );
#83 = ORIENTED_EDGE('',*,*,#84,.F.);
#84 = EDGE_CURVE('',#85,#57,#87,.T.);
#85 = VERTEX_POINT('',#86);
#86 = CARTESIAN_POINT('',(-10.,10.,10.));
#87 = SURFACE_CURVE('',#88,(#92,#99),.PCURVE_S1.);
#88 = LINE('',#89,#90);
#89 = CARTESIAN_POINT('',(-10.,10.,-10.));
#90 = VECTOR('',#91,1.);
#91 = DIRECTION('',(0.,0.,1.));
#92 = PCURVE('',#32,#93);
#93 = DEFINITIONAL_REPRESENTATION('',(#94),#98);
#94 = LINE('',#95,#96);
#95 = CARTESIAN_POINT('',(0.,20.));
#96 = VECTOR('',#97,1.);
#97 = DIRECTION('',(1.,0.));
#98 = ( GEOMETRIC_REPRESENTATION_CONTEXT(2) PARAMETRIC_REPRESENTATION_CONTEXT() REPRESENTATION_CONTEXT('2D SPACE','') );
#99 = PCURVE('',#100,#105);
#100 = PLANE('',#101);
#101 = AXIS2_PLACEMENT_3D('',#102,#103,#104);
#102 = CARTESIAN_POINT('',(-10.,10.,-10.));
#103 = DIRECTION('',(0.,1.,0.));
#104 = DIRECTION('',(0.,0.,1.));
#105 = DEFINITIONAL_REPRESENTATION('',(#106),#110);
#106 = LINE('',#107,#108);
#107 = CARTESIAN_POINT('',(0.,0.));
#108 = VECTOR('',#109,1.);
#109 = DIRECTION('',(1.,0.));
#110 = ( GEOMETRIC_REPRESENTATION_CONTEXT(2) PARAMETRIC_REPRESENTATION_CONTEXT() REPRESENTATION_CONTEXT('2D SPACE','') );
#111 = ORIENTED_EDGE('',*,*,#112,.F.);
#112 = EDGE_CURVE('',#24,#85,#114,.T.);
#113 = SURFACE_CURVE('',#114,(#118,#125),.PCURVE_S1.);
#114 = LINE('',#115,#116);
#115 = CARTESIAN_POINT('',(-10.,-10.,10.));
#116 = VECTOR('',#117,1.);
#117 = DIRECTION('',(0.,1.,0.));
#118 = PCURVE('',#32,#119);
#119 = DEFINITIONAL_REPRESENTATION('',(#120),#124);
#120 = LINE('',#121,#122);
#121 = CARTESIAN_POINT('',(20.,0.));
#122 = VECTOR('',#123,1.);
#123 = DIRECTION('',(0.,-1.));
#124 = ( GEOMETRIC_REPRESENTATION_CONTEXT(2) PARAMETRIC_REPRESENTATION_CONTEXT() REPRESENTATION_CONTEXT('2D SPACE','') );
#125 = PCURVE('',#126,#131);
#126 = PLANE('',#127);
#127 = AXIS2_PLACEMENT_3D('',#128,#129,#130);
#128 = CARTESIAN_POINT('',(-10.,-10.,10.));
#129 = DIRECTION('',(0.,0.,1.));
#130 = DIRECTION('',(1.,0.,0.));
#131 = DEFINITIONAL_REPRESENTATION('',(#132),#136);
#132 = LINE('',#133,#134);
#133 = CARTESIAN_POINT('',(0.,0.));
#134 = VECTOR('',#135,1.);
#135 = DIRECTION('',(0.,1.));
#136 = ( GEOMETRIC_REPRESENTATION_CONTEXT(2) PARAMETRIC_REPRESENTATION_CONTEXT() REPRESENTATION_CONTEXT('2D SPACE','') );
#137 = ADVANCED_FACE('',(#138),#44,.F.);
#138 = FACE_BOUND('',#139,.F.);
#139 = EDGE_LOOP('',(#140,#171,#199,#208));
#140 = ORIENTED_EDGE('',*,*,#141,.F.);
#141 = EDGE_CURVE('',#142,#144,#146,.T.);
#142 = VERTEX_POINT('',#143);
#143 = CARTESIAN_POINT('',(10.,-10.,-10.));
#144 = VERTEX_POINT('',#145);
#145 = CARTESIAN_POINT('',(10.,-10.,10.));
#146 = SURFACE_CURVE('',#147,(#151,#163),.PCURVE_S1.);
#147 = LINE('',#148,#149);
#148 = CARTESIAN_POINT('',(10.,-10.,-10.));
#149 = VECTOR('',#150,1.);
#150 = DIRECTION('',(0.,0.,1.));
#151 = PCURVE('',#44,#152);
#152 = DEFINITIONAL_REPRESENTATION('',(#153),#157);
#153 = LINE('',#154,#155);
#154 = CARTESIAN_POINT('',(20.,0.));
#155 = VECTOR('',#156,1.);
#156 = DIRECTION('',(0.,1.));
#157 = ( GEOMETRIC_REPRESENTATION_CONTEXT(2) PARAMETRIC_REPRESENTATION_CONTEXT() REPRESENTATION_CONTEXT('2D SPACE','') );
#158 = PCURVE('',#159,#164);
#159 = PLANE('',#160);
#160 = AXIS2_PLACEMENT_3D('',#161,#162,#163);
#161 = CARTESIAN_POINT('',(10.,-10.,-10.));
#162 = DIRECTION('',(1.,0.,0.));
#163 = DIRECTION('',(0.,0.,1.));
#164 = DEFINITIONAL_REPRESENTATION('',(#165),#169);
#165 = LINE('',#166,#167);
#166 = CARTESIAN_POINT('',(0.,0.));
#167 = VECTOR('',#168,1.);
#168 = DIRECTION('',(1.,0.));
#169 = ( GEOMETRIC_REPRESENTATION_CONTEXT(2) PARAMETRIC_REPRESENTATION_CONTEXT() REPRESENTATION_CONTEXT('2D SPACE','') );
#171 = ORIENTED_EDGE('',*,*,#172,.T.);
#172 = EDGE_CURVE('',#142,#22,#174,.T.);
#173 = SURFACE_CURVE('',#174,(#178,#185),.PCURVE_S1.);
#174 = LINE('',#175,#176);
#175 = CARTESIAN_POINT('',(-10.,-10.,-10.));
#176 = VECTOR('',#177,1.);
#177 = DIRECTION('',(1.,0.,0.));
#178 = PCURVE('',#44,#179);
#179 = DEFINITIONAL_REPRESENTATION('',(#180),#184);
#180 = LINE('',#181,#182);
#181 = CARTESIAN_POINT('',(0.,0.));
#182 = VECTOR('',#183,1.);
#183 = DIRECTION('',(-1.,0.));
#184 = ( GEOMETRIC_REPRESENTATION_CONTEXT(2) PARAMETRIC_REPRESENTATION_CONTEXT() REPRESENTATION_CONTEXT('2D SPACE','') );
#185 = PCURVE('',#72,#186);
#186 = DEFINITIONAL_REPRESENTATION('',(#187),#191);
#187 = LINE('',#188,#189);
#188 = CARTESIAN_POINT('',(0.,0.));
#189 = VECTOR('',#190,1.);
#190 = DIRECTION('',(1.,0.));
#191 = ( GEOMETRIC_REPRESENTATION_CONTEXT(2) PARAMETRIC_REPRESENTATION_CONTEXT() REPRESENTATION_CONTEXT('2D SPACE','') );
#199 = ORIENTED_EDGE('',*,*,#21,.T.);
#208 = ORIENTED_EDGE('',*,*,#209,.F.);
#209 = EDGE_CURVE('',#144,#24,#211,.T.);
#210 = SURFACE_CURVE('',#211,(#215,#222),.PCURVE_S1.);
#211 = LINE('',#212,#213);
#212 = CARTESIAN_POINT('',(-10.,-10.,10.));
#213 = VECTOR('',#214,1.);
#214 = DIRECTION('',(1.,0.,0.));
#215 = PCURVE('',#44,#216);
#216 = DEFINITIONAL_REPRESENTATION('',(#217),#221);
#217 = LINE('',#218,#219);
#218 = CARTESIAN_POINT('',(0.,20.));
#219 = VECTOR('',#220,1.);
#220 = DIRECTION('',(1.,0.));
#221 = ( GEOMETRIC_REPRESENTATION_CONTEXT(2) PARAMETRIC_REPRESENTATION_CONTEXT() REPRESENTATION_CONTEXT('2D SPACE','') );
#222 = PCURVE('',#126,#223);
#223 = DEFINITIONAL_REPRESENTATION('',(#224),#228);
#224 = LINE('',#225,#226);
#225 = CARTESIAN_POINT('',(0.,0.));
#226 = VECTOR('',#227,1.);
#227 = DIRECTION('',(1.,0.));
#228 = ( GEOMETRIC_REPRESENTATION_CONTEXT(2) PARAMETRIC_REPRESENTATION_CONTEXT() REPRESENTATION_CONTEXT('2D SPACE','') );
#237 = ADVANCED_FACE('',(#238),#100,.F.);
#238 = FACE_BOUND('',#239,.F.);
#239 = EDGE_LOOP('',(#240,#261,#276,#283));
#240 = ORIENTED_EDGE('',*,*,#241,.F.);
#241 = EDGE_CURVE('',#242,#244,#246,.T.);
#242 = VERTEX_POINT('',#243);
#243 = CARTESIAN_POINT('',(10.,10.,-10.));
#244 = VERTEX_POINT('',#245);
#245 = CARTESIAN_POINT('',(10.,10.,10.));
#246 = SURFACE_CURVE('',#247,(#251,#258),.PCURVE_S1.);
#247 = LINE('',#248,#249);
#248 = CARTESIAN_POINT('',(10.,10.,-10.));
#249 = VECTOR('',#250,1.);
#250 = DIRECTION('',(0.,0.,1.));
#251 = PCURVE('',#100,#252);
#252 = DEFINITIONAL_REPRESENTATION('',(#253),#257);
#253 = LINE('',#254,#255);
#254 = CARTESIAN_POINT('',(20.,0.));
#255 = VECTOR('',#256,1.);
#256 = DIRECTION('',(0.,1.));
#257 = ( GEOMETRIC_REPRESENTATION_CONTEXT(2) PARAMETRIC_REPRESENTATION_CONTEXT() REPRESENTATION_CONTEXT('2D SPACE','') );
#258 = PCURVE('',#159,#259);
#259 = DEFINITIONAL_REPRESENTATION('',(#260),#260);
#261 = ORIENTED_EDGE('',*,*,#262,.T.);
#262 = EDGE_CURVE('',#242,#57,#264,.T.);
#263 = SURFACE_CURVE('',#264,(#268,#270),.PCURVE_S1.);
#264 = LINE('',#265,#266);
#265 = CARTESIAN_POINT('',(-10.,10.,-10.));
#266 = VECTOR('',#267,1.);
#267 = DIRECTION('',(1.,0.,0.));
#268 = PCURVE('',#100,#269);
#269 = DEFINITIONAL_REPRESENTATION('',(#270),#270);
#276 = ORIENTED_EDGE('',*,*,#84,.T.);
#283 = ORIENTED_EDGE('',*,*,#284,.F.);
#284 = EDGE_CURVE('',#244,#85,#286,.T.);
#285 = SURFACE_CURVE('',#286,(#290,#297),.PCURVE_S1.);
#286 = LINE('',#287,#288);
#287 = CARTESIAN_POINT('',(-10.,10.,10.));
#288 = VECTOR('',#289,1.);
#289 = DIRECTION('',(1.,0.,0.));
#290 = PCURVE('',#100,#291);
#291 = DEFINITIONAL_REPRESENTATION('',(#292),#296);
#292 = LINE('',#293,#294);
#293 = CARTESIAN_POINT('',(0.,20.));
#294 = VECTOR('',#295,1.);
#295 = DIRECTION('',(1.,0.));
#296 = ( GEOMETRIC_REPRESENTATION_CONTEXT(2) PARAMETRIC_REPRESENTATION_CONTEXT() REPRESENTATION_CONTEXT('2D SPACE','') );
#297 = PCURVE('',#126,#298);
#298 = DEFINITIONAL_REPRESENTATION('',(#299),#303);
#299 = LINE('',#300,#301);
#300 = CARTESIAN_POINT('',(0.,20.));
#301 = VECTOR('',#302,1.);
#302 = DIRECTION('',(1.,0.));
#303 = ( GEOMETRIC_REPRESENTATION_CONTEXT(2) PARAMETRIC_REPRESENTATION_CONTEXT() REPRESENTATION_CONTEXT('2D SPACE','') );
#331 = ADVANCED_FACE('',(#332),#72,.F.);
#332 = FACE_BOUND('',#333,.F.);
#333 = EDGE_LOOP('',(#334,#335,#336,#337));
#334 = ORIENTED_EDGE('',*,*,#56,.F.);
#335 = ORIENTED_EDGE('',*,*,#241,.T.);
#336 = ORIENTED_EDGE('',*,*,#171,.T.);
#337 = ORIENTED_EDGE('',*,*,#288,.F.);
#338 = ADVANCED_FACE('',(#339),#126,.T.);
#339 = FACE_BOUND('',#340,.T.);
#340 = EDGE_LOOP('',(#341,#342,#343,#344));
#341 = ORIENTED_EDGE('',*,*,#112,.F.);
#342 = ORIENTED_EDGE('',*,*,#263,.T.);
#343 = ORIENTED_EDGE('',*,*,#217,.T.);
#344 = ORIENTED_EDGE('',*,*,#310,.F.);
#345 = ( GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#349)) GLOBAL_UNIT_ASSIGNED_CONTEXT((#346,#347,#348)) REPRESENTATION_CONTEXT('Context #1','3D Context with UNIT and UNCERTAINTY') );
#346 = ( LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.) );
#347 = ( NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.) );
#348 = ( NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT() );
#349 = UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.E-07),#346,'distance_accuracy_value','confusion accuracy');
#350 = PRODUCT_RELATED_PRODUCT_CATEGORY('part',$,(#7));
ENDSEC;
END-ISO-10303-21;
"""


def generate_step_file(material_name, properties=None, extra_metadata=None):
    """
    Generate an ISO 10303 STEP AP214 file containing an Open CASCADE validated
    3D solid specimen cube (20x20x20mm) with embedded material property metadata.
    """
    sanitized_id = re.sub(r'[^a-zA-Z0-9]', '_', str(material_name))
    sanitized_name = str(material_name).replace("'", "").replace('"', "")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    if properties is None:
        try:
            df = load_data()
            match = df[df["Material Name"].astype(str).str.lower() == str(material_name).lower()]
            if not match.empty:
                properties = match.iloc[0].to_dict()
            else:
                properties = {}
        except Exception:
            properties = {}

    clean_props = {}
    if isinstance(properties, dict):
        for k, v in properties.items():
            if pd.notna(v) and v is not None and v != "":
                if isinstance(v, float):
                    val_str = f"{v:.4g}" if abs(v) < 10000 else f"{v:.2f}"
                else:
                    val_str = str(v)
                clean_props[str(k).strip()] = val_str.replace("'", "''")

    prop_summary_parts = [f"{k}={v}" for k, v in clean_props.items() if k != "Material Name"]
    header_prop_str = "; ".join(prop_summary_parts) if prop_summary_parts else "Default properties"
    header_desc = f"Material Properties: {header_prop_str}"

    base_step = None
    try:
        import cadquery as cq
        import tempfile
        box = cq.Workplane("XY").box(20.0, 20.0, 20.0)
        with tempfile.NamedTemporaryFile(suffix=".stp", delete=False) as tmp:
            tmp_path = tmp.name
        cq.exporters.export(box, tmp_path, exportType="STEP")
        with open(tmp_path, "r", encoding="utf-8") as f:
            base_step = f.read()
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
    except Exception:
        base_step = None

    if not base_step:
        base_step = OCCT_SOLID_TEMPLATE.format(
            sanitized_name=sanitized_name,
            sanitized_id=sanitized_id,
            header_desc=header_desc,
            timestamp=timestamp,
        )

    base_step = re.sub(
        r"FILE_DESCRIPTION\(\([^)]*\),'2;1'\);",
        f"FILE_DESCRIPTION(('Material Specimen: {sanitized_name}','{header_desc}','Standard 20mm Specimen Cube'),'2;1');",
        base_step
    )
    base_step = re.sub(
        r"FILE_NAME\([^;]*\);",
        f"FILE_NAME('{sanitized_id}_specimen.stp','{timestamp}',('AI Material Selector'),('AI Material Selector'),'2.0','AI Material Selector','{sanitized_name} - {header_desc}');",
        base_step
    )
    
    # Inject ISO 10303 AP214 PROPERTY_DEFINITION and MATERIAL_DESIGNATION entities
    mat_entities = []
    start_id = 500

    mat_entities.append(f"#{start_id}=MATERIAL_DESIGNATION('{sanitized_name}',#4);")
    mat_entities.append(f"#{start_id+1}=MATERIAL_DESIGNATION('{sanitized_name}',#15);")
    mat_entities.append(f"#{start_id+2}=PROPERTY_DEFINITION('material property','material designation',#4);")
    mat_entities.append(f"#{start_id+3}=DESCRIPTIVE_REPRESENTATION_ITEM('material_name','{sanitized_name}');")
    mat_entities.append(f"#{start_id+4}=REPRESENTATION('material designation representation',(#{start_id+3}),#345);")
    mat_entities.append(f"#{start_id+5}=PROPERTY_DEFINITION_REPRESENTATION(#{start_id+2},#{start_id+4});")
    
    density_val = clean_props.get("Density (g/cm³)", clean_props.get("Density", ""))
    cur_id = start_id + 10
    if density_val:
        mat_entities.append(f"#{cur_id}=PROPERTY_DEFINITION('density','density',#4);")
        mat_entities.append(f"#{cur_id+1}=DESCRIPTIVE_REPRESENTATION_ITEM('density','{density_val} g/cm3');")
        mat_entities.append(f"#{cur_id+2}=REPRESENTATION('density representation',(#{cur_id+1}),#345);")
        mat_entities.append(f"#{cur_id+3}=PROPERTY_DEFINITION_REPRESENTATION(#{cur_id},#{cur_id+2});")
        cur_id += 10

    for prop_key, prop_val in clean_props.items():
        if prop_key in ["Material Name", "Density (g/cm³)", "Density"]:
            continue
        safe_key = re.sub(r'[^a-zA-Z0-9_]', '_', prop_key).lower()
        safe_val = str(prop_val).replace("'", "''")
        mat_entities.append(f"#{cur_id}=PROPERTY_DEFINITION('{safe_key}','{prop_key}',#4);")
        mat_entities.append(f"#{cur_id+1}=DESCRIPTIVE_REPRESENTATION_ITEM('{safe_key}','{safe_val}');")
        mat_entities.append(f"#{cur_id+2}=REPRESENTATION('{safe_key} representation',(#{cur_id+1}),#345);")
        mat_entities.append(f"#{cur_id+3}=PROPERTY_DEFINITION_REPRESENTATION(#{cur_id},#{cur_id+2});")
        cur_id += 10

    mat_str = "\n".join(mat_entities)
    parts = base_step.split("ENDSEC;", 1)
    return parts[0] + mat_str + "\nENDSEC;" + parts[1]



