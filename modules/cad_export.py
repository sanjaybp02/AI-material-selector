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
#1 = APPLICATION_PROTOCOL_DEFINITION('international standard',
  'automotive_design',2000,#2);
#2 = APPLICATION_CONTEXT(
  'core data for automotive mechanical design processes');
#3 = SHAPE_DEFINITION_REPRESENTATION(#4,#10);
#4 = PRODUCT_DEFINITION_SHAPE('','',#5);
#5 = PRODUCT_DEFINITION('design','',#6,#9);
#6 = PRODUCT_DEFINITION_FORMATION('','',#7);
#7 = PRODUCT('Open CASCADE STEP translator 7.9 1',
  'Open CASCADE STEP translator 7.9 1','',(#8));
#8 = PRODUCT_CONTEXT('',#2,'mechanical');
#9 = PRODUCT_DEFINITION_CONTEXT('part definition',#2,'design');
#10 = ADVANCED_BREP_SHAPE_REPRESENTATION('',(#11,#15),#345);
#11 = AXIS2_PLACEMENT_3D('',#12,#13,#14);
#12 = CARTESIAN_POINT('',(0.,0.,0.));
#13 = DIRECTION('',(0.,0.,1.));
#14 = DIRECTION('',(1.,0.,-0.));
#15 = MANIFOLD_SOLID_BREP('',#16);
#16 = CLOSED_SHELL('',(#17,#137,#237,#284,#331,#338));
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
#42 = ( GEOMETRIC_REPRESENTATION_CONTEXT(2) 
PARAMETRIC_REPRESENTATION_CONTEXT() REPRESENTATION_CONTEXT('2D SPACE',''
  ) );
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
#54 = ( GEOMETRIC_REPRESENTATION_CONTEXT(2) 
PARAMETRIC_REPRESENTATION_CONTEXT() REPRESENTATION_CONTEXT('2D SPACE',''
  ) );
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
#70 = ( GEOMETRIC_REPRESENTATION_CONTEXT(2) 
PARAMETRIC_REPRESENTATION_CONTEXT() REPRESENTATION_CONTEXT('2D SPACE',''
  ) );
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
#82 = ( GEOMETRIC_REPRESENTATION_CONTEXT(2) 
PARAMETRIC_REPRESENTATION_CONTEXT() REPRESENTATION_CONTEXT('2D SPACE',''
  ) );
#83 = ORIENTED_EDGE('',*,*,#84,.T.);
#84 = EDGE_CURVE('',#57,#85,#87,.T.);
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
#95 = CARTESIAN_POINT('',(0.,-20.));
#96 = VECTOR('',#97,1.);
#97 = DIRECTION('',(1.,0.));
#98 = ( GEOMETRIC_REPRESENTATION_CONTEXT(2) 
PARAMETRIC_REPRESENTATION_CONTEXT() REPRESENTATION_CONTEXT('2D SPACE',''
  ) );
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
#110 = ( GEOMETRIC_REPRESENTATION_CONTEXT(2) 
PARAMETRIC_REPRESENTATION_CONTEXT() REPRESENTATION_CONTEXT('2D SPACE',''
  ) );
#111 = ORIENTED_EDGE('',*,*,#112,.F.);
#112 = EDGE_CURVE('',#24,#85,#113,.T.);
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
#124 = ( GEOMETRIC_REPRESENTATION_CONTEXT(2) 
PARAMETRIC_REPRESENTATION_CONTEXT() REPRESENTATION_CONTEXT('2D SPACE',''
  ) );
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
#136 = ( GEOMETRIC_REPRESENTATION_CONTEXT(2) 
PARAMETRIC_REPRESENTATION_CONTEXT() REPRESENTATION_CONTEXT('2D SPACE',''
  ) );
