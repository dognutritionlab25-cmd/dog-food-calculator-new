import streamlit as st
import pandas as pd

st.set_page_config(page_title="반려견 영양 연구소 계산기 v5.5", layout="wide")
st.title("🐶 반려견 영양 연구소 [생식 계산기 v5.5]")
st.info("💡 전문가용 맞춤형 영양 컨설팅 & 레시피 분석 시스템 | v5.5: 요오드 추가, 뼈재료 칼슘 Segal 실측값 교정, 켈프·양배추·배추 추가")

# ── AAFCO 기준 ─────────────────────────────────────────────────────────────
aafco_standards = {
    "단백질(g)": {"min": 45,   "max": None},
    "지방(g)":   {"min": 13.8, "max": None},
    "칼슘(mg)":  {"min": 1250, "max": 6250},
    "인(mg)":    {"min": 1000, "max": 4000},
    "철(mg)":    {"min": 10,   "max": None},
    "아연(mg)":  {"min": 20,   "max": None},
    "구리(mg)":  {"min": 1.83, "max": None},
    "망간(mg)":  {"min": 1.25, "max": None},
    "비타민A(IU)": {"min": 1250, "max": None},
    "비타민D(IU)": {"min": 125,  "max": None},
    "비타민E(IU)": {"min": 12.5, "max": None},
    "나트륨(mg)": {"min": 200,  "max": None},
    "요오드(mcg)": {"min": 220,  "max": 1400},  # NRC 2006 권장 220, 안전상한 1400 (1000kcal당)
}

# ── 아미노산 DB (생식 기준, 100g당 mg) ────────────────────────────────────
amino_db = {
    "닭가슴살(생,껍질제)": {"류신":1510,"이소류신":910,"발린":840,"페닐알라닌":830,"티로신":690,"트레오닌":860,"메티오닌":510,"리신":1700,"트립토판":260,"히스티딘":690,"아르기닌":1270},
    "소고기(lean)":        {"류신":1720,"이소류신":915,"발린":999,"페닐알라닌":803,"티로신":699,"트레오닌":937,"메티오닌":510,"리신":1807,"트립토판":244,"히스티딘":699,"아르기닌":1330},
    "말고기(lean,생)":     {"류신":1720,"이소류신":1030,"발린":1120,"페닐알라닌":890,"티로신":730,"트레오닌":970,"메티오닌":480,"리신":1850,"트립토판":270,"히스티딘":730,"아르기닌":1290},
    "양고기(lean,다리)":   {"류신":1665,"이소류신":897,"발린":1008,"페닐알라닌":695,"티로신":584,"트레오닌":813,"메티오닌":492,"리신":1769,"트립토판":224,"히스티딘":584,"아르기닌":1190},
    "염소고기(lean)":      {"류신":1716,"이소류신":1042,"발린":1103,"페닐알라닌":715,"티로신":600,"트레오닌":981,"메티오닌":552,"리신":1532,"트립토판":306,"히스티딘":600,"아르기닌":1260},
    "칠면조가슴살(생)":    {"류신":1310,"이소류신":765,"발린":873,"페닐알라닌":716,"티로신":598,"트레오닌":742,"메티오닌":463,"리신":1468,"트립토판":223,"히스티딘":598,"아르기닌":1100},
    "오리고기(lean,생)":   {"류신":1544,"이소류신":939,"발린":956,"페닐알라닌":766,"티로신":640,"트레오닌":781,"메티오닌":494,"리신":1564,"트립토판":254,"히스티딘":640,"아르기닌":1180},
    "사슴고기(lean,생)":   {"류신":2280,"이소류신":1287,"발린":1455,"페닐알라닌":1133,"티로신":830,"트레오닌":1133,"메티오닌":700,"리신":2434,"트립토판":266,"히스티딘":895,"아르기닌":2175},
    "소간(생)":            {"류신":1910,"이소류신":967,"발린":1260,"페닐알라닌":1084,"티로신":807,"트레오닌":869,"메티오닌":543,"리신":1607,"트립토판":263,"히스티딘":807,"아르기닌":1120},
    "닭간(생)":            {"류신":1512,"이소류신":813,"발린":998,"페닐알라닌":824,"티로신":653,"트레오닌":725,"메티오닌":432,"리신":1332,"트립토판":176,"히스티딘":653,"아르기닌":980},
    "소심장(생)":          {"류신":1700,"이소류신":950,"발린":1050,"페닐알라닌":820,"티로신":720,"트레오닌":900,"메티오닌":520,"리신":1750,"트립토판":250,"히스티딘":720,"아르기닌":1150},
    "소창자(생)":          {"류신":1580,"이소류신":894,"발린":1150,"페닐알라닌":746,"티로신":639,"트레오닌":797,"메티오닌":504,"리신":1530,"트립토판":231,"히스티딘":639,"아르기닌":1080},
    "소비장(생)":          {"류신":1100,"이소류신":620,"발린":840,"페닐알라닌":540,"티로신":415,"트레오닌":530,"메티오닌":350,"리신":1000,"트립토판":170,"히스티딘":415,"아르기닌":800},
    "정어리(생)":          {"류신":2001,"이소류신":1134,"발린":1268,"페닐알라닌":961,"티로신":783,"트레오닌":1079,"메티오닌":729,"리신":2260,"트립토판":276,"히스티딘":725,"아르기닌":1473},
    "계란노른자(생)":      {"류신":1200,"이소류신":700,"발린":800,"페닐알라닌":600,"티로신":600,"트레오닌":600,"메티오닌":300,"리신":1000,"트립토판":200,"히스티딘":400,"아르기닌":900},
    "굴(생,동부야생)":     {"류신":716,"이소류신":459,"발린":523,"페닐알라닌":413,"티로신":330,"트레오닌":242,"메티오닌":257,"리신":762,"트립토판":138,"히스티딘":220,"아르기닌":540},
}

amino_name_map = {
    "닭가슴살 (Chicken Breast)":    "닭가슴살(생,껍질제)",
    "소고기 (Beef)":                "소고기(lean)",
    "말고기 (Horse Meat)":          "말고기(lean,생)",
    "사슴고기 (Venison)":           "사슴고기(lean,생)",
    "정어리 (Sardine)":             "정어리(생)",
    "계란노른자 (Egg Yolk)":        "계란노른자(생)",
    "굴 (Oyster)":                  "굴(생,동부야생)",
    "소간 (Beef Liver)":            "소간(생)",
    "닭간 (Chicken Liver)":         "닭간(생)",
    "소심장 (Beef Heart)":          "소심장(생)",
    "소비장/지라 (Beef Spleen)":    "소비장(생)",
    "소폐 (Beef Lung)":             None,
    "소신장 (Beef Kidney)":         None,
    "소췌장 (Beef Pancreas)":       None,
    "소우신통 (Beef Penis)":        None,
    "닭심장 (Chicken Heart)":       None,
    "닭근위 (Chicken Gizzard)":     None,
    "오리간 (Duck Liver)":          None,
    "돼지간 (Pork Liver)":          None,
    "돼지신장 (Pork Kidney)":       None,
    "돼지심장 (Pork Heart)":        None,
    "그린트라이프 (Green Tripe)":   None,
    "블루베리 (Blueberry)":         None,
    "브로콜리 퓨레 (Broccoli)":     None,
    "토마토 퓨레 (Tomato)":         None,
    "우엉 퓨레 (Burdock Root)":     None,
    "청경채 퓨레 (Bok Choy)":       None,
    "단호박 퓨레 (Kabocha)":        None,
    "본브로스 소뼈 (Bone Broth)":   None,
    "파프리카 퓨레 (Paprika)":      None,
    "샐러리 퓨레 (Celery)":         None,
    "당근 퓨레 (Carrot)":           None,
    # v5.3 신규
    "칠면조 가슴살 (Turkey Breast)": "칠면조가슴살(생)",
    "오리 가슴살 (Duck Breast)":     "오리고기(lean,생)",
    "염소고기 (Goat)":               "염소고기(lean)",
    "양고기 (Lamb)":                 "양고기(lean,다리)",
    "열빙어 (Smelt)":                None,
    "산양유 케피어 (Goat Kefir)":    None,
    "초록홍합 (Green-Lipped Mussel)":None,
    # v5.4 신규
    "돼지 안심 (Pork Tenderloin)":  None,
    "양간 (Lamb Liver)":            None,
    "꿩 (Pheasant)":                None,
    "토끼고기 (Rabbit)":            None,
    "치아씨드 (Chia Seeds)":        None,
    "메추리알 (Quail Egg)":         None,
    "연어 (Salmon)":                None,
    # v5.5 신규
    "켈프 (Kelp/Seaweed)":         None,
    "양배추 퓨레 (Cabbage)":        None,
    "배추 퓨레 (Napa Cabbage)":     None,
}

