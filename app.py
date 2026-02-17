import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="반려견 영양 연구소 계산기 v4.0", layout="wide")

# --- [상단 헤더] ---
st.title("🐶 반려견 영양 연구소 [생식 계산기 v4.0]")
st.info("💡 전문가용 맞춤형 영양 컨설팅 & 레시피 분석 시스템 | 아미노산 · 오메가 분석 추가")

# --- [1. AAFCO 기준] ---
aafco_standards = {
    "단백질(g)": {"min": 45, "max": None},
    "지방(g)": {"min": 13.8, "max": None},
    "칼슘(mg)": {"min": 1250, "max": 6250},
    "인(mg)": {"min": 1000, "max": 4000},
    "철(mg)": {"min": 10, "max": None},
    "아연(mg)": {"min": 20, "max": None},
    "구리(mg)": {"min": 1.83, "max": None},
    "망간(mg)": {"min": 1.25, "max": None},
    "비타민A(IU)": {"min": 1250, "max": None},
    "비타민D(IU)": {"min": 125, "max": None},
    "비타민E(IU)": {"min": 12.5, "max": None},
    "나트륨(mg)": {"min": 200, "max": None},
}

# --- [2. 아미노산 데이터베이스 (생식 기준, 100g당 mg)] ---
# 출처: 노션 자료(근육육/내장) + USDA FoodData Central(정어리생/계란노른자/굴)
amino_db = {
    # 근육육 (노션 자료)
    "닭가슴살(생,껍질제)":    {"류신": 1510, "이소류신": 910, "발린": 840, "페닐알라닌": 830, "티로신": 690, "트레오닌": 860, "메티오닌": 510, "리신": 1700, "트립토판": 260, "히스티딘": 690, "아르기닌": 1270},
    "소고기(lean)":           {"류신": 1720, "이소류신": 915, "발린": 999, "페닐알라닌": 803, "티로신": 699, "트레오닌": 937, "메티오닌": 510, "리신": 1807, "트립토판": 244, "히스티딘": 699, "아르기닌": 1330},
    "말고기(lean,생)":        {"류신": 1720, "이소류신": 1030, "발린": 1120, "페닐알라닌": 890, "티로신": 730, "트레오닌": 970, "메티오닌": 480, "리신": 1850, "트립토판": 270, "히스티딘": 730, "아르기닌": 1290},
    "양고기(lean,다리)":      {"류신": 1665, "이소류신": 897, "발린": 1008, "페닐알라닌": 695, "티로신": 584, "트레오닌": 813, "메티오닌": 492, "리신": 1769, "트립토판": 224, "히스티딘": 584, "아르기닌": 1190},
    "염소고기(lean)":         {"류신": 1716, "이소류신": 1042, "발린": 1103, "페닐알라닌": 715, "티로신": 600, "트레오닌": 981, "메티오닌": 552, "리신": 1532, "트립토판": 306, "히스티딘": 600, "아르기닌": 1260},
    "칠면조가슴살(생)":       {"류신": 1310, "이소류신": 765, "발린": 873, "페닐알라닌": 716, "티로신": 598, "트레오닌": 742, "메티오닌": 463, "리신": 1468, "트립토판": 223, "히스티딘": 598, "아르기닌": 1100},
    "오리고기(lean,생)":      {"류신": 1544, "이소류신": 939, "발린": 956, "페닐알라닌": 766, "티로신": 640, "트레오닌": 781, "메티오닌": 494, "리신": 1564, "트립토판": 254, "히스티딘": 640, "아르기닌": 1180},
    # 내장 (노션 자료)
    "소간(생)":               {"류신": 1910, "이소류신": 967, "발린": 1260, "페닐알라닌": 1084, "티로신": 807, "트레오닌": 869, "메티오닌": 543, "리신": 1607, "트립토판": 263, "히스티딘": 807, "아르기닌": 1120},
    "닭간(생)":               {"류신": 1512, "이소류신": 813, "발린": 998, "페닐알라닌": 824, "티로신": 653, "트레오닌": 725, "메티오닌": 432, "리신": 1332, "트립토판": 176, "히스티딘": 653, "아르기닌": 980},
    "소심장(생)":             {"류신": 1700, "이소류신": 950, "발린": 1050, "페닐알라닌": 820, "티로신": 720, "트레오닌": 900, "메티오닌": 520, "리신": 1750, "트립토판": 250, "히스티딘": 720, "아르기닌": 1150},
    "소창자(생)":             {"류신": 1580, "이소류신": 894, "발린": 1150, "페닐알라닌": 746, "티로신": 639, "트레오닌": 797, "메티오닌": 504, "리신": 1530, "트립토판": 231, "히스티딘": 639, "아르기닌": 1080},
    "소비장(생)":             {"류신": 1100, "이소류신": 620, "발린": 840, "페닐알라닌": 540, "티로신": 415, "트레오닌": 530, "메티오닌": 350, "리신": 1000, "트립토판": 170, "히스티딘": 415, "아르기닌": 800},
    # USDA 기준 (생 기준)
    "정어리(생)":             {"류신": 2001, "이소류신": 1134, "발린": 1268, "페닐알라닌": 961, "티로신": 783, "트레오닌": 1079, "메티오닌": 729, "리신": 2260, "트립토판": 276, "히스티딘": 725, "아르기닌": 1473},
    "계란노른자(생)":         {"류신": 1200, "이소류신": 700, "발린": 800, "페닐알라닌": 600, "티로신": 600, "트레오닌": 600, "메티오닌": 300, "리신": 1000, "트립토판": 200, "히스티딘": 400, "아르기닌": 900},
    "굴(생,동부야생)":        {"류신": 716, "이소류신": 459, "발린": 523, "페닐알라닌": 413, "티로신": 330, "트레오닌": 242, "메티오닌": 257, "리신": 762, "트립토판": 138, "히스티딘": 220, "아르기닌": 540},
}