#137 = ADVANCED_FACE('',(#138),#152,.T.);
#138 = FACE_BOUND('',#139,.T.);
#139 = EDGE_LOOP('',(#140,#170,#193,#216));
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
#151 = PCURVE('',#152,#157);
#152 = PLANE('',#153);
#153 = AXIS2_PLACEMENT_3D('',#154,#155,#156);
#154 = CARTESIAN_POINT('',(10.,-10.,-10.));
#155 = DIRECTION('',(1.,0.,0.));
#156 = DIRECTION('',(0.,0.,1.));
#157 = DEFINITIONAL_REPRESENTATION('',(#158),#162);
#158 = LINE('',#159,#160);
#159 = CARTESIAN_POINT('',(0.,0.));
#160 = VECTOR('',#161,1.);
#161 = DIRECTION('',(1.,0.));
#162 = ( GEOMETRIC_REPRESENTATION_CONTEXT(2) 
PARAMETRIC_REPRESENTATION_CONTEXT() REPRESENTATION_CONTEXT('2D SPACE',''
  ) );
#163 = PCURVE('',#44,#164);
#164 = DEFINITIONAL_REPRESENTATION('',(#165),#169);
#165 = LINE('',#166,#167);
#166 = CARTESIAN_POINT('',(0.,20.));
#167 = VECTOR('',#168,1.);
#168 = DIRECTION('',(1.,0.));
#169 = ( GEOMETRIC_REPRESENTATION_CONTEXT(2) 
PARAMETRIC_REPRESENTATION_CONTEXT() REPRESENTATION_CONTEXT('2D SPACE',''
  ) );
#170 = ORIENTED_EDGE('',*,*,#171,.T.);
#171 = EDGE_CURVE('',#142,#172,#174,.T.);
#172 = VERTEX_POINT('',#173);
#173 = CARTESIAN_POINT('',(10.,10.,-10.));
#174 = SURFACE_CURVE('',#175,(#179,#186),.PCURVE_S1.);
#175 = LINE('',#176,#177);
#176 = CARTESIAN_POINT('',(10.,-10.,-10.));
#177 = VECTOR('',#178,1.);
#178 = DIRECTION('',(0.,1.,0.));
#179 = PCURVE('',#152,#180);
#180 = DEFINITIONAL_REPRESENTATION('',(#181),#185);
#181 = LINE('',#182,#183);
#182 = CARTESIAN_POINT('',(0.,0.));
#183 = VECTOR('',#184,1.);
#184 = DIRECTION('',(0.,-1.));
#185 = ( GEOMETRIC_REPRESENTATION_CONTEXT(2) 
PARAMETRIC_REPRESENTATION_CONTEXT() REPRESENTATION_CONTEXT('2D SPACE',''
  ) );
#186 = PCURVE('',#72,#187);
#187 = DEFINITIONAL_REPRESENTATION('',(#188),#192);
#188 = LINE('',#189,#190);
#189 = CARTESIAN_POINT('',(20.,0.));
#190 = VECTOR('',#191,1.);
#191 = DIRECTION('',(0.,1.));
#192 = ( GEOMETRIC_REPRESENTATION_CONTEXT(2) 
PARAMETRIC_REPRESENTATION_CONTEXT() REPRESENTATION_CONTEXT('2D SPACE',''
  ) );
#193 = ORIENTED_EDGE('',*,*,#194,.T.);
#194 = EDGE_CURVE('',#172,#195,#197,.T.);
#195 = VERTEX_POINT('',#196);
#196 = CARTESIAN_POINT('',(10.,10.,10.));
#197 = SURFACE_CURVE('',#198,(#202,#209),.PCURVE_S1.);
#198 = LINE('',#199,#200);
#199 = CARTESIAN_POINT('',(10.,10.,-10.));
#200 = VECTOR('',#201,1.);
#201 = DIRECTION('',(0.,0.,1.));
#202 = PCURVE('',#152,#203);
#203 = DEFINITIONAL_REPRESENTATION('',(#204),#208);
#204 = LINE('',#205,#206);
#205 = CARTESIAN_POINT('',(0.,-20.));
#206 = VECTOR('',#207,1.);
#207 = DIRECTION('',(1.,0.));
#208 = ( GEOMETRIC_REPRESENTATION_CONTEXT(2) 
PARAMETRIC_REPRESENTATION_CONTEXT() REPRESENTATION_CONTEXT('2D SPACE',''
  ) );
