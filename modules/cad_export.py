import datetime
import re
import pandas as pd
from modules.data_loader import load_data


def generate_step_file(material_name, properties=None, extra_metadata=None):
    """
    Generate a valid ISO 10303 STEP AP214 / AP242 file representing a standard
    specimen block (10x10x100mm) with all material properties (density, yield strength,
    tensile strength, elastic modulus, thermal conductivity, carbon footprint, cost, standards,
    and any custom uploaded/user properties) embedded into the STEP header and ISO 10303
    DATA section property definitions.
    """
    # Sanitize the name for STEP identifiers (alphanumeric and underscores)
    sanitized_id = re.sub(r'[^a-zA-Z0-9]', '_', str(material_name))
    sanitized_name = str(material_name).replace("'", "").replace('"', "")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    # If properties dictionary is not provided, try to load from materials.csv
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

    # Clean properties dictionary
    clean_props = {}
    if isinstance(properties, dict):
        for k, v in properties.items():
            if pd.notna(v) and v is not None and v != "":
                if isinstance(v, float):
                    val_str = f"{v:.4g}" if abs(v) < 10000 else f"{v:.2f}"
                else:
                    val_str = str(v)
                clean_props[str(k).strip()] = val_str.replace("'", "''")

    # Build header description summary
    prop_summary_parts = []
    for k, v in clean_props.items():
        if k != "Material Name":
            prop_summary_parts.append(f"{k}={v}")
    
    header_prop_str = "; ".join(prop_summary_parts) if prop_summary_parts else "Default mechanical & physical properties"
    header_desc = f"Material Properties: {header_prop_str}"

    # Build STEP DATA section property entities starting after #147
    data_property_entities = []
    
    # Extract density if available for explicit CAD density binding
    density_val = clean_props.get("Density (g/cm³)", clean_props.get("Density", ""))

    # #160+: Material designation & property definitions linked directly to SOLID BODY (#141), SHAPE (#142/#150), PRODUCT (#146), and PRODUCT_DEFINITION (#149) for SpaceClaim / SolidWorks / ANSYS
    data_property_entities.append(f"#160=MATERIAL_DESIGNATION('{sanitized_name}',(#141,#142,#146,#149,#150));")
    data_property_entities.append(f"#161=MATERIAL_PROPERTY('','material designation',#141);")
    data_property_entities.append(f"#162=DESCRIPTIVE_REPRESENTATION_ITEM('material_name','{sanitized_name}');")
    data_property_entities.append(f"#163=REPRESENTATION('material designation representation',(#162),#6);")
    data_property_entities.append(f"#164=PROPERTY_DEFINITION_REPRESENTATION(#161,#163);")

    if density_val:
        data_property_entities.append(f"#165=MATERIAL_PROPERTY('density','density',#141);")
        data_property_entities.append(f"#166=DESCRIPTIVE_REPRESENTATION_ITEM('density','{density_val} g/cm3');")
        data_property_entities.append(f"#167=REPRESENTATION('density representation',(#166),#6);")
        data_property_entities.append(f"#168=PROPERTY_DEFINITION_REPRESENTATION(#165,#167);")

    entity_id = 170
    for prop_key, prop_val in clean_props.items():
        if prop_key in ["Material Name", "Density (g/cm³)", "Density"]:
            continue
        safe_key = re.sub(r'[^a-zA-Z0-9_]', '_', prop_key).lower()
        safe_val = str(prop_val).replace("'", "''")
        
        p_def = entity_id
        d_item = entity_id + 1
        rep = entity_id + 2
        p_rep = entity_id + 3
        
        data_property_entities.append(f"#{p_def}=MATERIAL_PROPERTY('{safe_key}','{prop_key}',#141);")
        data_property_entities.append(f"#{d_item}=DESCRIPTIVE_REPRESENTATION_ITEM('{safe_key}','{safe_val}');")
        data_property_entities.append(f"#{rep}=REPRESENTATION('{safe_key} representation',(#{d_item}),#6);")
        data_property_entities.append(f"#{p_rep}=PROPERTY_DEFINITION_REPRESENTATION(#{p_def},#{rep});")
        
        entity_id += 10

    properties_entities_str = "\n".join(data_property_entities)

    step_content = f"""ISO-10303-21;
HEADER;
FILE_DESCRIPTION(('Material Specimen: {sanitized_name}','{header_desc}','ASTM Tensile Specimen Block (10x10x100mm)'),'2;1');
FILE_NAME('{sanitized_id}_specimen.stp','{timestamp}',('AI Material Selector'),('AI Material Selector'),'2.0','AI Material Selector','{sanitized_name} - {header_desc}');
FILE_SCHEMA(('AUTOMOTIVE_DESIGN {{1 0 10303 214 1 1 1 1}}','AP242_MANAGED_MODEL_BASED_3D_ENGINEERING {{1 0 10303 242 1 1 1 1}}'));
ENDSEC;
DATA;
/* Geometric Representation Context & Units */
#1=(GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#2)) GLOBAL_UNIT_ASSIGNED_CONTEXT((#3,#4,#5)) REPRESENTATION_CONTEXT('3D Context','3D Context with mm units'));
#2=UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.E-05),#3,'distance_accuracy_value','confusion accuracy');
#3=(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.));
#4=(NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.));
#5=(NAMED_UNIT(*) SOLID_ANGLE_UNIT() SI_UNIT($,.STERADIAN.));

/* Axis Placement & Origin */
#6=CARTESIAN_POINT('Origin',(0.0,0.0,0.0));
#7=DIRECTION('Axis',(0.0,0.0,1.0));
#8=DIRECTION('RefDir',(1.0,0.0,0.0));
#9=AXIS2_PLACEMENT_3D('Placement',#6,#7,#8);

/* Block Geometry Vertices (10mm x 10mm x 100mm Solid Specimen Block) */
#10=CARTESIAN_POINT('',(0.0,0.0,0.0));
#11=CARTESIAN_POINT('',(10.0,0.0,0.0));
#12=CARTESIAN_POINT('',(10.0,10.0,0.0));
#13=CARTESIAN_POINT('',(0.0,10.0,0.0));
#14=CARTESIAN_POINT('',(0.0,0.0,100.0));
#15=CARTESIAN_POINT('',(10.0,0.0,100.0));
#16=CARTESIAN_POINT('',(10.0,10.0,100.0));
#17=CARTESIAN_POINT('',(0.0,10.0,100.0));

#20=VERTEX_POINT('',#10);
#21=VERTEX_POINT('',#11);
#22=VERTEX_POINT('',#12);
#23=VERTEX_POINT('',#13);
#24=VERTEX_POINT('',#14);
#25=VERTEX_POINT('',#15);
#26=VERTEX_POINT('',#16);
#27=VERTEX_POINT('',#17);

#30=DIRECTION('',(1.0,0.0,0.0));
#31=DIRECTION('',(0.0,1.0,0.0));
#32=DIRECTION('',(0.0,0.0,1.0));
#33=DIRECTION('',(-1.0,0.0,0.0));
#34=DIRECTION('',(0.0,-1.0,0.0));
#35=DIRECTION('',(0.0,0.0,-1.0));

#40=LINE('',#10,#30);
#41=LINE('',#11,#31);
#42=LINE('',#12,#33);
#43=LINE('',#13,#34);
#44=LINE('',#14,#30);
#45=LINE('',#15,#31);
#46=LINE('',#16,#33);
#47=LINE('',#17,#34);
#48=LINE('',#10,#32);
#49=LINE('',#11,#32);
#50=LINE('',#12,#32);
#51=LINE('',#13,#32);

#60=EDGE_CURVE('',#20,#21,#40,.T.);
#61=EDGE_CURVE('',#21,#22,#41,.T.);
#62=EDGE_CURVE('',#22,#23,#42,.T.);
#63=EDGE_CURVE('',#23,#20,#43,.T.);
#64=EDGE_CURVE('',#24,#25,#44,.T.);
#65=EDGE_CURVE('',#25,#26,#45,.T.);
#66=EDGE_CURVE('',#26,#27,#46,.T.);
#67=EDGE_CURVE('',#27,#24,#47,.T.);
#68=EDGE_CURVE('',#20,#24,#48,.T.);
#69=EDGE_CURVE('',#21,#25,#49,.T.);
#70=EDGE_CURVE('',#22,#26,#50,.T.);
#71=EDGE_CURVE('',#23,#27,#51,.T.);

#80=ORIENTED_EDGE('',*,*,#60,.T.);
#81=ORIENTED_EDGE('',*,*,#61,.T.);
#82=ORIENTED_EDGE('',*,*,#62,.T.);
#83=ORIENTED_EDGE('',*,*,#63,.T.);
#84=EDGE_LOOP('',(#80,#81,#82,#83));
#85=FACE_OUTER_BOUND('',#84,.T.);
#86=AXIS2_PLACEMENT_3D('',#10,#35,#30);
#87=PLANE('',#86);
#88=ADVANCED_FACE('',(#85),#87,.F.);

#90=ORIENTED_EDGE('',*,*,#64,.T.);
#91=ORIENTED_EDGE('',*,*,#65,.T.);
#92=ORIENTED_EDGE('',*,*,#66,.T.);
#93=ORIENTED_EDGE('',*,*,#67,.T.);
#94=EDGE_LOOP('',(#90,#91,#92,#93));
#95=FACE_OUTER_BOUND('',#94,.T.);
#96=AXIS2_PLACEMENT_3D('',#14,#32,#30);
#97=PLANE('',#96);
#98=ADVANCED_FACE('',(#95),#97,.T.);

#100=ORIENTED_EDGE('',*,*,#60,.T.);
#101=ORIENTED_EDGE('',*,*,#69,.T.);
#102=ORIENTED_EDGE('',*,*,#64,.F.);
#103=ORIENTED_EDGE('',*,*,#68,.F.);
#104=EDGE_LOOP('',(#100,#101,#102,#103));
#105=FACE_OUTER_BOUND('',#104,.T.);
#106=AXIS2_PLACEMENT_3D('',#10,#34,#30);
#107=PLANE('',#106);
#108=ADVANCED_FACE('',(#105),#107,.T.);

#110=ORIENTED_EDGE('',*,*,#61,.T.);
#111=ORIENTED_EDGE('',*,*,#70,.T.);
#112=ORIENTED_EDGE('',*,*,#65,.F.);
#113=ORIENTED_EDGE('',*,*,#69,.F.);
#114=EDGE_LOOP('',(#110,#111,#112,#113));
#115=FACE_OUTER_BOUND('',#114,.T.);
#116=AXIS2_PLACEMENT_3D('',#11,#30,#31);
#117=PLANE('',#116);
#118=ADVANCED_FACE('',(#115),#117,.T.);

#120=ORIENTED_EDGE('',*,*,#62,.T.);
#121=ORIENTED_EDGE('',*,*,#71,.T.);
#122=ORIENTED_EDGE('',*,*,#66,.F.);
#123=ORIENTED_EDGE('',*,*,#70,.F.);
#124=EDGE_LOOP('',(#120,#121,#122,#123));
#125=FACE_OUTER_BOUND('',#124,.T.);
#126=AXIS2_PLACEMENT_3D('',#12,#31,#33);
#127=PLANE('',#126);
#128=ADVANCED_FACE('',(#125),#127,.T.);

#130=ORIENTED_EDGE('',*,*,#63,.T.);
#131=ORIENTED_EDGE('',*,*,#68,.T.);
#132=ORIENTED_EDGE('',*,*,#67,.F.);
#133=ORIENTED_EDGE('',*,*,#71,.F.);
#134=EDGE_LOOP('',(#130,#131,#132,#133));
#135=FACE_OUTER_BOUND('',#134,.T.);
#136=AXIS2_PLACEMENT_3D('',#13,#33,#34);
#137=PLANE('',#136);
#138=ADVANCED_FACE('',(#135),#137,.T.);

/* Solid Body & Assembly Topology */
#140=CLOSED_SHELL('Solid Shell',(#88,#98,#108,#118,#128,#138));
#141=MANIFOLD_SOLID_BREP('{sanitized_id}_Specimen_Solid',#140);
#142=ADVANCED_BREP_SHAPE_REPRESENTATION('{sanitized_id}_Specimen_Shape',(#141,#9),#1);

#143=APPLICATION_CONTEXT('automotive design');
#144=APPLICATION_PROTOCOL_DEFINITION('international standard','automotive_design',2000,#143);
#145=PRODUCT_CONTEXT('mechanical',#143,'mechanical');
#146=PRODUCT('{sanitized_id}_Part','{sanitized_name}_Part','{sanitized_name} Solid Specimen Block',(#145));
#147=PRODUCT_DEFINITION_FORMATION('1','1',#146);
#148=PRODUCT_DEFINITION_CONTEXT('part definition',#143,'design');
#149=PRODUCT_DEFINITION('design','{sanitized_name} Specimen',#147,#148);
#150=PRODUCT_DEFINITION_SHAPE('Shape For Product',$,#149);
#151=SHAPE_DEFINITION_REPRESENTATION(#150,#142);

{properties_entities_str}
ENDSEC;
END-ISO-10303-21;
"""
    return step_content