# ── 오메가 DB ──────────────────────────────────────────────────────────────
omega_db = {
    "닭발 (뼈 60%)":               (0.45, 0.060, "7.5:1",  "USDA 곡물사육 닭 기준"),
    "닭목뼈 (뼈 36%)":             (0.45, 0.060, "7.5:1",  "USDA 곡물사육 닭 기준"),
    "닭날개 (뼈 45%)":             (0.45, 0.060, "7.5:1",  "USDA 곡물사육 닭 기준"),
    "닭북채 (뼈 30%)":             (0.45, 0.060, "7.5:1",  "USDA 곡물사육 닭 기준"),
    "전체 칠면조 (뼈 21%)":        (0.27, 0.060, "4.5:1",  "USDA 칠면조 raw"),
    "칠면조 목뼈 (뼈 42%)":        (0.27, 0.060, "4.5:1",  "USDA 칠면조 raw"),
    "칠면조 날개 (뼈 37%)":        (0.27, 0.060, "4.5:1",  "USDA 칠면조 raw"),
    "전체 오리 (뼈 28%)":          (0.98, 0.070, "14.0:1", "USDA 오리 raw 곡물사육"),
    "오리 목뼈 (뼈 50%)":          (0.98, 0.070, "14.0:1", "USDA 오리 raw 곡물사육"),
    "오리발 (뼈 60%)":             (0.98, 0.070, "14.0:1", "USDA 오리 raw 곡물사육"),
    "소갈비뼈 (뼈 52%)":           (0.14, 0.036, "3.9:1",  "USDA 소고기 lean raw"),
    "소꼬리 (뼈 55%)":             (0.14, 0.036, "3.9:1",  "USDA 소고기 lean raw"),
    "양 갈비뼈 (뼈 27%)":          (0.31, 0.080, "3.9:1",  "USDA 양고기 raw"),
    "양 목뼈 (뼈 32%)":            (0.31, 0.080, "3.9:1",  "USDA 양고기 raw"),
    "전체 메츄리 (뼈 10%)":        (0.27, 0.060, "4.5:1",  "메추리=칠면조 유사 적용"),
    "소간 (Beef Liver)":           (0.460, 0.065, "7.1:1", "USDA FDC 168627 raw"),
    "소심장 (Beef Heart)":         (0.260, 0.050, "5.2:1", "USDA FDC 168625 raw"),
    "소폐 (Beef Lung)":            (0.150, 0.040, "3.8:1", "USDA 추정"),
    "소신장 (Beef Kidney)":        (0.190, 0.060, "3.2:1", "USDA FDC 168630 raw 추정"),
    "소비장/지라 (Beef Spleen)":   (0.120, 0.030, "4.0:1", "USDA FDC raw 추정"),
    "닭간 (Chicken Liver)":        (0.560, 0.080, "7.0:1", "USDA FDC 172544 raw"),
    "닭심장 (Chicken Heart)":      (0.450, 0.065, "6.9:1", "USDA FDC raw 추정"),
    "닭근위 (Chicken Gizzard)":    (0.180, 0.040, "4.5:1", "USDA FDC 172552 raw"),
    "그린트라이프 (Green Tripe)":  (0.120, 0.030, "4.0:1", "초지 반추동물 추정"),
    "닭가슴살 (Chicken Breast)":   (0.450, 0.060, "7.5:1", "USDA FDC 171077 raw 곡물사육"),
    "소고기 (Beef)":               (0.140, 0.036, "3.9:1", "USDA FDC 174006 lean raw"),
    "말고기 (Horse Meat)":         (0.180, 0.070, "2.6:1", "방목 추정, ALA 풍부"),
    "사슴고기 (Venison)":          (0.225, 0.104, "2.2:1", "USDA Food Composite DB raw"),
    "정어리 (Sardine)":            (0.110, 1.480, "0.07:1","USDA 175139 EPA+DHA+ALA 합산"),
    "계란노른자 (Egg Yolk)":       (1.800, 0.100, "18.0:1","USDA raw 곡물사육"),
    "굴 (Oyster)":                 (0.040, 0.270, "0.15:1","USDA 175167 EPA+DHA 기준"),
    "블루베리 (Blueberry)":        (0.058, 0.043, "1.4:1", "USDA blueberry raw"),
    "브로콜리 퓨레 (Broccoli)":    (0.038, 0.105, "0.36:1","USDA raw broccoli"),
    "토마토 퓨레 (Tomato)":        (0.083, 0.004, "20.8:1","USDA raw tomato"),
    "당근 퓨레 (Carrot)":          (0.115, 0.002, "57.5:1","USDA raw carrot"),
    "파프리카 퓨레 (Paprika)":     (0.160, 0.030, "5.3:1", "USDA red bell pepper raw"),
    "샐러리 퓨레 (Celery)":        (0.079, 0.027, "2.9:1", "USDA celery raw"),
    # v5.3 신규
    "칠면조 가슴살 (Turkey Breast)": (0.27, 0.060, "4.5:1", "USDA FDC 171093 turkey breast raw"),
    "오리 가슴살 (Duck Breast)":     (0.98, 0.180, "5.4:1", "USDA FDC 174469 duck wild breast raw"),
    "염소고기 (Goat)":               (0.30, 0.080, "3.8:1", "USDA FDC 175306 goat raw 추정"),
    "양고기 (Lamb)":                 (0.31, 0.080, "3.9:1", "USDA FDC 174369 lamb leg raw"),
    "열빙어 (Smelt)":                (0.11, 0.470, "0.23:1","USDA FDC 175150 smelt rainbow raw, EPA+DHA"),
    "산양유 케피어 (Goat Kefir)":    (0.09, 0.015, "6.0:1", "USDA FDC 171264 goat milk 기반 추정"),
    "초록홍합 (Green-Lipped Mussel)":(0.18, 0.940, "0.19:1","littlechief.dog GLM 100g 오메가3 0.94g"),
    # v5.4 신규
    "돼지 안심 (Pork Tenderloin)":  (0.31, 0.007, "44:1",  "USDA FDC 168249 pork tenderloin raw"),
    "양간 (Lamb Liver)":            (0.091,0.102, "0.89:1","USDA FDC 172531 lamb liver raw"),
    "꿩 (Pheasant)":                (0.16, 0.050, "3.2:1", "USDA FDC 169902 pheasant raw 추정"),
    "토끼고기 (Rabbit)":            (0.244,0.062, "3.9:1", "USDA FDC 172521 rabbit domesticated raw"),
    "치아씨드 (Chia Seeds)":        (5.836,17.83, "0.33:1","USDA FDC 170554 chia seeds ALA+linoleic"),
    "메추리알 (Quail Egg)":         (0.44, 0.10,  "4.4:1", "USDA FDC 172188 quail egg raw 추정"),
    "연어 (Salmon)":                (0.11, 2.26,  "0.05:1","USDA FDC 175167 Atlantic salmon farmed raw EPA+DHA"),
    # v5.5 신규
    "켈프 (Kelp/Seaweed)":         (0.002,0.0,   "N/A",   "USDA FDC 168457 kelp raw — 오메가3 미미"),
    "양배추 퓨레 (Cabbage)":        (0.023,0.012, "1.9:1", "USDA FDC 169975 cabbage raw"),
    "배추 퓨레 (Napa Cabbage)":     (0.02, 0.027, "0.74:1","USDA FDC 169979 napa cabbage raw"),
}