# db_data 재료명 → amino_db 키 매핑
amino_name_map = {
    "닭가슴살 (Chicken Breast)": "닭가슴살(생,껍질제)",
    "소고기 (Beef)": "소고기(lean)",
    "말고기 (Horse Meat)": "말고기(lean,생)",
    "사슴고기 (Venison)": None,
    "정어리 (Sardine)": "정어리(생)",
    "계란노른자 (Egg Yolk)": "계란노른자(생)",
    "굴 (Oyster)": "굴(생,동부야생)",
    "소간 (Beef Liver)": "소간(생)",
    "소심장 (Beef Heart)": "소심장(생)",
    "소폐 (Beef Lung)": None,
    "그린트라이프 (Green Tripe)": None,
    "블루베리 (Blueberry)": None,
}

# --- [3. 오메가 6:3 비율 데이터베이스] ---
# (o6비율, o3비율, 표시문자열, 비고)
omega_db = {
    "닭발 (뼈 60%)":            (15, 1, "15:1",       "곡물사육 가금류"),
    "닭목뼈 (뼈 36%)":          (11, 1, "11:1~12:1",  "껍질제거시 개선"),
    "닭날개 (뼈 45%)":          (15, 1, "15:1",       "곡물사육 기준"),
    "닭북채 (뼈 30%)":          (15, 1, "15:1",       "곡물사육 기준"),
    "전체 칠면조 (뼈 21%)":     (5, 1,  "3:1~6:1",    "방사 기준"),
    "칠면조 목뼈 (뼈 42%)":     (5, 1,  "3:1~6:1",    "방사 기준"),
    "칠면조 날개 (뼈 37%)":     (5, 1,  "3:1~6:1",    "방사 기준"),
    "전체 오리 (뼈 28%)":       (13, 1, "12:1~15:1",  "곡물사육 오리"),
    "오리 목뼈 (뼈 50%)":       (13, 1, "12:1~15:1",  "곡물사육 오리"),
    "오리발 (뼈 60%)":          (13, 1, "12:1~15:1",  "곡물사육 오리"),
    "소갈비뼈 (뼈 52%)":        (4, 1,  "3:1~5:1",    "목초비육 기준"),
    "소꼬리 (뼈 55%)":          (4, 1,  "3:1~5:1",    "목초비육 기준"),
    "양 갈비뼈 (뼈 27%)":       (4, 1,  "3:1~4:1",    "양고기"),
    "양 목뼈 (뼈 32%)":         (4, 1,  "3:1~4:1",    "양고기"),
    "전체 메츄리 (뼈 10%)":     (5, 1,  "4:1~6:1",    "메추리"),
    "소간 (Beef Liver)":        (4, 1,  "3:1~5:1",    "소 내장"),
    "소심장 (Beef Heart)":      (4, 1,  "3:1~5:1",    "소 내장"),
    "소폐 (Beef Lung)":         (4, 1,  "3:1~5:1",    "소 내장"),
    "그린트라이프 (Green Tripe)":(5, 1,  "3:1~6:1",    "천연 촉매제"),
    "닭가슴살 (Chicken Breast)": (17, 1, "15:1~20:1",  "케이지/곡물사육"),
    "소고기 (Beef)":             (4, 1,  "3:1~5:1",    "목초비육 기준"),
    "말고기 (Horse Meat)":       (3, 1,  "2:1~5:1",    "청정 적색육, ALA풍부"),
    "사슴고기 (Venison)":        (2, 1,  "1.5:1~3:1",  "진화적 정답"),
    "정어리 (Sardine)":          (1, 2,  "0.1:1~1:1",  "최고의 항염 식품"),
    "계란노른자 (Egg Yolk)":     (9, 1,  "8:1~10:1",   "사육방식에 따라 변동"),
    "굴 (Oyster)":               (1, 1,  "~1:1",       "EPA/DHA 풍부"),
    "블루베리 (Blueberry)":      (5, 1,  "4:1~6:1",    "항산화 위주"),
}

