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
    
    # #150: Material designation
    data_property_entities.append(f"#150=MATERIAL_DESIGNATION('{sanitized_name}',(#145));")
    data_property_entities.append(f"#151=PROPERTY_DEFINITION('material property','material designation',#145);")
    data_property_entities.append(f"#152=DESCRIPTIVE_REPRESENTATION_ITEM('material_name','{sanitized_name}');")
    data_property_entities.append(f"#153=REPRESENTATION('material designation representation',(#152),#6);")
    data_property_entities.append(f"#154=PROPERTY_DEFINITION_REPRESENTATION(#151,#153);")

    entity_id = 160
    for prop_key, prop_val in clean_props.items():
        if prop_key == "Material Name":
            continue
        safe_key = re.sub(r'[^a-zA-Z0-9_]', '_', prop_key).lower()
        safe_val = str(prop_val).replace("'", "''")
        
        p_def = entity_id
        d_item = entity_id + 1
        rep = entity_id + 2
        p_rep = entity_id + 3
        
        data_property_entities.append(f"#{p_def}=PROPERTY_DEFINITION('material property','{prop_key}',#145);")
        data_property_entities.append(f"#{d_item}=DESCRIPTIVE_REPRESENTATION_ITEM('{safe_key}','{safe_val}');")
        data_property_entities.append(f"#{rep}=REPRESENTATION('{safe_key} representation',(#{d_item}),#6);")
        data_property_entities.append(f"#{p_rep}=PROPERTY_DEFINITION_REPRESENTATION(#{p_def},#{rep});")
        
        entity_id += 10

    properties_entities_str = "\n".join(data_property_entities)

    step_content = f"""ISO-10303-21;
HEADER;
FILE_DESCRIPTION(('Material Specimen: {sanitized_name}','{header_desc}','ASTM Tensile Specimen block (10x10x100mm)'),'2;1');
FILE_NAME('{sanitized_id}_specimen.stp','{timestamp}',('AI Material Selector'),('AI Material Selector'),'2.0','AI Material Selector','');
FILE_SCHEMA(('AUTOMOTIVE_DESIGN {{1 0 10303 214 1 1 1 1}}'));
ENDSEC;
DATA;
#1=DIRECTION('',(0.0,0.0,1.0));
#2=VECTOR('',#1,1.0);
#3=DIRECTION('',(1.0,0.0,0.0));
#4=DIRECTION('',(0.0,1.0,0.0));
#5=CARTESIAN_POINT('',(0.0,0.0,0.0));
#6=AXIS2_PLACEMENT_3D('',#5,#1,#3);
#7=PLANE('',#6);
#8=DIRECTION('',(0.0,0.0,-1.0));
#9=VECTOR('',#8,1.0);
#10=DIRECTION('',(-1.0,0.0,0.0));
#11=DIRECTION('',(0.0,1.0,0.0));
#12=CARTESIAN_POINT('',(0.0,0.0,100.0));
#13=AXIS2_PLACEMENT_3D('',#12,#8,#10);
#14=PLANE('',#13);
#15=DIRECTION('',(0.0,1.0,0.0));
#16=VECTOR('',#15,1.0);
#17=DIRECTION('',(1.0,0.0,0.0));
#18=DIRECTION('',(0.0,0.0,-1.0));
#19=CARTESIAN_POINT('',(0.0,0.0,0.0));
#20=AXIS2_PLACEMENT_3D('',#19,#15,#17);
#21=PLANE('',#20);
#22=DIRECTION('',(0.0,-1.0,0.0));
#23=VECTOR('',#22,1.0);
#24=DIRECTION('',(-1.0,0.0,0.0));
#25=DIRECTION('',(0.0,0.0,-1.0));
#26=CARTESIAN_POINT('',(0.0,10.0,0.0));
#27=AXIS2_PLACEMENT_3D('',#26,#22,#24);
#28=PLANE('',#27);
#29=DIRECTION('',(1.0,0.0,0.0));
#30=VECTOR('',#29,1.0);
#31=DIRECTION('',(0.0,-1.0,0.0));
#32=DIRECTION('',(0.0,0.0,-1.0));
#33=CARTESIAN_POINT('',(0.0,0.0,0.0));
#34=AXIS2_PLACEMENT_3D('',#33,#29,#31);
#35=PLANE('',#34);
#36=DIRECTION('',(-1.0,0.0,0.0));
#37=VECTOR('',#36,1.0);
#38=DIRECTION('',(0.0,1.0,0.0));
#39=DIRECTION('',(0.0,0.0,-1.0));
#40=CARTESIAN_POINT('',(10.0,0.0,0.0));
#41=AXIS2_PLACEMENT_3D('',#40,#36,#38);
#42=PLANE('',#41);
#43=CARTESIAN_POINT('',(0.0,0.0,0.0));
#44=CARTESIAN_POINT('',(0.0,0.0,100.0));
#45=VERTEX_POINT('',#43);
#46=VERTEX_POINT('',#44);
#47=CARTESIAN_POINT('',(0.0,10.0,0.0));
#48=CARTESIAN_POINT('',(0.0,10.0,100.0));
#49=VERTEX_POINT('',#47);
#50=VERTEX_POINT('',#48);
#51=CARTESIAN_POINT('',(10.0,10.0,0.0));
#52=CARTESIAN_POINT('',(10.0,10.0,100.0));
#53=VERTEX_POINT('',#51);
#54=VERTEX_POINT('',#52);
#55=CARTESIAN_POINT('',(10.0,0.0,0.0));
#56=CARTESIAN_POINT('',(10.0,0.0,100.0));
#57=VERTEX_POINT('',#55);
#58=VERTEX_POINT('',#56);
#59=DIRECTION('',(0.0,0.0,1.0));
#60=LINE('',#43,#59);
#61=DIRECTION('',(0.0,0.0,1.0));
#62=LINE('',#47,#61);
#63=DIRECTION('',(0.0,0.0,1.0));
#64=LINE('',#51,#63);
#65=DIRECTION('',(0.0,0.0,1.0));
#66=LINE('',#55,#65);
#67=DIRECTION('',(0.0,1.0,0.0));
#68=LINE('',#43,#67);
#69=DIRECTION('',(1.0,0.0,0.0));
#70=LINE('',#47,#69);
#71=DIRECTION('',(0.0,-1.0,0.0));
#72=LINE('',#51,#71);
#73=DIRECTION('',(-1.0,0.0,0.0));
#74=LINE('',#55,#73);
#75=DIRECTION('',(0.0,1.0,0.0));
#76=LINE('',#44,#75);
#77=DIRECTION('',(1.0,0.0,0.0));
#78=LINE('',#48,#77);
#79=DIRECTION('',(0.0,-1.0,0.0));
#80=LINE('',#52,#79);
#81=DIRECTION('',(-1.0,0.0,0.0));
#82=LINE('',#56,#81);
#83=EDGE_CURVE('',#45,#46,#60,.T.);
#84=EDGE_CURVE('',#49,#50,#62,.T.);
#85=EDGE_CURVE('',#53,#54,#64,.T.);
#86=EDGE_CURVE('',#57,#58,#66,.T.);
#87=EDGE_CURVE('',#45,#49,#68,.T.);
#88=EDGE_CURVE('',#49,#53,#70,.T.);
#89=EDGE_CURVE('',#53,#57,#72,.T.);
#90=EDGE_CURVE('',#57,#45,#74,.T.);
#91=EDGE_CURVE('',#46,#50,#76,.T.);
#92=EDGE_CURVE('',#50,#54,#77,.T.);
#93=EDGE_CURVE('',#54,#58,#79,.T.);
#94=EDGE_CURVE('',#58,#46,#82,.T.);
#95=ORIENTED_EDGE('',*,*,#83,.T.);
#96=ORIENTED_EDGE('',*,*,#91,.T.);
#97=ORIENTED_EDGE('',*,*,#84,.F.);
#98=ORIENTED_EDGE('',*,*,#87,.F.);
#99=EDGE_LOOP('',(#95,#96,#97,#98));
#100=FACE_OUTER_BOUND('',#99,.T.);
#101=ADVANCED_FACE('',(#100),#7,.T.);
#102=ORIENTED_EDGE('',*,*,#84,.T.);
#103=ORIENTED_EDGE('',*,*,#92,.T.);
#104=ORIENTED_EDGE('',*,*,#85,.F.);
#105=ORIENTED_EDGE('',*,*,#88,.F.);
#106=EDGE_LOOP('',(#102,#103,#104,#105));
#107=FACE_OUTER_BOUND('',#106,.T.);
#108=ADVANCED_FACE('',(#107),#21,.T.);
#109=ORIENTED_EDGE('',*,*,#85,.T.);
#110=ORIENTED_EDGE('',*,*,#93,.T.);
#111=ORIENTED_EDGE('',*,*,#86,.F.);
#112=ORIENTED_EDGE('',*,*,#89,.F.);
#113=EDGE_LOOP('',(#109,#110,#111,#112));
#114=FACE_OUTER_BOUND('',#113,.T.);
#115=ADVANCED_FACE('',(#114),#28,.T.);
#116=ORIENTED_EDGE('',*,*,#86,.T.);
#117=ORIENTED_EDGE('',*,*,#94,.T.);
#118=ORIENTED_EDGE('',*,*,#83,.F.);
#119=ORIENTED_EDGE('',*,*,#90,.F.);
#120=EDGE_LOOP('',(#116,#117,#118,#119));
#121=FACE_OUTER_BOUND('',#120,.T.);
#122=ADVANCED_FACE('',(#121),#35,.T.);
#123=ORIENTED_EDGE('',*,*,#87,.T.);
#124=ORIENTED_EDGE('',*,*,#88,.T.);
#125=ORIENTED_EDGE('',*,*,#89,.T.);
#126=ORIENTED_EDGE('',*,*,#90,.T.);
#127=EDGE_LOOP('',(#123,#124,#125,#126));
#128=FACE_OUTER_BOUND('',#127,.T.);
#129=ADVANCED_FACE('',(#128),#14,.T.);
#130=ORIENTED_EDGE('',*,*,#91,.F.);
#131=ORIENTED_EDGE('',*,*,#94,.F.);
#132=ORIENTED_EDGE('',*,*,#93,.F.);
#133=ORIENTED_EDGE('',*,*,#92,.F.);
#134=EDGE_LOOP('',(#130,#131,#132,#133));
#135=FACE_OUTER_BOUND('',#134,.T.);
#136=ADVANCED_FACE('',(#135),#42,.T.);
#137=CLOSED_SHELL('',(#101,#108,#115,#122,#129,#136));
#138=MANIFOLD_SOLID_BREP('{sanitized_id}_Specimen',#137);
#139=SHAPE_REPRESENTATION('',(#138),#6);
#140=PRODUCT_DEFINITION_CONTEXT('',#141,'design');
#141=APPLICATION_CONTEXT('automotive design');
#142=PRODUCT_CONTEXT('',#141,'mechanical');
#143=PRODUCT('{sanitized_id}_Part','{sanitized_name}_Part','{sanitized_name} ASTM Specimen with Material Properties',(#142));
#144=PRODUCT_DEFINITION_FORMATION('','',#143);
#145=PRODUCT_DEFINITION('design','Material Specimen for {sanitized_name}',#144,#140);
#146=PRODUCT_DEFINITION_SHAPE('',$,#145);
#147=SHAPE_DEFINITION_REPRESENTATION(#146,#139);
{properties_entities_str}
ENDSEC;
END-ISO-10303-21;
"""
    return step_content