# ── 메인 DB ────────────────────────────────────────────────────────────────
# category:
#   bone   = 뼈고기
#   meat   = 근육고기 (심장·폐·모래주머니·생식기 포함 — 근육성 기관)
#   organ  = 분비성 내장 (간·신장·비장·췌장 등)
#   veggie = 채소·과일·기타
db_data = [
    # ── 뼈류 ──
    # ── 뼈고기 (bone) ─────────────────────────────────────────────────────────
    # 칼슘 출처: Segal=Monica Segal K9 Kitchen 실측값, est=bone_pct×4166 추정값
    # 인(P): Segal 실측값 없음 → 뼈 Ca:P≈2:1 기준으로 칼슘×0.5 추정
    # 요오드: 해조류 아니므로 0
    {"재료명":"닭발 (뼈 60%)",        "category":"bone","bone_pct":0.60,"칼슘":2500,"인":1250,"칼슘출처":"est", "칼로리":215,"단백질":19.0,"지방":14.6,"철":2.0, "아연":1.5, "구리":0.1,  "망간":0.05,"비타민A":30,  "비타민D":0,  "비타민E":0,   "나트륨":67, "요오드(mcg)":0},
    {"재료명":"닭목뼈 (뼈 36%)",      "category":"bone","bone_pct":0.36,"칼슘":1150,"인":575, "칼슘출처":"Segal","칼로리":154,"단백질":17.6,"지방":8.78,"철":2.06,"아연":2.68,"구리":0.1,  "망간":0.03,"비타민A":146, "비타민D":0,  "비타민E":0,   "나트륨":81, "요오드(mcg)":0},
    {"재료명":"닭날개 (뼈 45%)",      "category":"bone","bone_pct":0.45,"칼슘":920, "인":460, "칼슘출처":"Segal","칼로리":203,"단백질":18.0,"지방":14.0,"철":1.0, "아연":1.0, "구리":0.1,  "망간":0.02,"비타민A":40,  "비타민D":0,  "비타민E":0.3, "나트륨":70, "요오드(mcg)":0},
    {"재료명":"닭북채 (뼈 30%)",      "category":"bone","bone_pct":0.30,"칼슘":880, "인":440, "칼슘출처":"Segal","칼로리":120,"단백질":18.0,"지방":4.0, "철":0.8, "아연":1.5, "구리":0.1,  "망간":0.02,"비타민A":20,  "비타민D":0,  "비타민E":0.2, "나트륨":80, "요오드(mcg)":0},
    {"재료명":"전체 칠면조 (뼈 21%)", "category":"bone","bone_pct":0.21,"칼슘":875, "인":438, "칼슘출처":"est", "칼로리":160,"단백질":20.0,"지방":8.0, "철":1.5, "아연":2.0, "구리":0.1,  "망간":0.02,"비타민A":50,  "비타민D":0,  "비타민E":0,   "나트륨":60, "요오드(mcg)":0},
    {"재료명":"칠면조 목뼈 (뼈 42%)", "category":"bone","bone_pct":0.42,"칼슘":1840,"인":920, "칼슘출처":"Segal","칼로리":225,"단백질":30.0,"지방":11.0,"철":2.0, "아연":3.0, "구리":0.2,  "망간":0.04,"비타민A":40,  "비타민D":0,  "비타민E":0,   "나트륨":90, "요오드(mcg)":0},
    {"재료명":"칠면조 날개 (뼈 37%)", "category":"bone","bone_pct":0.37,"칼슘":2900,"인":1450,"칼슘출처":"Segal","칼로리":200,"단백질":18.0,"지방":13.0,"철":1.5, "아연":1.5, "구리":0.1,  "망간":0.02,"비타민A":30,  "비타민D":0,  "비타민E":0,   "나트륨":80, "요오드(mcg)":0},
    {"재료명":"전체 오리 (뼈 28%)",   "category":"bone","bone_pct":0.28,"칼슘":870, "인":435, "칼슘출처":"Segal","칼로리":250,"단백질":15.0,"지방":20.0,"철":2.5, "아연":1.8, "구리":0.2,  "망간":0.03,"비타민A":60,  "비타민D":0,  "비타민E":0.5, "나트륨":65, "요오드(mcg)":0},
    {"재료명":"오리 목뼈 (뼈 50%)",   "category":"bone","bone_pct":0.50,"칼슘":2083,"인":1042,"칼슘출처":"est", "칼로리":250,"단백질":18.0,"지방":18.0,"철":2.8, "아연":2.0, "구리":0.2,  "망간":0.04,"비타민A":50,  "비타민D":0,  "비타민E":0,   "나트륨":85, "요오드(mcg)":0},
    {"재료명":"오리발 (뼈 60%)",      "category":"bone","bone_pct":0.60,"칼슘":2500,"인":1250,"칼슘출처":"est", "칼로리":253,"단백질":20.0,"지방":18.0,"철":2.0, "아연":1.5, "구리":0.1,  "망간":0.05,"비타민A":40,  "비타민D":0,  "비타민E":0,   "나트륨":90, "요오드(mcg)":0},
    {"재료명":"소갈비뼈 (뼈 52%)",    "category":"bone","bone_pct":0.52,"칼슘":2166,"인":1083,"칼슘출처":"est", "칼로리":300,"단백질":18.0,"지방":25.0,"철":3.0, "아연":4.5, "구리":0.1,  "망간":0.02,"비타민A":10,  "비타민D":2,  "비타민E":0,   "나트륨":70, "요오드(mcg)":0},
    {"재료명":"소꼬리 (뼈 55%)",      "category":"bone","bone_pct":0.55,"칼슘":2290,"인":1145,"칼슘출처":"est", "칼로리":262,"단백질":21.0,"지방":18.0,"철":4.9, "아연":3.5, "구리":0.1,  "망간":0.02,"비타민A":0,   "비타민D":0,  "비타민E":0,   "나트륨":60, "요오드(mcg)":0},
    {"재료명":"양 갈비뼈 (뼈 27%)",   "category":"bone","bone_pct":0.27,"칼슘":1360,"인":680, "칼슘출처":"Segal","칼로리":355,"단백질":22.0,"지방":30.0,"철":2.0, "아연":4.0, "구리":0.1,  "망간":0.02,"비타민A":0,   "비타민D":1,  "비타민E":0.1, "나트륨":76, "요오드(mcg)":0},
    {"재료명":"양 목뼈 (뼈 32%)",     "category":"bone","bone_pct":0.32,"칼슘":1333,"인":667, "칼슘출처":"est", "칼로리":260,"단백질":20.0,"지방":20.0,"철":4.0, "아연":4.2, "구리":0.2,  "망간":0.02,"비타민A":0,   "비타민D":0,  "비타민E":0,   "나트륨":70, "요오드(mcg)":0},
    {"재료명":"전체 메츄리 (뼈 10%)", "category":"bone","bone_pct":0.10,"칼슘":416, "인":208, "칼슘출처":"est", "칼로리":200,"단백질":20.0,"지방":12.0,"철":4.0, "아연":2.5, "구리":0.5,  "망간":0.02,"비타민A":50,  "비타민D":10, "비타민E":1.0, "나트륨":50, "요오드(mcg)":0},

    # ── 분비성 내장 (organ) ──
    {"재료명":"소간 (Beef Liver)",          "category":"organ","bone_pct":0,"칼로리":135,"단백질":20.4,"지방":3.63,"칼슘":5,  "인":387,"철":4.9,  "아연":4.0, "구리":9.76, "망간":0.31, "비타민A":16900,"비타민D":49,"비타민E":0.38,"나트륨":69, "요오드(mcg)":0},
    {"재료명":"소신장 (Beef Kidney)",        "category":"organ","bone_pct":0,"칼로리":97, "단백질":17.4,"지방":2.82,"칼슘":13, "인":257,"철":4.37, "아연":1.93,"구리":0.436,"망간":0.138,"비타민A":1166, "비타민D":49,"비타민E":0.29,"나트륨":182, "요오드(mcg)":0},
    {"재료명":"소비장/지라 (Beef Spleen)",   "category":"organ","bone_pct":0,"칼로리":105,"단백질":18.3,"지방":3.04,"칼슘":8,  "인":249,"철":30.3, "아연":2.42,"구리":0.147,"망간":0.032,"비타민A":8,    "비타민D":0, "비타민E":0.26,"나트륨":84, "요오드(mcg)":0},
    {"재료명":"소췌장 (Beef Pancreas)",      "category":"organ","bone_pct":0,"칼로리":233,"단백질":14.7,"지방":19.1,"칼슘":10, "인":234,"철":2.26, "아연":2.0, "구리":0.097,"망간":0.046,"비타민A":0,    "비타민D":0, "비타민E":0.23,"나트륨":85, "요오드(mcg)":0},
    {"재료명":"닭간 (Chicken Liver)",        "category":"organ","bone_pct":0,"칼로리":119,"단백질":16.9,"지방":4.83,"칼슘":8,  "인":297,"철":9.0,  "아연":2.67,"구리":0.492,"망간":0.351,"비타민A":3296, "비타민D":55,"비타민E":1.1, "나트륨":71, "요오드(mcg)":0},
    {"재료명":"오리간 (Duck Liver)",         "category":"organ","bone_pct":0,"칼로리":136,"단백질":18.7,"지방":4.64,"칼슘":11, "인":263,"철":30.5, "아연":2.68,"구리":0.999,"망간":0.314,"비타민A":4970, "비타민D":80,"비타민E":1.51,"나트륨":144, "요오드(mcg)":0},
    {"재료명":"돼지간 (Pork Liver)",         "category":"organ","bone_pct":0,"칼로리":134,"단백질":20.9,"지방":3.65,"칼슘":8,  "인":387,"철":17.9, "아연":4.02,"구리":0.796,"망간":0.355,"비타민A":6502, "비타민D":53,"비타민E":0.39,"나트륨":49, "요오드(mcg)":0},
    {"재료명":"돼지신장 (Pork Kidney)",      "category":"organ","bone_pct":0,"칼로리":100,"단백질":16.7,"지방":3.09,"칼슘":10, "인":244,"철":4.52, "아연":2.07,"구리":0.344,"망간":0.078,"비타민A":36,   "비타민D":49,"비타민E":0.26,"나트륨":113, "요오드(mcg)":0},
    {"재료명":"그린트라이프 (Green Tripe)",  "category":"organ","bone_pct":0,"칼로리":85, "단백질":14.9,"지방":1.98,"칼슘":112,"인":159,"철":4.44, "아연":1.72,"구리":0.094,"망간":4.06, "비타민A":20,   "비타민D":8, "비타민E":0.45,"나트륨":81, "요오드(mcg)":0},

    # ── 근육고기 (meat) — 심장·폐·모래주머니·생식기 포함 ──
    {"재료명":"닭가슴살 (Chicken Breast)",   "category":"meat","bone_pct":0,"칼로리":120,"단백질":22.5,"지방":2.62,"칼슘":5,  "인":213,"철":0.37, "아연":0.68,"구리":0.037,"망간":0.011,"비타민A":30,   "비타민D":0, "비타민E":0.56,"나트륨":45, "요오드(mcg)":0},
    {"재료명":"소고기 (Beef)",               "category":"meat","bone_pct":0,"칼로리":152,"단백질":20.8,"지방":7.0, "칼슘":10, "인":192,"철":2.33, "아연":4.97,"구리":0.075,"망간":0.01, "비타민A":14,   "비타민D":3, "비타민E":0.17,"나트륨":66, "요오드(mcg)":0},
    {"재료명":"말고기 (Horse Meat)",         "category":"meat","bone_pct":0,"칼로리":133,"단백질":21.4,"지방":4.6, "칼슘":6,  "인":221,"철":3.82, "아연":2.9, "구리":0.144,"망간":0.019,"비타민A":0,    "비타민D":0, "비타민E":0,   "나트륨":53, "요오드(mcg)":0},
    {"재료명":"사슴고기 (Venison)",          "category":"meat","bone_pct":0,"칼로리":116,"단백질":21.5,"지방":2.66,"칼슘":7,  "인":201,"철":2.92, "아연":4.2, "구리":0.14, "망간":0.014,"비타민A":0,    "비타민D":0, "비타민E":0,   "나트륨":75, "요오드(mcg)":0},
    {"재료명":"정어리 (Sardine)",            "category":"meat","bone_pct":0,"칼로리":208,"단백질":24.6,"지방":11.4,"칼슘":382,"인":490,"철":2.92, "아연":1.4, "구리":0.186,"망간":0,    "비타민A":30,   "비타민D":4.8,"비타민E":1.38,"나트륨":307, "요오드(mcg)":0},
    {"재료명":"계란노른자 (Egg Yolk)",       "category":"meat","bone_pct":0,"칼로리":322,"단백질":15.9,"지방":26.5,"칼슘":129,"인":390,"철":2.73, "아연":2.3, "구리":0.077,"망간":0.31, "비타민A":1440, "비타민D":49,"비타민E":0.38,"나트륨":48, "요오드(mcg)":0},
    # 근육성 기관 (organ → meat 재분류)
    {"재료명":"소심장 (Beef Heart)",         "category":"meat","bone_pct":0,"칼로리":112,"단백질":18.5,"지방":3.4, "칼슘":4,  "인":209,"철":4.38, "아연":1.51,"구리":0.373,"망간":0.034,"비타민A":34,   "비타민D":6, "비타민E":1.22,"나트륨":86, "요오드(mcg)":0},
    {"재료명":"소폐 (Beef Lung)",            "category":"meat","bone_pct":0,"칼로리":92, "단백질":16.2,"지방":2.5, "칼슘":10, "인":224,"철":7.95, "아연":1.61,"구리":0.26, "망간":0.019,"비타민A":46,   "비타민D":0, "비타민E":0,   "나트륨":198, "요오드(mcg)":0},
    {"재료명":"소우신통 (Beef Penis)",       "category":"meat","bone_pct":0,"칼로리":120,"단백질":22.0,"지방":3.0, "칼슘":8,  "인":180,"철":2.0,  "아연":2.0, "구리":0.1,  "망간":0.02, "비타민A":0,    "비타민D":0, "비타민E":0.5, "나트륨":70, "요오드(mcg)":0},
    {"재료명":"닭심장 (Chicken Heart)",      "category":"meat","bone_pct":0,"칼로리":153,"단백질":15.6,"지방":9.33,"칼슘":11, "인":159,"철":5.95, "아연":6.49,"구리":0.301,"망간":0.073,"비타민A":34,   "비타민D":0, "비타민E":1.0, "나트륨":65, "요오드(mcg)":0},
    {"재료명":"닭근위 (Chicken Gizzard)",    "category":"meat","bone_pct":0,"칼로리":94, "단백질":17.7,"지방":2.06,"칼슘":9,  "인":148,"철":2.49, "아연":2.72,"구리":0.122,"망간":0.038,"비타민A":40,   "비타민D":0, "비타민E":0.22,"나트륨":69, "요오드(mcg)":0},
    {"재료명":"돼지심장 (Pork Heart)",       "category":"meat","bone_pct":0,"칼로리":118,"단백질":17.7,"지방":4.67,"칼슘":6,  "인":210,"철":3.37, "아연":2.63,"구리":0.382,"망간":0.031,"비타민A":0,    "비타민D":49,"비타민E":0.83,"나트륨":57, "요오드(mcg)":0},

    # ── 채소·과일·기타 (veggie) ──
    {"재료명":"굴 (Oyster)",                 "category":"veggie","bone_pct":0,"칼로리":68, "단백질":7.67,"지방":2.68,"칼슘":49, "인":151,"철":7.28, "아연":98.9,"구리":4.85, "망간":0.45, "비타민A":326,  "비타민D":1, "비타민E":0.92,"나트륨":122, "요오드(mcg)":0},
    {"재료명":"블루베리 (Blueberry)",        "category":"veggie","bone_pct":0,"칼로리":57, "단백질":0.74,"지방":0.33,"칼슘":6,  "인":12, "철":0.28, "아연":0.06,"구리":1.6,  "망간":0.262,"비타민A":54,   "비타민D":0, "비타민E":0.57,"나트륨":1, "요오드(mcg)":0},
    {"재료명":"브로콜리 퓨레 (Broccoli)",   "category":"veggie","bone_pct":0,"칼로리":34, "단백질":2.82,"지방":0.37,"칼슘":47, "인":66, "철":0.73, "아연":0.41,"구리":0.049,"망간":0.21, "비타민A":623,  "비타민D":0, "비타민E":0.78,"나트륨":33, "요오드(mcg)":0},
    {"재료명":"토마토 퓨레 (Tomato)",       "category":"veggie","bone_pct":0,"칼로리":18, "단백질":0.88,"지방":0.2, "칼슘":10, "인":24, "철":0.27, "아연":0.17,"구리":0.059,"망간":0.114,"비타민A":833,  "비타민D":0, "비타민E":0.54,"나트륨":5, "요오드(mcg)":0},
    {"재료명":"우엉 퓨레 (Burdock Root)",   "category":"veggie","bone_pct":0,"칼로리":72, "단백질":1.53,"지방":0.15,"칼슘":41, "인":51, "철":0.8,  "아연":0.33,"구리":0.08, "망간":0.23, "비타민A":0,    "비타민D":0, "비타민E":0.4, "나트륨":5, "요오드(mcg)":0},
    {"재료명":"청경채 퓨레 (Bok Choy)",    "category":"veggie","bone_pct":0,"칼로리":13, "단백질":1.5, "지방":0.2, "칼슘":105,"인":37, "철":0.8,  "아연":0.19,"구리":0.021,"망간":0.159,"비타민A":4468, "비타민D":0, "비타민E":0.09,"나트륨":65, "요오드(mcg)":0},
    {"재료명":"단호박 퓨레 (Kabocha)",     "category":"veggie","bone_pct":0,"칼로리":34, "단백질":1.0, "지방":0.1, "칼슘":20, "인":30, "철":0.4,  "아연":0.15,"구리":0.07, "망간":0.15, "비타민A":1370, "비타민D":0, "비타민E":0.3, "나트륨":3, "요오드(mcg)":0},
    {"재료명":"본브로스 소뼈 (Bone Broth)","category":"veggie","bone_pct":0,"칼로리":18, "단백질":4.0, "지방":0.0, "칼슘":5,  "인":10, "철":0.2,  "아연":0.1, "구리":0.02, "망간":0,    "비타민A":0,    "비타민D":0, "비타민E":0,   "나트륨":20, "요오드(mcg)":0},
    {"재료명":"파프리카 퓨레 (Paprika)",   "category":"veggie","bone_pct":0,"칼로리":31, "단백질":1.0, "지방":0.3, "칼슘":7,  "인":26, "철":0.43, "아연":0.25,"구리":0.017,"망간":0.11, "비타민A":3131, "비타민D":0, "비타민E":1.58,"나트륨":4, "요오드(mcg)":0},
    {"재료명":"샐러리 퓨레 (Celery)",     "category":"veggie","bone_pct":0,"칼로리":16, "단백질":0.69,"지방":0.17,"칼슘":40, "인":24, "철":0.2,  "아연":0.13,"구리":0.04, "망간":0.1,  "비타민A":449,  "비타민D":0, "비타민E":0.27,"나트륨":80, "요오드(mcg)":0},
    {"재료명":"당근 퓨레 (Carrot)",       "category":"veggie","bone_pct":0,"칼로리":41, "단백질":0.93,"지방":0.24,"칼슘":33, "인":35, "철":0.3,  "아연":0.24,"구리":0.045,"망간":0.143,"비타민A":16706,"비타민D":0, "비타민E":0.66,"나트륨":69, "요오드(mcg)":0},

    # ── v5.3 신규 추가 ──────────────────────────────────────────────────────
    # 칠면조 가슴살 (USDA FDC 171093 Turkey breast raw)
    {"재료명":"칠면조 가슴살 (Turkey Breast)",  "category":"meat","bone_pct":0,"칼로리":111,"단백질":24.6,"지방":0.7, "칼슘":10, "인":206,"철":1.2,  "아연":1.2, "구리":0.06, "망간":0.02, "비타민A":0,    "비타민D":0,  "비타민E":0.1, "나트륨":49, "요오드(mcg)":0},
    # 오리 가슴살 야생 (USDA FDC 174469 Duck wild breast raw)
    {"재료명":"오리 가슴살 (Duck Breast)",      "category":"meat","bone_pct":0,"칼로리":123,"단백질":19.8,"지방":4.3, "칼슘":3,  "인":186,"철":4.5,  "아연":1.5, "구리":0.26, "망간":0.02, "비타민A":60,   "비타민D":0,  "비타민E":0.5, "나트륨":57, "요오드(mcg)":0},
    # 염소고기 (USDA FDC 175306 Goat raw)
    {"재료명":"염소고기 (Goat)",               "category":"meat","bone_pct":0,"칼로리":109,"단백질":20.6,"지방":2.31,"칼슘":13, "인":180,"철":2.83, "아연":4.5, "구리":0.11, "망간":0.019,"비타민A":0,    "비타민D":0,  "비타민E":0.27,"나트륨":82, "요오드(mcg)":0},
    # 양고기 다리살 (USDA FDC 174369 Lamb leg raw)
    {"재료명":"양고기 (Lamb)",                 "category":"meat","bone_pct":0,"칼로리":153,"단백질":20.3,"지방":7.64,"칼슘":16, "인":190,"철":1.88, "아연":3.95,"구리":0.117,"망간":0.023,"비타민A":0,    "비타민D":0,  "비타민E":0.14,"나트륨":72, "요오드(mcg)":0},
    # 열빙어/smelt (USDA FDC 175150 Smelt rainbow raw)
    {"재료명":"열빙어 (Smelt)",                "category":"meat","bone_pct":0,"칼로리":97, "단백질":17.6,"지방":2.42,"칼슘":60, "인":230,"철":0.9,  "아연":1.7, "구리":0.14, "망간":0.7,  "비타민A":15,   "비타민D":32, "비타민E":0.5, "나트륨":60, "요오드(mcg)":0},
    # 산양유 케피어/요거트 (USDA FDC 171264 Goat milk raw 기반, 발효로 단백질/칼슘 소폭 조정)
    {"재료명":"산양유 케피어 (Goat Kefir)",    "category":"meat","bone_pct":0,"칼로리":69, "단백질":3.5, "지방":4.0, "칼슘":134,"인":111,"철":0.05, "아연":0.3, "구리":0.05, "망간":0.02, "비타민A":185,  "비타민D":4,  "비타민E":0.1, "나트륨":50, "요오드(mcg)":0},
    # 초록홍합 생 (NZ Green-lipped mussel raw USDA SR28 + littlechief.dog 교차검증)
    {"재료명":"초록홍합 (Green-Lipped Mussel)","category":"meat","bone_pct":0,"칼로리":80, "단백질":11.9,"지방":2.24,"칼슘":33, "인":285,"철":3.36, "아연":2.67,"구리":0.15, "망간":3.4,  "비타민A":40,   "비타민D":4,  "비타민E":0.9, "나트륨":185, "요오드(mcg)":0},

    # ── v5.4 신규 추가 ──────────────────────────────────────────────────────
    # 돼지 안심 (USDA FDC 168249 Pork tenderloin raw)
    {"재료명":"돼지 안심 (Pork Tenderloin)",    "category":"meat","bone_pct":0,"칼로리":109,"단백질":20.9,"지방":2.1, "칼슘":5,  "인":247,"철":0.97, "아연":1.88,"구리":0.094,"망간":0.012,"비타민A":0,    "비타민D":8,  "비타민E":0.22,"나트륨":53, "요오드(mcg)":0},
    # 양간 (USDA FDC 172531 Lamb liver raw) — 100g 환산
    {"재료명":"양간 (Lamb Liver)",              "category":"organ","bone_pct":0,"칼로리":139,"단백질":20.7,"지방":5.1, "칼슘":7,  "인":369,"철":7.5,  "아연":4.6, "구리":7.14, "망간":0.18, "비타민A":6990, "비타민D":0,  "비타민E":0,   "나트륨":71, "요오드(mcg)":0},
    # 꿩 살코기 생 (USDA FDC 169902 Pheasant raw meat only)
    {"재료명":"꿩 (Pheasant)",                  "category":"meat","bone_pct":0,"칼로리":133,"단백질":23.6,"지방":3.6, "칼슘":12, "인":214,"철":1.1,  "아연":1.0, "구리":0.07, "망간":0.01, "비타민A":177,  "비타민D":0,  "비타민E":0,   "나트륨":40, "요오드(mcg)":0},
    # 토끼고기 가정사육 생 (USDA FDC 172521 Rabbit domesticated raw)
    {"재료명":"토끼고기 (Rabbit)",              "category":"meat","bone_pct":0,"칼로리":136,"단백질":20.4,"지방":5.6, "칼슘":13, "인":216,"철":1.6,  "아연":1.6, "구리":0.14, "망간":0.04, "비타민A":0,    "비타민D":0,  "비타민E":0,   "나트륨":41, "요오드(mcg)":0},
    # 치아씨드 (USDA FDC 170554 Chia seeds raw)
    {"재료명":"치아씨드 (Chia Seeds)",          "category":"veggie","bone_pct":0,"칼로리":486,"단백질":16.5,"지방":30.7,"칼슘":631,"인":860,"철":7.7,  "아연":4.6, "구리":0.924,"망간":2.72, "비타민A":54,   "비타민D":0,  "비타민E":0.5, "나트륨":16, "요오드(mcg)":0},
    # 메추리알 생 (USDA FDC 172188 Quail egg raw)
    {"재료명":"메추리알 (Quail Egg)",           "category":"meat","bone_pct":0,"칼로리":158,"단백질":13.1,"지방":11.1,"칼슘":64, "인":226,"철":3.65, "아연":1.47,"구리":0.11, "망간":0.10, "비타민A":543,  "비타민D":132,"비타민E":1.08,"나트륨":141, "요오드(mcg)":0},
    # 연어 대서양 양식 생 (USDA FDC 175167 Salmon Atlantic farmed raw)
    {"재료명":"연어 (Salmon)",                  "category":"meat","bone_pct":0,"칼로리":208,"단백질":20.4,"지방":13.4,"칼슘":9,  "인":240,"철":0.34, "아연":0.36,"구리":0.05, "망간":0.01, "비타민A":50,   "비타민D":447,"비타민E":3.55,"나트륨":59,  "요오드(mcg)":0},
    # ── v5.5 신규 ──────────────────────────────────────────────────────────
    # 켈프 생 (USDA FDC 168457) — 요오드는 제품·종·산지마다 다름, 1500mcg/100g은 참고값
    # NRC 권장: 220mcg/1000kcal, 안전상한: 1400mcg/1000kcal
    {"재료명":"켈프 (Kelp/Seaweed)",            "category":"veggie","bone_pct":0,"칼로리":43, "단백질":1.68,"지방":0.56,"칼슘":168,"인":42, "철":2.85, "아연":1.23,"구리":0.13, "망간":0.2,  "비타민A":116, "비타민D":0,  "비타민E":0.87,"나트륨":233, "요오드(mcg)":1500},
    # 양배추 퓨레 생 (USDA FDC 169975 Cabbage raw)
    {"재료명":"양배추 퓨레 (Cabbage)",          "category":"veggie","bone_pct":0,"칼로리":25, "단백질":1.28,"지방":0.1, "칼슘":40, "인":26,  "철":0.47, "아연":0.18,"구리":0.019,"망간":0.16, "비타민A":98,  "비타민D":0,  "비타민E":0.15,"나트륨":18,  "요오드(mcg)":0},
    # 배추 퓨레 생 (USDA FDC 169979 Napa cabbage raw)
    {"재료명":"배추 퓨레 (Napa Cabbage)",       "category":"veggie","bone_pct":0,"칼로리":12, "단백질":0.9, "지방":0.1, "칼슘":105,"인":37,  "철":0.8,  "아연":0.19,"구리":0.021,"망간":0.16, "비타민A":4468,"비타민D":0,  "비타민E":0.09,"나트륨":65,  "요오드(mcg)":0},
]
food_df = pd.DataFrame(db_data)