#209 = PCURVE('',#100,#210);
#210 = DEFINITIONAL_REPRESENTATION('',(#211),#215);
#211 = LINE('',#212,#213);
#212 = CARTESIAN_POINT('',(0.,20.));
#213 = VECTOR('',#214,1.);
#214 = DIRECTION('',(1.,0.));
#215 = ( GEOMETRIC_REPRESENTATION_CONTEXT(2) 
PARAMETRIC_REPRESENTATION_CONTEXT() REPRESENTATION_CONTEXT('2D SPACE',''
  ) );
#216 = ORIENTED_EDGE('',*,*,#217,.F.);
#217 = EDGE_CURVE('',#144,#195,#218,.T.);
#218 = SURFACE_CURVE('',#219,(#223,#230),.PCURVE_S1.);
#219 = LINE('',#220,#221);
#220 = CARTESIAN_POINT('',(10.,-10.,10.));
#221 = VECTOR('',#222,1.);
#222 = DIRECTION('',(0.,1.,0.));
#223 = PCURVE('',#152,#224);
#224 = DEFINITIONAL_REPRESENTATION('',(#225),#229);
#225 = LINE('',#226,#227);
#226 = CARTESIAN_POINT('',(20.,0.));
#227 = VECTOR('',#228,1.);
#228 = DIRECTION('',(0.,-1.));
#229 = ( GEOMETRIC_REPRESENTATION_CONTEXT(2) 
PARAMETRIC_REPRESENTATION_CONTEXT() REPRESENTATION_CONTEXT('2D SPACE',''
  ) );
#230 = PCURVE('',#126,#231);
#231 = DEFINITIONAL_REPRESENTATION('',(#232),#236);
#232 = LINE('',#233,#234);
#233 = CARTESIAN_POINT('',(20.,0.));
#234 = VECTOR('',#235,1.);
#235 = DIRECTION('',(0.,1.));
#236 = ( GEOMETRIC_REPRESENTATION_CONTEXT(2) 
PARAMETRIC_REPRESENTATION_CONTEXT() REPRESENTATION_CONTEXT('2D SPACE',''
  ) );
#237 = ADVANCED_FACE('',(#238),#44,.F.);
#238 = FACE_BOUND('',#239,.F.);
#239 = EDGE_LOOP('',(#240,#261,#262,#283));
#240 = ORIENTED_EDGE('',*,*,#241,.F.);
#241 = EDGE_CURVE('',#22,#142,#242,.T.);
#242 = SURFACE_CURVE('',#243,(#247,#254),.PCURVE_S1.);
#243 = LINE('',#244,#245);
#244 = CARTESIAN_POINT('',(-10.,-10.,-10.));
#245 = VECTOR('',#246,1.);
#246 = DIRECTION('',(1.,0.,0.));
#247 = PCURVE('',#44,#248);
#248 = DEFINITIONAL_REPRESENTATION('',(#249),#253);
#249 = LINE('',#250,#251);
#250 = CARTESIAN_POINT('',(0.,0.));
#251 = VECTOR('',#252,1.);
#252 = DIRECTION('',(0.,1.));
#253 = ( GEOMETRIC_REPRESENTATION_CONTEXT(2) 
PARAMETRIC_REPRESENTATION_CONTEXT() REPRESENTATION_CONTEXT('2D SPACE',''
  ) );
#254 = PCURVE('',#72,#255);
#255 = DEFINITIONAL_REPRESENTATION('',(#256),#260);
#256 = LINE('',#257,#258);
#257 = CARTESIAN_POINT('',(0.,0.));
#258 = VECTOR('',#259,1.);
#259 = DIRECTION('',(1.,0.));
#260 = ( GEOMETRIC_REPRESENTATION_CONTEXT(2) 
PARAMETRIC_REPRESENTATION_CONTEXT() REPRESENTATION_CONTEXT('2D SPACE',''
  ) );