# --- [4. 메인 데이터베이스] ---
db_data = [
    {"재료명": "닭발 (뼈 60%)", "category": "bone", "bone_pct": 0.60, "칼로리": 215, "단백질": 19.0, "지방": 14.6, "칼슘": 2500, "인": 1500, "철": 2.0, "아연": 1.5, "구리": 0.1, "망간": 0.05, "비타민A": 30, "비타민D": 0, "비타민E": 0, "나트륨": 67},
    {"재료명": "닭목뼈 (뼈 36%)", "category": "bone", "bone_pct": 0.36, "칼로리": 154, "단백질": 17.6, "지방": 8.78, "칼슘": 1500, "인": 900, "철": 2.06, "아연": 2.68, "구리": 0.1, "망간": 0.03, "비타민A": 146, "비타민D": 0, "비타민E": 0, "나트륨": 81},
    {"재료명": "닭날개 (뼈 45%)", "category": "bone", "bone_pct": 0.45, "칼로리": 203, "단백질": 18.0, "지방": 14.0, "칼슘": 1875, "인": 1125, "철": 1.0, "아연": 1.0, "구리": 0.1, "망간": 0.02, "비타민A": 40, "비타민D": 0, "비타민E": 0.3, "나트륨": 70},
    {"재료명": "닭북채 (뼈 30%)", "category": "bone", "bone_pct": 0.30, "칼로리": 120, "단백질": 18.0, "지방": 4.0, "칼슘": 1250, "인": 750, "철": 0.8, "아연": 1.5, "구리": 0.1, "망간": 0.02, "비타민A": 20, "비타민D": 0, "비타민E": 0.2, "나트륨": 80},
    {"재료명": "전체 칠면조 (뼈 21%)", "category": "bone", "bone_pct": 0.21, "칼로리": 160, "단백질": 20.0, "지방": 8.0, "칼슘": 875, "인": 525, "철": 1.5, "아연": 2.0, "구리": 0.1, "망간": 0.02, "비타민A": 50, "비타민D": 0, "비타민E": 0, "나트륨": 60},
    {"재료명": "칠면조 목뼈 (뼈 42%)", "category": "bone", "bone_pct": 0.42, "칼로리": 225, "단백질": 30.0, "지방": 11.0, "칼슘": 1750, "인": 1050, "철": 2.0, "아연": 3.0, "구리": 0.2, "망간": 0.04, "비타민A": 40, "비타민D": 0, "비타민E": 0, "나트륨": 90},
    {"재료명": "칠면조 날개 (뼈 37%)", "category": "bone", "bone_pct": 0.37, "칼로리": 200, "단백질": 18.0, "지방": 13.0, "칼슘": 1540, "인": 925, "철": 1.5, "아연": 1.5, "구리": 0.1, "망간": 0.02, "비타민A": 30, "비타민D": 0, "비타민E": 0, "나트륨": 80},
    {"재료명": "전체 오리 (뼈 28%)", "category": "bone", "bone_pct": 0.28, "칼로리": 250, "단백질": 15.0, "지방": 20.0, "칼슘": 1166, "인": 700, "철": 2.5, "아연": 1.8, "구리": 0.2, "망간": 0.03, "비타민A": 60, "비타민D": 0, "비타민E": 0.5, "나트륨": 65},
    {"재료명": "오리 목뼈 (뼈 50%)", "category": "bone", "bone_pct": 0.50, "칼로리": 250, "단백질": 18.0, "지방": 18.0, "칼슘": 2083, "인": 1250, "철": 2.8, "아연": 2.0, "구리": 0.2, "망간": 0.04, "비타민A": 50, "비타민D": 0, "비타민E": 0, "나트륨": 85},
    {"재료명": "오리발 (뼈 60%)", "category": "bone", "bone_pct": 0.60, "칼로리": 253, "단백질": 20.0, "지방": 18.0, "칼슘": 2500, "인": 1500, "철": 2.0, "아연": 1.5, "구리": 0.1, "망간": 0.05, "비타민A": 40, "비타민D": 0, "비타민E": 0, "나트륨": 90},
    {"재료명": "소갈비뼈 (뼈 52%)", "category": "bone", "bone_pct": 0.52, "칼로리": 300, "단백질": 18.0, "지방": 25.0, "칼슘": 2166, "인": 1300, "철": 3.0, "아연": 4.5, "구리": 0.1, "망간": 0.02, "비타민A": 10, "비타민D": 2, "비타민E": 0, "나트륨": 70},
    {"재료명": "소꼬리 (뼈 55%)", "category": "bone", "bone_pct": 0.55, "칼로리": 262, "단백질": 21.0, "지방": 18.0, "칼슘": 2290, "인": 1375, "철": 4.9, "아연": 3.5, "구리": 0.1, "망간": 0.02, "비타민A": 0, "비타민D": 0, "비타민E": 0, "나트륨": 60},
    {"재료명": "양 갈비뼈 (뼈 27%)", "category": "bone", "bone_pct": 0.27, "칼로리": 355, "단백질": 22.0, "지방": 30.0, "칼슘": 1125, "인": 675, "철": 2.0, "아연": 4.0, "구리": 0.1, "망간": 0.02, "비타민A": 0, "비타민D": 1, "비타민E": 0.1, "나트륨": 76},
    {"재료명": "양 목뼈 (뼈 32%)", "category": "bone", "bone_pct": 0.32, "칼로리": 260, "단백질": 20.0, "지방": 20.0, "칼슘": 1333, "인": 800, "철": 4.0, "아연": 4.2, "구리": 0.2, "망간": 0.02, "비타민A": 0, "비타민D": 0, "비타민E": 0, "나트륨": 70},
    {"재료명": "전체 메츄리 (뼈 10%)", "category": "bone", "bone_pct": 0.10, "칼로리": 200, "단백질": 20.0, "지방": 12.0, "칼슘": 416, "인": 250, "철": 4.0, "아연": 2.5, "구리": 0.5, "망간": 0.02, "비타민A": 50, "비타민D": 10, "비타민E": 1.0, "나트륨": 50},
    {"재료명": "소간 (Beef Liver)", "category": "organ", "bone_pct": 0, "칼로리": 135, "단백질": 20.4, "지방": 3.63, "칼슘": 5, "인": 387, "철": 4.9, "아연": 4.0, "구리": 9.76, "망간": 0.31, "비타민A": 16900, "비타민D": 49, "비타민E": 0.38, "나트륨": 69},
    {"재료명": "소심장 (Beef Heart)", "category": "organ", "bone_pct": 0, "칼로리": 112, "단백질": 18.5, "지방": 3.4, "칼슘": 4, "인": 209, "철": 4.38, "아연": 1.51, "구리": 0.373, "망간": 0.034, "비타민A": 34, "비타민D": 6, "비타민E": 1.22, "나트륨": 86},
    {"재료명": "소폐 (Beef Lung)", "category": "organ", "bone_pct": 0, "칼로리": 92, "단백질": 16.2, "지방": 2.5, "칼슘": 10, "인": 224, "철": 7.95, "아연": 1.61, "구리": 0.26, "망간": 0.019, "비타민A": 46, "비타민D": 0, "비타민E": 0, "나트륨": 198},
    {"재료명": "그린트라이프 (Green Tripe)", "category": "organ", "bone_pct": 0, "칼로리": 85, "단백질": 14.9, "지방": 1.98, "칼슘": 112, "인": 159, "철": 4.44, "아연": 1.72, "구리": 0.094, "망간": 4.06, "비타민A": 20, "비타민D": 8, "비타민E": 0.45, "나트륨": 81},
    {"재료명": "닭가슴살 (Chicken Breast)", "category": "meat", "bone_pct": 0, "칼로리": 120, "단백질": 22.5, "지방": 2.62, "칼슘": 5, "인": 213, "철": 0.37, "아연": 0.68, "구리": 0.037, "망간": 0.011, "비타민A": 30, "비타민D": 0, "비타민E": 0.56, "나트륨": 45},
    {"재료명": "소고기 (Beef)", "category": "meat", "bone_pct": 0, "칼로리": 152, "단백질": 20.8, "지방": 7.0, "칼슘": 10, "인": 192, "철": 2.33, "아연": 4.97, "구리": 0.075, "망간": 0.01, "비타민A": 14, "비타민D": 3, "비타민E": 0.17, "나트륨": 66},
    {"재료명": "말고기 (Horse Meat)", "category": "meat", "bone_pct": 0, "칼로리": 133, "단백질": 21.4, "지방": 4.6, "칼슘": 6, "인": 221, "철": 3.82, "아연": 2.9, "구리": 0.144, "망간": 0.019, "비타민A": 0, "비타민D": 0, "비타민E": 0, "나트륨": 53},
    {"재료명": "사슴고기 (Venison)", "category": "meat", "bone_pct": 0, "칼로리": 116, "단백질": 21.5, "지방": 2.66, "칼슘": 7, "인": 201, "철": 2.92, "아연": 4.2, "구리": 0.14, "망간": 0.014, "비타민A": 0, "비타민D": 0, "비타민E": 0, "나트륨": 75},
    {"재료명": "정어리 (Sardine)", "category": "meat", "bone_pct": 0, "칼로리": 208, "단백질": 24.6, "지방": 11.4, "칼슘": 382, "인": 490, "철": 2.92, "아연": 1.4, "구리": 0.186, "망간": 0, "비타민A": 30, "비타민D": 4.8, "비타민E": 1.38, "나트륨": 307},
    {"재료명": "계란노른자 (Egg Yolk)", "category": "meat", "bone_pct": 0, "칼로리": 322, "단백질": 15.9, "지방": 26.5, "칼슘": 129, "인": 390, "철": 2.73, "아연": 2.3, "구리": 0.077, "망간": 0.31, "비타민A": 1440, "비타민D": 49, "비타민E": 0.38, "나트륨": 48},
    {"재료명": "굴 (Oyster)", "category": "veggie", "bone_pct": 0, "칼로리": 68, "단백질": 7.67, "지방": 2.68, "칼슘": 49, "인": 151, "철": 7.28, "아연": 98.9, "구리": 4.85, "망간": 0.45, "비타민A": 326, "비타민D": 1, "비타민E": 0.92, "나트륨": 122},
    {"재료명": "블루베리 (Blueberry)", "category": "veggie", "bone_pct": 0, "칼로리": 57, "단백질": 0.74, "지방": 0.33, "칼슘": 6, "인": 12, "철": 0.28, "아연": 0.06, "구리": 1.6, "망간": 0.262, "비타민A": 54, "비타민D": 0, "비타민E": 0.57, "나트륨": 1},
]
food_df = pd.DataFrame(db_data)