# ── 강아지 정보 ────────────────────────────────────────────────────────────
col1, col2 = st.columns([1, 2])
with col1:
    st.subheader("🐶 강아지 정보")
    weight = st.number_input("몸무게 (kg)", 0.1, 60.0, 3.0, step=0.1)
    der_options = {
        "3.0: 성장기 강아지 (퍼피)": 3.0,
        "2.0: 체중 증가 필요": 2.0,
        "2.0: 매우 활동적인 성견 / 야외 훈련량 많음": 2.0,
        "1.8: 비중성화 성견 · 보통 활동량": 1.8,
        "1.6: 중성화 성견 · 보통 활동량 (기본값) ⭐": 1.6,
        "1.4: 중성화 성견 · 낮은 활동량 / 비만 경향": 1.4,
        "1.4: 노견 · 활동적": 1.4,
        "1.2: 중성화 성견 · 매우 낮은 활동량": 1.2,
        "1.2: 노견 · 보통": 1.2,
        "1.0: 노견 · 거의 안 움직임": 1.0,
        "1.0: 체중 감량이 필요한 성견 (다이어트)": 1.0,
    }
    selected_label = st.selectbox("강아지의 현재 상태를 선택해 주세요!", list(der_options.keys()), index=4)
    activity = der_options[selected_label]
    rer = 70 * (weight ** 0.75)
    der = rer * activity
    st.metric("하루 목표 칼로리 (DER)", f"{der:.1f} kcal")