#261 = ORIENTED_EDGE('',*,*,#21,.T.);
#262 = ORIENTED_EDGE('',*,*,#263,.T.);
#263 = EDGE_CURVE('',#24,#144,#264,.T.);
#264 = SURFACE_CURVE('',#265,(#269,#276),.PCURVE_S1.);
#265 = LINE('',#266,#267);
#266 = CARTESIAN_POINT('',(-10.,-10.,10.));
#267 = VECTOR('',#268,1.);
#268 = DIRECTION('',(1.,0.,0.));
#269 = PCURVE('',#44,#270);
#270 = DEFINITIONAL_REPRESENTATION('',(#271),#275);
#271 = LINE('',#272,#273);
#272 = CARTESIAN_POINT('',(20.,0.));
#273 = VECTOR('',#274,1.);
#274 = DIRECTION('',(0.,1.));
#275 = ( GEOMETRIC_REPRESENTATION_CONTEXT(2) 
PARAMETRIC_REPRESENTATION_CONTEXT() REPRESENTATION_CONTEXT('2D SPACE',''
  ) );
#276 = PCURVE('',#126,#277);
#277 = DEFINITIONAL_REPRESENTATION('',(#278),#282);
#278 = LINE('',#279,#280);
#279 = CARTESIAN_POINT('',(0.,0.));
#280 = VECTOR('',#281,1.);
#281 = DIRECTION('',(1.,0.));
#282 = ( GEOMETRIC_REPRESENTATION_CONTEXT(2) 
PARAMETRIC_REPRESENTATION_CONTEXT() REPRESENTATION_CONTEXT('2D SPACE',''
  ) );
#283 = ORIENTED_EDGE('',*,*,#141,.F.);
#284 = ADVANCED_FACE('',(#285),#100,.T.);
#285 = FACE_BOUND('',#286,.T.);
#286 = EDGE_LOOP('',(#287,#308,#309,#330));
#287 = ORIENTED_EDGE('',*,*,#288,.F.);
#288 = EDGE_CURVE('',#57,#172,#289,.T.);
#289 = SURFACE_CURVE('',#290,(#294,#301),.PCURVE_S1.);
#290 = LINE('',#291,#292);
#291 = CARTESIAN_POINT('',(-10.,10.,-10.));
#292 = VECTOR('',#293,1.);
#293 = DIRECTION('',(1.,0.,0.));
#294 = PCURVE('',#100,#295);
#295 = DEFINITIONAL_REPRESENTATION('',(#296),#300);
#296 = LINE('',#297,#298);
#297 = CARTESIAN_POINT('',(0.,0.));
#298 = VECTOR('',#299,1.);
#299 = DIRECTION('',(0.,1.));
#300 = ( GEOMETRIC_REPRESENTATION_CONTEXT(2) 
PARAMETRIC_REPRESENTATION_CONTEXT() REPRESENTATION_CONTEXT('2D SPACE',''
  ) );
#301 = PCURVE('',#72,#302);
#302 = DEFINITIONAL_REPRESENTATION('',(#303),#307);
#303 = LINE('',#304,#305);
#304 = CARTESIAN_POINT('',(0.,20.));
#305 = VECTOR('',#306,1.);
#306 = DIRECTION('',(1.,0.));
#307 = ( GEOMETRIC_REPRESENTATION_CONTEXT(2) 
PARAMETRIC_REPRESENTATION_CONTEXT() REPRESENTATION_CONTEXT('2D SPACE',''
  ) );
#308 = ORIENTED_EDGE('',*,*,#84,.T.);
#309 = ORIENTED_EDGE('',*,*,#310,.T.);
#310 = EDGE_CURVE('',#85,#195,#311,.T.);
#311 = SURFACE_CURVE('',#312,(#316,#323),.PCURVE_S1.);
#312 = LINE('',#313,#314);
#313 = CARTESIAN_POINT('',(-10.,10.,10.));
#314 = VECTOR('',#315,1.);
#315 = DIRECTION('',(1.,0.,0.));
#316 = PCURVE('',#100,#317);
#317 = DEFINITIONAL_REPRESENTATION('',(#318),#322);
#318 = LINE('',#319,#320);
#319 = CARTESIAN_POINT('',(20.,0.));
#320 = VECTOR('',#321,1.);
#321 = DIRECTION('',(0.,1.));
#322 = ( GEOMETRIC_REPRESENTATION_CONTEXT(2) 
PARAMETRIC_REPRESENTATION_CONTEXT() REPRESENTATION_CONTEXT('2D SPACE',''
  ) );