# --- [5. 메인 화면] ---
col1, col2 = st.columns([1, 2])
with col1:
    st.subheader("🐶 강아지 정보")
    weight = st.number_input("몸무게 (kg)", 0.1, 60.0, 3.0, step=0.1)
    der_options = {
        "1.0: 체중 감량이 필요한 성견 (다이어트)": 1.0,
        "1.2: 중성화 성견 · 매우 낮은 활동량": 1.2,
        "1.4: 중성화 성견 · 낮은 활동량 / 비만 경향": 1.4,
        "1.6: 중성화 성견 · 보통 활동량 (기본값) ⭐": 1.6,
        "1.8: 비중성화 성견 · 보통 활동량": 1.8,
        "2.0: 매우 활동적인 성견 / 야외·훈련량 많음": 2.0,
        "3.0: 성장기 강아지 (퍼피)": 3.0
    }
    selected_label = st.selectbox("강아지의 현재 상태를 선택해 주세요!", options=list(der_options.keys()), index=3)
    activity = der_options[selected_label]
    rer = 70 * (weight ** 0.75)
    der = rer * activity
    st.metric(label="하루 목표 칼로리 (DER)", value=f"{der:.1f} kcal")

with col2:
    st.subheader("🥩 냉장고 털기 (재료 선택)")
    all_foods = food_df['재료명'].tolist()
    bone_options = [f for f in all_foods if "뼈" in f or "발" in f or "날개" in f or "전체" in f]
    default_selections = [bone_options[0]] if bone_options else []
    selected = st.multiselect("재료를 고르세요:", all_foods, default=default_selections)