with col2:
    st.subheader("🥩 냉장고 털기 (재료 선택)")
    all_foods = food_df['재료명'].tolist()
    bone_options = [f for f in all_foods if food_df[food_df['재료명']==f]['category'].values[0]=='bone']
    selected = st.multiselect("재료를 고르세요:", all_foods, default=[bone_options[0]] if bone_options else [])
    st.caption("💡 심장·폐·모래주머니·우신통은 근육고기로 분류됩니다")

# ── 급여량 입력 ──────────────────────────────────────────────────────────────
amounts = {}
if selected:
    cols = st.columns(3)
    for i, f in enumerate(selected):
        with cols[i % 3]:
            amounts[f] = st.number_input(f"{f} (g)", 0, 1000, 50, step=5)

# ── 계산 ────────────────────────────────────────────────────────────────────
if selected:
    st.divider()
    total_grams = sum(amounts.values())
    mass_breakdown = {"actual_bone": 0, "muscle_meat": 0, "organ": 0, "veggie": 0}
    total_stats = {k: 0.0 for k in aafco_standards}
    total_kcal = 0.0
    recipe_save_list = []
    aa_keys = ["류신","이소류신","발린","페닐알라닌","티로신","트레오닌","메티오닌","리신","트립토판","히스티딘","아르기닌"]
    total_amino = {k: 0.0 for k in aa_keys}
    omega6_total = 0.0
    omega3_total = 0.0

    for f in selected:
        grams = amounts[f]
        if grams <= 0:
            continue
        recipe_save_list.append({"재료명": f, "급여량(g)": grams})
        row = food_df[food_df['재료명'] == f].iloc[0]
        ratio = grams / 100
        total_kcal += row['칼로리'] * ratio
        for nutri in aafco_standards:
            # 요오드(mcg)는 컬럼명에 단위 포함이라 별도 처리
            col_name = nutri if nutri in row.index else nutri.split("(")[0]
            if col_name in row:
                total_stats[nutri] += row[col_name] * ratio
        cat, b_pct = row['category'], row['bone_pct']
        if cat == 'bone':
            mass_breakdown['actual_bone'] += grams * b_pct
            mass_breakdown['muscle_meat'] += grams * (1 - b_pct)
        elif cat == 'meat':
            mass_breakdown['muscle_meat'] += grams
        elif cat == 'organ':
            mass_breakdown['organ'] += grams
        else:
            mass_breakdown['veggie'] += grams
        ak = amino_name_map.get(f)
        if ak and ak in amino_db:
            for aa, val in amino_db[ak].items():
                if aa in total_amino:
                    total_amino[aa] += val * ratio
        if f in omega_db:
            o6_per100, o3_per100, _, _ = omega_db[f]
            omega6_total += o6_per100 * ratio
            omega3_total += o3_per100 * ratio

    # 레시피 저장
    st.subheader("💾 레시피 저장 및 고객 발송")
    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        if recipe_save_list:
            csv = pd.DataFrame(recipe_save_list).to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 엑셀(CSV) 파일로 저장하기", csv, f"영양레시피_{weight}kg.csv", "text/csv")
    with c_btn2:
        with st.expander("🖨️ PDF로 저장해서 고객에게 보내려면?"):
            st.markdown("1. **`Ctrl+P`** (맥 `Cmd+P`) 누르세요.\n2. 프린터를 **'PDF로 저장'**으로 바꾸세요.\n3. **저장** 클릭!")
    st.divider()

    # ── 탭 ──
    tab1, tab2, tab3, tab4 = st.tabs(["📊 AAFCO 영양분석", "🧬 아미노산 분석", "🐟 오메가 6:3 분석", "🔬 아연:구리 비율"])

    # TAB 1 ─ AAFCO
    with tab1:
        c1, c2 = st.columns([1, 2])
        with c1:
            st.subheader("⚖️ 식단 비율")
            st.metric("총 급여량", f"{total_grams:.1f} g")
            if total_grams > 0:
                pct_bone   = (mass_breakdown['actual_bone']  / total_grams) * 100
                pct_meat   = (mass_breakdown['muscle_meat']  / total_grams) * 100
                pct_organ  = (mass_breakdown['organ']        / total_grams) * 100
                pct_veggie = (mass_breakdown['veggie']       / total_grams) * 100
                st.write(f"🦴 **뼈 ({pct_bone:.1f}%)** | 목표 12%");         st.progress(min(pct_bone/20,1.0))
                st.write(f"🥩 **살코기 ({pct_meat:.1f}%)** | 목표 60~70%"); st.progress(min(pct_meat/100,1.0))
                st.write(f"🫀 **내장 ({pct_organ:.1f}%)** | 목표 10~25%");  st.progress(min(pct_organ/40,1.0))
                st.write(f"🥦 **야채 ({pct_veggie:.1f}%)** | 목표 5~10%"); st.progress(min(pct_veggie/20,1.0))
                st.caption("💡 심장·폐·모래주머니·우신통은 살코기로 분류")
        with c2:
            st.subheader("📊 AAFCO 영양 분석")
            if total_kcal > 0:
                kcal_pct = (total_kcal / der) * 100
                kc1, kc2, kc3 = st.columns(3)
                with kc1: st.metric("🔥 섭취 칼로리", f"{total_kcal:.0f} kcal")
                with kc2: st.metric("🎯 목표 칼로리", f"{der:.0f} kcal")
                with kc3:
                    delta_kcal = total_kcal - der
                    st.metric("📈 차이", f"{delta_kcal:+.0f} kcal",
                              delta=f"{kcal_pct:.1f}% 충족",
                              delta_color="normal" if abs(delta_kcal)<50 else ("inverse" if delta_kcal>0 else "off"))
                st.progress(min(kcal_pct/100,1.0), text=f"칼로리 충족률: {kcal_pct:.1f}%")
                # Ca:P 비율 사전 계산 (칼슘 판정에 반영)
                ca, p = total_stats["칼슘(mg)"], total_stats["인(mg)"]
                cap_ratio = ca / p if p > 0 else 0
                cap_ok = 1.1 <= cap_ratio <= 2.0

                res_data = []
                for nutri, std in aafco_standards.items():
                    val_1000 = (total_stats[nutri] / total_kcal) * 1000
                    min_v, max_v = std['min'], std['max']
                    status = "✅ 적합"
                    if val_1000 < min_v:
                        status = f"❌ 부족 (최소 {min_v})"
                    elif max_v and val_1000 > max_v:
                        status = f"⚠️ 과잉 (최대 {max_v})"
                    # 칼슘은 절대량이 적합해도 Ca:P 범위 벗어나면 불균형으로 표시
                    if nutri == "칼슘(mg)" and status == "✅ 적합" and not cap_ok:
                        status = f"⚠️ Ca:P 불균형 ({cap_ratio:.2f}:1, 권장 1.1~2:1)"
                    res_data.append({"영양소":nutri,"현재(1000kcal당)":f"{val_1000:.2f}","AAFCO 기준":f"{min_v}~{max_v if max_v else ''}","판정":status})
                res_df = pd.DataFrame(res_data)
                def color_status(val):
                    return f'color:{"green" if "적합" in val else "red" if "부족" in val else "orange"};font-weight:bold'
                st.dataframe(res_df.style.map(color_status, subset=['판정']), use_container_width=True)
                if p > 0:
                    cap_color = "normal" if cap_ok else "error"
                    if cap_ok:
                        st.info(f"🦴 **Ca:P 비율 = {cap_ratio:.2f} : 1** ✅ (권장 1.1~2 : 1)")
                    else:
                        st.warning(f"🦴 **Ca:P 비율 = {cap_ratio:.2f} : 1** ⚠️ 권장 범위(1.1~2:1) 벗어남 — 뼈재료를 조정하세요.")

                # 켈프 요오드 안내
                if "켈프 (Kelp/Seaweed)" in selected:
                    st.info(
                        "🌿 **켈프 요오드 안내**: DB 요오드값(1500mcg/100g)은 참고값입니다. "
                        "제품·종·산지에 따라 500~8000mcg/100g으로 편차가 매우 큽니다. "
                        "실제 급여 시 제품 라벨의 요오드 함량을 반드시 확인하세요. "
                        f"(NRC 권장 220mcg/1000kcal, 안전상한 1400mcg/1000kcal)"
                    )
                # 칼슘출처 표시
                has_est = any(
                    food_df[food_df['재료명'] == f].iloc[0].get('칼슘출처', '') == 'est'
                    for f in selected if f in food_df['재료명'].values
                    and food_df[food_df['재료명'] == f].iloc[0].get('category') == 'bone'
                )
                if has_est:
                    st.caption("🦴 뼈재료 칼슘값 중 일부는 bone_pct 기반 추정값(est)입니다. "
                               "실측값(Segal 출처) 재료: 닭목뼈, 닭날개, 닭북채, 전체오리, 칠면조목뼈, 칠면조날개, 양갈비뼈")

    # TAB 2 ─ 아미노산
    with tab2:
        st.subheader("🧬 필수 아미노산 분석")
        st.caption("출처: 노션 자료(근육육/내장) + USDA FoodData Central | 생식(raw) 기준")
        st.caption("⚠️ 뼈류·소폐·그린트라이프·신규 내장육 일부·야채 퓨레는 아미노산 데이터 없음 — 집계 제외")
        nrc_adult = {"류신":1700,"이소류신":950,"발린":1230,"메티오닌":830,"리신":1580,"트레오닌":1200,"트립토판":400,"히스티딘":480,"페닐알라닌":1130,"아르기닌":1280}
        nrc_puppy = {"류신":2550,"이소류신":1430,"발린":1840,"메티오닌":1245,"리신":2370,"트레오닌":1800,"트립토판":600,"히스티딘":720,"페닐알라닌":1695,"아르기닌":1920}
        display_aa = ["류신","이소류신","발린","메티오닌","리신","트레오닌","트립토판","히스티딘","페닐알라닌","아르기닌"]
        has_amino = any(amino_name_map.get(f) in amino_db for f in selected if amounts.get(f,0)>0)
        if has_amino and total_kcal > 0:
            aa_result = []
            for aa in display_aa:
                total_mg = total_amino.get(aa, 0)
                per_1000 = total_mg / total_kcal * 1000
                nrc_min = nrc_adult.get(aa)
                status = ("✅" if per_1000 >= nrc_min else "⚠️") if nrc_min else "-"
                aa_result.append({"아미노산":aa,"총량(mg)":f"{total_mg:.0f}","1000kcal당(mg)":f"{per_1000:.0f}","NRC 성견기준":str(nrc_min) if nrc_min else "-","판정":status})
            def color_aa(val):
                if "✅" in str(val): return "color:green;font-weight:bold"
                if "⚠️" in str(val): return "color:orange;font-weight:bold"
                return ""
            st.dataframe(pd.DataFrame(aa_result).style.map(color_aa,subset=["판정"]),use_container_width=True,hide_index=True)
            st.caption("💡 NRC 기준은 가공사료 기준 최솟값 — 생식은 열처리 손실이 없어 동일 수치도 실제 흡수량이 더 높습니다.")
            st.divider()
            st.markdown("##### 🔍 아미노산 용도별 분석")
            card1, card2, card3 = st.columns(3)
            with card1:
                st.markdown("**🐾 성장기 퍼피**")
                for aa in ["류신","리신","아르기닌","트레오닌"]:
                    mg=total_amino.get(aa,0); p1k=mg/total_kcal*1000; ref=nrc_puppy.get(aa,0)
                    st.markdown(f"**{aa}** {mg:.0f}mg | 1000kcal당 {p1k:.0f}mg {'✅' if p1k>=ref else '⚠️'}")
                    st.caption(f"퍼피 기준 {ref}mg/1000kcal")
            with card2:
                st.markdown("**🦴 노령견 근육 유지**")
                bcaa_names=["류신","이소류신","발린"]
                bcaa_total=sum(total_amino.get(a,0) for a in bcaa_names)
                bcaa_p1k=bcaa_total/total_kcal*1000
                st.metric("💪 BCAA 합계",f"{bcaa_total:.0f}mg",delta=f"1000kcal당 {bcaa_p1k:.0f}mg")
                for aa in ["류신","이소류신","발린","리신"]:
                    mg=total_amino.get(aa,0); p1k=mg/total_kcal*1000; ref=nrc_adult.get(aa,0)
                    st.markdown(f"**{aa}** {mg:.0f}mg {'✅' if p1k>=ref else '⚠️'}")
                    st.caption(f"성견 기준 {ref}mg/1000kcal")
            with card3:
                st.markdown("**✨ 피부·털 건강**")
                met=total_amino.get("메티오닌",0); met1k=met/total_kcal*1000; ref_met=nrc_adult.get("메티오닌",830)
                st.metric("🟡 메티오닌",f"{met:.0f}mg",delta=f"1000kcal당 {met1k:.0f}mg")
                st.caption(f"성견 기준 {ref_met}mg/1000kcal {'✅' if met1k>=ref_met else '⚠️'}")
                phe=total_amino.get("페닐알라닌",0); trp=total_amino.get("트립토판",0)
                aaa=phe+trp; aaa1k=aaa/total_kcal*1000
                ref_phe=nrc_adult.get("페닐알라닌",1130); ref_trp=nrc_adult.get("트립토판",400)
                st.metric("🔵 페닐알라닌+트립토판",f"{aaa:.0f}mg",delta=f"1000kcal당 {aaa1k:.0f}mg")
                st.markdown(f"**페닐알라닌** {phe:.0f}mg {'✅' if phe/total_kcal*1000>=ref_phe else '⚠️'}")
                st.markdown(f"**트립토판** {trp:.0f}mg {'✅' if trp/total_kcal*1000>=ref_trp else '⚠️'}")
            st.divider()
            with st.expander("📋 재료별 아미노산 상세"):
                detail=[]
                for f in selected:
                    if amounts.get(f,0)>0:
                        ak=amino_name_map.get(f); row_d={"재료명":f,"급여량(g)":amounts[f]}
                        if ak and ak in amino_db: row_d.update({k:f"{v}mg" for k,v in amino_db[ak].items() if k in display_aa})
                        else: row_d["류신"]="데이터없음"
                        detail.append(row_d)
                st.dataframe(pd.DataFrame(detail),use_container_width=True)
        else:
            st.warning("아미노산 데이터가 있는 재료를 추가하세요 (근육육 / 내장).")

    # TAB 3 ─ 오메가
    with tab3:
        st.subheader("🐟 오메가 6:3 비율 분석")
        st.caption("출처: USDA FoodData Central raw 데이터 기반")
        if omega6_total + omega3_total > 0:
            ratio_omega = omega6_total / omega3_total if omega3_total > 0 else 999
            co1,co2,co3=st.columns(3)
            with co1: st.metric("오메가-6 추정량",f"{omega6_total:.2f} g")
            with co2: st.metric("오메가-3 추정량",f"{omega3_total:.2f} g")
            with co3: st.metric("오메가 6:3 비율",f"{ratio_omega:.1f} : 1")
            if ratio_omega<=5:   st.success(f"✅ {ratio_omega:.1f}:1 — 항염증 범위.")
            elif ratio_omega<=10: st.warning(f"⚠️ {ratio_omega:.1f}:1 — 허용범위. 정어리·말고기 추가 권장.")
            else:                 st.error(f"❌ {ratio_omega:.1f}:1 — 오메가-6 과잉. 정어리를 추가하세요.")
            od=[]
            for f in selected:
                if amounts.get(f,0)>0 and f in omega_db:
                    o6_per100,o3_per100,ratio_str,note=omega_db[f]; g=amounts[f]
                    od.append({"재료명":f,"급여량(g)":g,"O6/100g(g)":f"{o6_per100:.3f}","O3/100g(g)":f"{o3_per100:.3f}","해당량 O6(g)":f"{o6_per100*g/100:.3f}","해당량 O3(g)":f"{o3_per100*g/100:.3f}","비율":ratio_str,"비고":note})
            if od: st.dataframe(pd.DataFrame(od),use_container_width=True)
        else:
            st.info("오메가 데이터가 있는 재료를 선택하면 분석 결과가 나타납니다.")
        st.info("💡 정어리(생)·말고기·목초 소고기·야생 사슴이 오메가-3 비율 개선에 가장 효과적입니다.")

    # TAB 4 ─ 아연:구리 비율
    with tab4:
        st.subheader("🔬 아연:구리 비율 분석")
        st.caption("✨ 생식의 미네랄 균형을 확인하세요")
        with st.expander("📋 생식 vs 사료 기준 비교"):
            standards_df=pd.DataFrame({"기준":["AAFCO (사료)","NRC (사료)","FEDIAF (사료)","🥩 생식 전문가 권장","⭐ 생식 최적 범위"],"구리 (mg/1000kcal)":["7.3","6.0","7.3","2.0","-"],"아연 (mg/1000kcal)":["120","80-100","100","15-20","-"],"아연:구리 비율":["16.4:1","10:1","10:1","7.5:1 ~ 10:1","**5:1 ~ 12:1**"]})
            st.table(standards_df)
            st.caption("⚠️ 사료 기준(AAFCO/NRC)은 가공 사료용입니다. 생식은 다른 기준 적용!")
        st.markdown("---")
        copper_value = total_stats["구리(mg)"] / total_kcal * 1000 if total_kcal > 0 else 0
        zinc_value   = total_stats["아연(mg)"] / total_kcal * 1000 if total_kcal > 0 else 0
        col1,col2,col3=st.columns(3)
        with col1:
            st.markdown("#### 구리")
            st.metric("현재 값",f"{copper_value:.2f} mg",delta=f"{copper_value-1.83:.2f}",delta_color="normal" if copper_value>=1.83 else "inverse")
            st.caption("AAFCO 기준: 1.83 mg 이상")
        with col2:
            st.markdown("#### 아연")
            st.metric("현재 값",f"{zinc_value:.2f} mg",delta=f"{zinc_value-20:.2f}",delta_color="normal" if zinc_value>=15 else "inverse")
            st.caption("생식 권장: 15-20 mg")
        with col3:
            st.markdown("#### 아연:구리 비율")
            if copper_value > 0:
                ratio=zinc_value/copper_value
                if 5<=ratio<=12:   dt,dc="생식 기준 이상적","normal"
                elif 12<ratio<=16: dt,dc="약간 높음","off"
                else:              dt,dc="범위 벗어남","inverse"
                st.metric("현재 비율",f"{ratio:.1f}:1",delta=dt,delta_color=dc)
                st.caption("생식 권장: 5:1 ~ 12:1")
            else:
                st.metric("현재 비율","계산 불가")
        st.markdown("---")
        if copper_value > 0:
            ratio=zinc_value/copper_value
            st.markdown("### 🎯 평가 결과 (생식 기준)")
            if 5<=ratio<=12:
                st.success(f"✅ **생식 기준 이상적인 비율입니다!**\n\n- 현재 비율: {ratio:.1f}:1\n- 생식 권장 범위: 5:1 ~ 12:1\n\n💡 AAFCO 사료 기준(10:1~20:1)과 다릅니다. 생식은 구리 함량이 높은 간을 포함하므로 낮은 비율이 정상입니다.")
            elif 12<ratio<=16:
                st.info(f"ℹ️ **생식 기준 약간 높지만 허용 범위입니다**\n\n- 현재 비율: {ratio:.1f}:1\n- 소간 비중 약간 증가 (구리 풍부) 또는 현재 유지")
            elif ratio>16:
                st.warning(f"⚠️ **아연이 다소 높습니다** (생식 기준)\n\n- 현재 비율: {ratio:.1f}:1\n- 소간 또는 닭간 비중 증가 / 조개류 추가")
            elif 3<=ratio<5:
                st.warning(f"⚠️ **비율이 약간 낮습니다**\n\n- 현재 비율: {ratio:.1f}:1\n- 근육고기(소고기·양고기) 비중 증가 / 간 비중 약간 감소")
            else:
                st.error(f"❌ **아연이 부족합니다!**\n\n- 현재 비율: {ratio:.1f}:1\n- 근육고기 대폭 증가 / 굴 추가 / 아연 보충제 고려")
        else:
            st.info("ℹ️ 재료를 추가하여 구리와 아연 값을 확인하세요.")

else:
    st.info("재료를 선택하면 분석 결과가 나타납니다.")

st.markdown("---")
st.caption("반려견영양연구소 | 생식 계산기 v5.3")