#323 = PCURVE('',#126,#324);
#324 = DEFINITIONAL_REPRESENTATION('',(#325),#329);
#325 = LINE('',#326,#327);
#326 = CARTESIAN_POINT('',(0.,20.));
#327 = VECTOR('',#328,1.);
#328 = DIRECTION('',(1.,0.));
#329 = ( GEOMETRIC_REPRESENTATION_CONTEXT(2) 
PARAMETRIC_REPRESENTATION_CONTEXT() REPRESENTATION_CONTEXT('2D SPACE',''
  ) );
#330 = ORIENTED_EDGE('',*,*,#194,.F.);
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
#345 = ( GEOMETRIC_REPRESENTATION_CONTEXT(3) 
GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#349)) GLOBAL_UNIT_ASSIGNED_CONTEXT
((#346,#347,#348)) REPRESENTATION_CONTEXT('Context #1',
  '3D Context with UNIT and UNCERTAINTY') );
#346 = ( LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.) );
#347 = ( NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.) );
#348 = ( NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT() );
#349 = UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.E-07),#346,
  'distance_accuracy_value','confusion accuracy');
#350 = PRODUCT_RELATED_PRODUCT_CATEGORY('part',$,(#7));
ENDSEC;
END-ISO-10303-21;
"""


def _find_entity_ids(step_text, entity_type):
    """Return the ids (as strings, in file order) of every top-level entity
    of the given STEP keyword, e.g. entity_type='PRODUCT_DEFINITION_SHAPE'."""
    pattern = re.compile(r"#(\d+)\s*=\s*" + entity_type + r"\s*\(")
    return pattern.findall(step_text)


def _next_entity_id(step_text):
    """Lowest unused entity id, computed from every '#N =' assignment in the
    file (not mere references), so injected entities can never collide with
    ids already used by an arbitrary uploaded STEP file."""
    ids = [int(m) for m in re.findall(r"#(\d+)\s*=", step_text)]
    return (max(ids) + 1) if ids else 1


def apply_material_metadata(step_text, material_name, properties=None):
    """
    Format-agnostic material-property injector for any valid ISO-10303-21
    STEP file. Locates PRODUCT-level entities dynamically by scanning the
    file's own entity ids, rather than assuming a fixed layout — so it
    works equally on our own generated specimens and on arbitrary
    user-uploaded STEP AP203/AP214/AP242 files. Appends PROPERTY_DEFINITION
    and MATERIAL_DESIGNATION entities readable by SolidWorks, FreeCAD,
    SpaceClaim, and ANSYS.

    Raises ValueError if the file has no recognizable product/shape entity
    to attach properties to (i.e. it isn't a real CAD part export).
    """
    sanitized_name = str(material_name).replace("'", "").replace('"', "")

    clean_props = {}
    if isinstance(properties, dict):
        for k, v in properties.items():
            if pd.notna(v) and v is not None and v != "":
                if isinstance(v, float):
                    val_str = f"{v:.4g}" if abs(v) < 10000 else f"{v:.2f}"
                else:
                    val_str = str(v)
                clean_props[str(k).strip()] = val_str.replace("'", "''")

    # Prefer PRODUCT_DEFINITION_SHAPE (the AP214-correct attach point for
    # shape/material properties); fall back progressively for files that
    # only expose the looser entity types.
    targets = _find_entity_ids(step_text, "PRODUCT_DEFINITION_SHAPE")
    if not targets:
        targets = _find_entity_ids(step_text, "PRODUCT_DEFINITION")
    if not targets:
        targets = _find_entity_ids(step_text, "PRODUCT")
    if not targets:
        raise ValueError(
            "No PRODUCT, PRODUCT_DEFINITION, or PRODUCT_DEFINITION_SHAPE "
            "entity was found in this STEP file, so material properties "
            "can't be attached to it. It may not be a valid CAD part export."
        )
    targets = list(dict.fromkeys(targets))  # de-dupe, preserve order

    cur_id = _next_entity_id(step_text)
    entities = []

    # Self-contained representation context: injected properties never
    # depend on parsing or guessing the host file's own context entity.
    ctx_id, len_id, ang_id, sang_id = cur_id, cur_id + 1, cur_id + 2, cur_id + 3
    entities.append(
        f"#{ctx_id} = ( GEOMETRIC_REPRESENTATION_CONTEXT(3) "
        f"GLOBAL_UNIT_ASSIGNED_CONTEXT((#{len_id},#{ang_id},#{sang_id})) "
        f"REPRESENTATION_CONTEXT('AI Material Selector Context','3D') );"
    )
    entities.append(f"#{len_id} = ( LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.) );")
    entities.append(f"#{ang_id} = ( NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.) );")
    entities.append(f"#{sang_id} = ( NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT() );")
    cur_id += 4

    def _emit_property(key, value, target_ent):
        nonlocal cur_id
        safe_key = re.sub(r'[^a-zA-Z0-9_]', '_', key).lower() or "property"
        safe_val = str(value).replace("'", "''")
        entities.append(f"#{cur_id}=PROPERTY_DEFINITION('{safe_key}','{key}',#{target_ent});")
        entities.append(f"#{cur_id + 1}=DESCRIPTIVE_REPRESENTATION_ITEM('{key}','{safe_val}');")
        entities.append(f"#{cur_id + 2}=REPRESENTATION('{key} representation',(#{cur_id + 1}),#{ctx_id});")
        entities.append(f"#{cur_id + 3}=PROPERTY_DEFINITION_REPRESENTATION(#{cur_id},#{cur_id + 2});")
        cur_id += 4

    for target_ent in targets:
        entities.append(f"#{cur_id}=MATERIAL_DESIGNATION('{sanitized_name}',#{target_ent});")
        cur_id += 1
        _emit_property("Material Name", sanitized_name, target_ent)
        _emit_property("Material", sanitized_name, target_ent)
        for prop_key, prop_val in clean_props.items():
            if prop_key == "Material Name":
                continue
            _emit_property(prop_key, prop_val, target_ent)

    mat_str = "\n".join(entities)
    endsec_idx = step_text.rfind("ENDSEC;")
    if endsec_idx == -1:
        return step_text + "\n" + mat_str
    return step_text[:endsec_idx] + mat_str + "\nENDSEC;" + step_text[endsec_idx + len("ENDSEC;"):].lstrip()


_TEMPLATE_SCALE_TOKEN = re.compile(r'(?<![\d.])(-?)(10|20)\.(?!\d)')


def _scale_cube_template(template_text, edge_mm):
    """Uniformly rescale the validated 20mm-cube template to any edge length.
    Safe because every '10.'/'20.' literal in the template is a coordinate or
    parametric-range value derived from the 20mm edge (verified: none are
    embedded in larger numbers) — a uniform scale keeps the topology valid."""
    scale = float(edge_mm) / 20.0

    def repl(m):
        val = float(m.group(1) + m.group(2)) * scale
        text = f"{val:g}"
        # STEP REAL literals require a decimal point (e.g. "10." not "10");
        # only append one if :g didn't already produce one (non-integer
        # scale factors, e.g. 37.5, would otherwise get a second "." tacked
        # on — "37.5." is not a valid REAL literal).
        return text if "." in text else text + "."

    return _TEMPLATE_SCALE_TOKEN.sub(repl, template_text)


def generate_step_file(material_name, properties=None, extra_metadata=None, dimensions=(20.0, 20.0, 20.0)):
    """
    Generate an ISO 10303 STEP AP214 file containing a 3D solid specimen with
    embedded material property metadata.

    dimensions=(length, width, height) in mm. When cadquery is available,
    any box dimensions are supported (real geometry kernel). Without it, the
    dependency-free fallback only supports a uniform cube (length==width==
    height) via a validated, rescaled template — a ValueError is raised for
    non-uniform dimensions in that case so the caller can surface a clear
    message rather than silently returning wrong geometry.
    """
    sanitized_id = re.sub(r'[^a-zA-Z0-9]', '_', str(material_name))
    sanitized_name = str(material_name).replace("'", "").replace('"', "")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    length, width, height = (float(d) for d in dimensions)

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
    if abs(length - width) < 1e-6 and abs(length - height) < 1e-6:
        size_desc = f"Standard {length:g}mm Specimen Cube"
    else:
        size_desc = f"Specimen Block {length:g}x{width:g}x{height:g}mm"

    base_step = None
    try:
        import cadquery as cq
        import tempfile
        box = cq.Workplane("XY").box(length, width, height)
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
        if abs(length - width) > 1e-6 or abs(length - height) > 1e-6:
            raise ValueError(
                "Non-uniform box dimensions (length, width, and height not all "
                "equal) need the optional cadquery geometry engine, which isn't "
                "available in this environment. Use equal length/width/height "
                "for a cube specimen."
            )
        template = OCCT_SOLID_TEMPLATE.format(
            sanitized_name=sanitized_name,
            sanitized_id=sanitized_id,
            header_desc=header_desc,
            timestamp=timestamp,
        )
        base_step = _scale_cube_template(template, length)

    # Non-greedy .*? (not [^)]*) because header_desc routinely contains its own
    # parentheses (e.g. "Density (g/cm³)=..."), which would otherwise truncate
    # the match early and silently leave the placeholder text unreplaced.
    base_step = re.sub(
        r"FILE_DESCRIPTION\(\(.*?\),'2;1'\);",
        lambda _m: f"FILE_DESCRIPTION(('Material Specimen: {sanitized_name}','{header_desc}','{size_desc}'),'2;1');",
        base_step
    )
    base_step = re.sub(
        r"FILE_NAME\([^;]*\);",
        f"FILE_NAME('{sanitized_id}_specimen.stp','{timestamp}',('AI Material Selector'),('AI Material Selector'),'2.0','AI Material Selector','{sanitized_name} - {header_desc}');",
        base_step
    )

    # 1. Update Product & Material Names in DATA section (#4, #5, #6, #7, #10, #15)
    base_step = base_step.replace("Open CASCADE STEP translator 7.9 1", sanitized_name)
    base_step = re.sub(r"PRODUCT_DEFINITION\('design','',#6,#9\);", f"PRODUCT_DEFINITION('design','{sanitized_name}',#6,#9);", base_step)
    base_step = re.sub(r"PRODUCT_DEFINITION_SHAPE\('','',#5\);", f"PRODUCT_DEFINITION_SHAPE('{sanitized_name}','{sanitized_name}',#5);", base_step)
    base_step = re.sub(r"PRODUCT_DEFINITION_FORMATION\('','',#7\);", f"PRODUCT_DEFINITION_FORMATION('{sanitized_name}','{sanitized_name}',#7);", base_step)
    base_step = re.sub(r"MANIFOLD_SOLID_BREP\('([^']*)',#16\);", f"MANIFOLD_SOLID_BREP('{sanitized_name}',#16);", base_step)
    base_step = re.sub(r"ADVANCED_BREP_SHAPE_REPRESENTATION\('([^']*)',\(#11,#15\),#345\);", f"ADVANCED_BREP_SHAPE_REPRESENTATION('{sanitized_name}_Shape',(#11,#15),#345);", base_step)

    # 2. Material property entities for SpaceClaim / ANSYS / SolidWorks / FreeCAD.
    # Delegates to the generic injector so generated specimens and
    # user-uploaded STEP files share one correctness-tested code path.
    return apply_material_metadata(base_step, sanitized_name, clean_props)