amounts = {}
if selected:
    cols = st.columns(3)
    for i, f in enumerate(selected):
        with cols[i % 3]:
            amounts[f] = st.number_input(f"{f} (g)", 0, 1000, 50, step=5)

# --- [6. 계산 및 판정] ---
if selected:
    st.divider()

    total_grams = sum(amounts.values())
    mass_breakdown = {"actual_bone": 0, "muscle_meat": 0, "organ": 0, "veggie": 0}
    total_stats = {k: 0 for k in aafco_standards.keys()}
    total_kcal = 0
    recipe_save_list = []
    aa_keys = ["류신", "이소류신", "발린", "페닐알라닌", "티로신", "트레오닌", "메티오닌", "리신", "트립토판", "히스티딘", "아르기닌"]
    total_amino = {k: 0 for k in aa_keys}
    omega6_total = 0.0
    omega3_total = 0.0

    for f in selected:
        grams = amounts[f]
        if grams > 0:
            recipe_save_list.append({"재료명": f, "급여량(g)": grams})
            row = food_df[food_df['재료명'] == f].iloc[0]
            ratio = grams / 100
            total_kcal += row['칼로리'] * ratio

            for nutri in aafco_standards.keys():
                col_name = nutri.split("(")[0]
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

            # 아미노산
            amino_key = amino_name_map.get(f)
            if amino_key and amino_key in amino_db:
                for aa, val in amino_db[amino_key].items():
                    if aa in total_amino:
                        total_amino[aa] += val * ratio

            # 오메가 (지방량 기반 근사 배분)
            if f in omega_db:
                o6, o3, _, _ = omega_db[f]
                fat_g = row['지방'] * ratio
                denom = o6 + o3
                omega6_total += fat_g * (o6 / denom)
                omega3_total += fat_g * (o3 / denom)

    # 레시피 저장
    st.subheader("💾 레시피 저장 및 고객 발송")
    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        if recipe_save_list:
            df_recipe = pd.DataFrame(recipe_save_list)
            csv = df_recipe.to_csv(index=False).encode('utf-8-sig')
            st.download_button(label="📥 엑셀(CSV) 파일로 저장하기", data=csv, file_name=f"영양레시피_{weight}kg.csv", mime="text/csv")
    with c_btn2:
        with st.expander("🖨️ PDF로 저장해서 고객에게 보내려면?"):
            st.markdown('''
            1. **`Ctrl + P`** (맥북은 `Command + P`)를 누르세요.
            2. [대상(프린터)]를 **'PDF로 저장'**으로 바꾸세요.
            3. **[저장]** 버튼을 누르면 리포트가 만들어집니다!
            ''')

    st.divider()

    # 탭 구성
    tab1, tab2, tab3 = st.tabs(["📊 AAFCO 영양분석", "🧬 아미노산 분석", "🐟 오메가 6:3 분석"])

    # TAB 1: AAFCO (기존 원본 유지)
    with tab1:
        c1, c2 = st.columns([1, 2])
        with c1:
            st.subheader("⚖️ 식단 비율")
            st.metric("총 급여량", f"{total_grams:.1f} g")
            if total_grams > 0:
                pct_bone = (mass_breakdown['actual_bone'] / total_grams) * 100
                pct_meat = (mass_breakdown['muscle_meat'] / total_grams) * 100
                pct_organ = (mass_breakdown['organ'] / total_grams) * 100
                pct_veggie = (mass_breakdown['veggie'] / total_grams) * 100
                st.write(f"🦴 **뼈 ({pct_bone:.1f}%)** | 목표 12%")
                st.progress(min(pct_bone / 20, 1.0))
                st.write(f"🥩 **살코기 ({pct_meat:.1f}%)** | 목표 60~70%")
                st.progress(min(pct_meat / 100, 1.0))
                st.write(f"🫀 **내장 ({pct_organ:.1f}%)** | 목표 10~25%")
                st.progress(min(pct_organ / 40, 1.0))
                st.write(f"🥦 **야채 ({pct_veggie:.1f}%)** | 목표 5~10%")
                st.progress(min(pct_veggie / 20, 1.0))
        with c2:
            st.subheader("📊 AAFCO 영양 분석")
            res_data = []
            if total_kcal > 0:
                kcal_ratio = (total_kcal / der) * 100
                st.progress(min(kcal_ratio / 100, 1.0), text=f"칼로리 충족률: {kcal_ratio:.1f}%")
                for nutri, std in aafco_standards.items():
                    val_1000 = (total_stats[nutri] / total_kcal) * 1000
                    min_v, max_v = std['min'], std['max']
                    status = "✅ 적합"
                    if val_1000 < min_v:
                        status = f"❌ 부족 (최소 {min_v})"
                    elif max_v and val_1000 > max_v:
                        status = f"⚠️ 과잉 (최대 {max_v})"
                    res_data.append({"영양소": nutri, "현재(1000kcal당)": f"{val_1000:.2f}", "AAFCO 기준": f"{min_v}~{max_v if max_v else ''}", "판정": status})
                res_df = pd.DataFrame(res_data)
                def color_status(val):
                    return f'color: {"green" if "적합" in val else "red" if "부족" in val else "orange"}; font-weight: bold'
                st.dataframe(res_df.style.map(color_status, subset=['판정']), use_container_width=True)
                ca, p = total_stats["칼슘(mg)"], total_stats["인(mg)"]
                if p > 0:
                    ratio_cap = ca / p
                    st.info(f"🦴 **Ca:P 비율 = {ratio_cap:.2f} : 1** (권장 1.1~2 : 1)")

    # TAB 2: 아미노산 분석
    with tab2:
        st.subheader("🧬 필수 아미노산 분석")
        st.caption("출처: 노션 자료(근육육/내장) + USDA FoodData Central(정어리·계란노른자·굴) | 생식(raw) 기준")
        st.caption("⚠️ 뼈류·사슴고기·소폐·그린트라이프·블루베리는 아미노산 데이터 없음 — 집계 제외")

        # NRC 성견 최소기준 (mg/1000kcal, AAFCO 2014 기준)
        nrc_ref_1000kcal = {
            "류신": 1700, "이소류신": 950, "발린": 1230, "메티오닌": 830,
            "리신": 1580, "트레오닌": 1200, "트립토판": 400, "히스티딘": 480,
            "페닐알라닌": 1130, "아르기닌": 1280
        }

        display_aa = ["류신", "이소류신", "발린", "메티오닌", "리신", "트레오닌", "트립토판", "히스티딘", "페닐알라닌", "아르기닌"]
        has_amino = any(amino_name_map.get(f) in amino_db for f in selected if amounts.get(f, 0) > 0)

        if has_amino and total_kcal > 0:
            aa_result = []
            for aa in display_aa:
                total_mg = total_amino.get(aa, 0)
                per_1000kcal = (total_mg / total_kcal * 1000) if total_kcal > 0 else 0
                nrc_min = nrc_ref_1000kcal.get(aa)
                if nrc_min:
                    status = "✅ 충족" if per_1000kcal >= nrc_min else "⚠️ 확인필요"
                else:
                    status = "-"
                aa_result.append({
                    "아미노산": aa,
                    "총량(mg)": f"{total_mg:.0f}",
                    "1000kcal당(mg)": f"{per_1000kcal:.0f}",
                    "NRC 사료기준(mg/1000kcal)": str(nrc_min) if nrc_min else "-",
                    "판정": status
                })
            aa_df = pd.DataFrame(aa_result)
            def color_aa(val):
                if "✅" in str(val): return "color: green; font-weight: bold"
                if "⚠️" in str(val): return "color: orange; font-weight: bold"
                return ""
            st.dataframe(aa_df.style.map(color_aa, subset=["판정"]), use_container_width=True)
            st.info("💡 NRC 기준은 사료(가공) 기준 최솟값입니다. 생식은 열처리 손실 없이 생체이용률이 높아 동일 수치라도 실제 흡수량이 더 많을 수 있습니다.")

            col_m1, col_m2 = st.columns(2)
            with col_m1:
                bcaa = total_amino["류신"] + total_amino["이소류신"] + total_amino["발린"]
                st.metric("💪 BCAA 합계 (류신+이소류신+발린)", f"{bcaa:.0f} mg", help="근육 대사에 두드러지는 분지사슬 아미노산")
            with col_m2:
                saa = total_amino["메티오닌"]
                st.metric("✨ 황아미노산 (메티오닌)", f"{saa:.0f} mg", help="타우린·글루타치온 합성 전구체 / 피모·노령견 핵심")

            with st.expander("📋 재료별 아미노산 상세 보기"):
                detail_rows = []
                for f in selected:
                    if amounts.get(f, 0) > 0:
                        ak = amino_name_map.get(f)
                        if ak and ak in amino_db:
                            row_d = {"재료명": f, "급여량(g)": amounts[f]}
                            row_d.update({k: f"{v}mg" for k, v in amino_db[ak].items() if k in display_aa})
                            detail_rows.append(row_d)
                        else:
                            detail_rows.append({"재료명": f, "급여량(g)": amounts[f], "류신": "데이터없음"})
                if detail_rows:
                    st.dataframe(pd.DataFrame(detail_rows), use_container_width=True)
        else:
            st.warning("선택한 재료 중 아미노산 데이터가 있는 항목이 없습니다. 근육육 또는 내장을 추가해 주세요.")

    # TAB 3: 오메가 6:3 분석
    with tab3:
        st.subheader("🐟 오메가 6:3 비율 분석")
        st.caption("출처: 노션 자료 기반 비율 근사치. 사육방식·개체에 따라 실제 비율은 달라질 수 있습니다.")

        if omega6_total + omega3_total > 0:
            ratio_omega = omega6_total / omega3_total if omega3_total > 0 else 999
            co1, co2, co3 = st.columns(3)
            with co1:
                st.metric("오메가-6 추정량", f"{omega6_total:.2f} g")
            with co2:
                st.metric("오메가-3 추정량", f"{omega3_total:.2f} g")
            with co3:
                st.metric("오메가 6:3 비율", f"{ratio_omega:.1f} : 1")

            if ratio_omega <= 5:
                st.success(f"✅ {ratio_omega:.1f}:1 — 항염증 범위. 진화적 식단에 가깝습니다.")
            elif ratio_omega <= 10:
                st.warning(f"⚠️ {ratio_omega:.1f}:1 — 허용범위이나 개선 권장. 정어리·말고기·목초 소 추가를 고려하세요.")
            else:
                st.error(f"❌ {ratio_omega:.1f}:1 — 오메가-6 과잉. 정어리 또는 오메가-3 급원을 추가하세요.")

            omega_detail = []
            for f in selected:
                if amounts.get(f, 0) > 0 and f in omega_db:
                    o6, o3, ratio_str, note = omega_db[f]
                    omega_detail.append({"재료명": f, "급여량(g)": amounts[f], "오메가 6:3 비율": ratio_str, "비고": note})
            if omega_detail:
                st.dataframe(pd.DataFrame(omega_detail), use_container_width=True)
        else:
            st.info("오메가 데이터가 있는 재료를 선택하면 분석 결과가 나타납니다.")

        st.info("💡 정어리(생)·말고기·목초 소고기·야생 사슴이 오메가-3 비율 개선에 가장 효과적입니다.\n\n⚠️ 해바라기유 등 식물성 오메가-6 급원은 생식 식단에서 제외하는 것을 권장합니다.")

else:
    st.info("재료를 선택하면 분석 결과가 나타납니다.")
