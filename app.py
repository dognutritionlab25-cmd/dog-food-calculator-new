from nutrition_core import basic_judgments
from nutrition_core import energy_requirements
import streamlit as st
import pandas as pd
from nutrition_ui import (PRECOOKED_ITEMS, FRUIT_RAW_ITEMS, PREPARED_PUREE_ITEMS, WEIGHT_BASIS_NOTE, weight_label,
    render_data_warnings, render_coverage, render_scope, render_cooking_policy, nutrient_value_text)

st.set_page_config(page_title="반려견 영양 연구소 계산기 v6.2", layout="wide")
st.title("🐶 반려견 영양 연구소 [영양 계산기 v6.2]")
st.info("💡 전문가용 맞춤형 영양 컨설팅 & 레시피 분석 시스템 | v6.2: 국가표준식품성분DB 기준 영양수치 최종 반영(칼슘·인·비타민D/E/A 등 재검증), 정어리 3종 분리(생식용/뼈제외 화식용/뼈포함 통조림 화식용) 적용")

# Shared data and deterministic engine (no copied nutrition data).
from nutrition_core import calculate, make_request, standards, catalog_data, retention
from nutrition_core import create_snapshot, dumps_snapshot
_catalog = catalog_data()
aafco_standards = standards("calculator")
db_data = _catalog["db_data"]
amino_db = _catalog["amino_db"]
amino_name_map = _catalog["amino_name_map"]
omega_db = _catalog["omega_db"]

@st.cache_data
def load_food_df():
    return pd.DataFrame(db_data)

food_df = load_food_df()

# 반드시 익혀서 급여해야 하는 재료 — DB 수치 자체가 '익힌 상태' 기준이므로
# 화식 조리 보존율(중복 손실 계산)을 적용하지 않고, 입력값도 익힌 무게 그대로 사용
# PRECOOKED_ITEMS comes from the shared catalog via nutrition_ui.


# Preserve existing coefficient values, including unresolved effective O3 behavior.
RETENTION = _catalog["RETENTION"]
COOKING_YIELD = _catalog["COOKING_YIELD"]
get_retention_factor = retention

# ── 메인 탭: 생식 / 화식 ────────────────────────────────────────────────────
tab_raw, tab_cooked = st.tabs(["🥩 생식", "🍲 화식"])

# ════════════════════════════════════════════════════════════════════════════
# 생식 탭
# ════════════════════════════════════════════════════════════════════════════
with tab_raw:
    # ── 생식 탭 ──────────────────────────────────────────────────────────────
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
        rer, der = energy_requirements(weight, activity)
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

    # ── 켈프 (요오드 직접 입력) ──────────────────────────────────────────────────
    st.markdown("#### 🌿 켈프 (요오드 보충)")
    use_kelp = st.checkbox("켈프 급여", key="use_kelp_raw")
    kelp_iodine_mcg = 0.0
    if use_kelp:
        kelp_iodine_mcg = st.number_input(
            "오늘 급여한 켈프 요오드 총량 (mcg)", 0.0, 5000.0, 150.0, step=10.0, key="kelp_iodine_raw",
            help="캡슐 제품: 1알당 요오드 함량(제품 라벨) × 급여한 알 수. 파우더 제품: 급여한 g × 라벨의 g당 mcg."
        )
        st.caption(
            "🌿 **켈프 요오드 안내**: 요오드 함량은 제품·종·산지에 따라 편차가 매우 큽니다 "
            "(그램당 5~80mcg 이상까지 다양). g으로 계량해서 추정하지 말고, "
            "반드시 제품 라벨에 적힌 요오드 함량을 확인해서 위에 mcg로 직접 입력해주세요. "
            f"(NRC 권장 220mcg/1000kcal, AAFCO·NRC 안전상한 2750mcg/1000kcal)"
        )

    # Raw calculation stays inside its tab; it never stops the cooked tab.
    calc_btn = st.button("🔍 영양 분석 계산하기", type="primary", use_container_width=True) if selected else False
    if selected and (calc_btn or st.session_state.get("calc_done", False)):
        if calc_btn:
            st.session_state["calc_done"] = True
            st.session_state["calc_selected"] = list(selected)
            st.session_state["calc_amounts"] = dict(amounts)
            st.session_state["calc_kelp_iodine"] = kelp_iodine_mcg


        # Every displayed aggregate/detail uses the same current input after first calculation.
        _selected = list(selected)
        _amounts = dict(amounts)
        _kelp_iodine = kelp_iodine_mcg
        raw_request = make_request(_amounts, weight=weight, activity=activity, kelp=_kelp_iodine,
                                   supplements={"kelp_enabled": use_kelp, "iodine_mcg": _kelp_iodine})
        _raw_result = calculate(raw_request, "calculator")
        render_data_warnings(st, _raw_result)
        render_scope(st, "calculator")
        total_grams = _raw_result["input_grams"]
        mass_breakdown = _raw_result["mass"]
        total_stats = _raw_result["nutrients"]
        total_kcal = _raw_result["kcal"]
        total_amino = _raw_result["amino"]
        omega6_total = _raw_result["omega6"]
        omega3_total = _raw_result["omega3_food"]
        recipe_save_list = [{"재료명": f, "급여량(g)": g} for f, g in _amounts.items() if g > 0]

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
                    cap_ratio = _raw_result["ratios"]["ca_p"] if p > 0 else 0
                    cap_ok = 1.1 <= cap_ratio <= 2.0

                    res_data = []
                    for nutri, std in aafco_standards.items():
                        val_1000 = _raw_result["per_1000kcal"][nutri]
                        min_v, max_v = std['min'], std['max']
                        status = "✅ 적합"
                        if basic_judgments(_raw_result, "calculator")[nutri] == "unavailable":
                            status = "⚪ 판정 보류 (미등록 포함)"
                        elif basic_judgments(_raw_result, "calculator")[nutri] == "low":
                            status = f"❌ 부족 (최소 {min_v})"
                        elif basic_judgments(_raw_result, "calculator")[nutri] == "high":
                            status = f"⚠️ 과잉 (최대 {max_v})"
                        # 칼슘은 절대량이 적합해도 Ca:P 범위 벗어나면 불균형으로 표시
                        if nutri == "칼슘(mg)" and status == "✅ 적합" and not cap_ok:
                            status = f"⚠️ Ca:P 불균형 ({cap_ratio:.2f}:1, 권장 1.1~2:1)"
                        res_data.append({"영양소":nutri,"현재(1000kcal당)":nutrient_value_text(_raw_result, nutri),"AAFCO 기준":f"{min_v}~{max_v if max_v else ''}","판정":status})
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

                    # 아몬드 경고
                    if any("아몬드" in f for f in selected):
                        st.warning(
                            "⚠️ **아몬드 가루 주의**: 비타민E 공급 목적으로 소량(5~10g/일) 사용 권장. "
                            "지방 함량이 높아(50g/100g) 과량 급여 시 소화 장애 및 췌장 부담 위험이 있습니다."
                        )

                    # 칼슘출처 표시
                    est_items = []
                    for f in selected:
                        rows = food_df[food_df['재료명'] == f]
                        if not rows.empty:
                            row_f = rows.iloc[0]
                            src = row_f['칼슘출처'] if '칼슘출처' in row_f.index else ''
                            if isinstance(src, str) and src.startswith('est') and row_f['category'] == 'bone':
                                est_items.append(f)

                    if est_items:
                        st.caption(
                            f"⚠️ **칼슘 추정값 사용 재료**: {', '.join(est_items)} — "
                            "Segal 실측값이 없어 유사 가금류/포유류 뼈 평균 밀도로 추정. "
                            "AAFCO 칼슘 판정은 참고값으로만 활용하세요."
                        )

        # TAB 2 ─ 아미노산
        with tab2:
            st.subheader("🧬 필수 아미노산 분석")
            st.caption("출처: 노션 자료(근육육/내장) + USDA FoodData Central | 생식(raw) 기준")
            render_coverage(st, _raw_result, "amino")
            st.caption("주 표는 기존 성견 기준의 10개 표시 항목입니다. BCAA·Phe+Trp도 등록분 합계입니다.")
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
                st.caption("현재 표는 기존 성견 기준과 등록분을 비교합니다. 실제 흡수량을 별도로 계산하지 않습니다.")
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
                    bcaa_total=_raw_result["bcaa"]
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
                    aaa=_raw_result["phenylalanine_plus_tryptophan"]; aaa1k=aaa/total_kcal*1000
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
                            if ak and ak in amino_db: row_d.update({k:f"{v}mg/100g" for k,v in amino_db[ak].items() if k in display_aa})
                            else: row_d["류신"]="데이터없음"
                            detail.append(row_d)
                    st.dataframe(pd.DataFrame(detail),use_container_width=True)
            else:
                st.warning("아미노산 데이터가 있는 재료를 추가하세요 (근육육 / 내장).")

        # TAB 3 ─ 오메가
        with tab3:
            st.subheader("🐟 오메가 6:3 비율 분석")
            st.caption("기존 지방산 DB 등록분 기준이며 식품별 O3 집계 범위는 출처 메모에 따라 다릅니다.")
            has_omega_data = render_coverage(st, _raw_result, "omega")

            # EPA·DHA 영양제 직접 입력
            supp_o3 = 0.0
            epa_g = 0.0
            dha_g = 0.0
            with st.expander("➕ 오메가3 영양제 (EPA·DHA) 추가 입력", expanded=False):
                st.caption("오메가3 오일이나 영양제를 급여하는 경우 EPA와 DHA를 입력하면 비율 계산에 자동 반영됩니다.")
                epa_col, dha_col, unit_col = st.columns(3)
                with unit_col:
                    omega_unit = st.radio("단위", ["mg", "g"], horizontal=True, key="omega_unit")
                with epa_col:
                    epa_input = st.number_input("EPA", min_value=0.0, step=1.0 if omega_unit=="mg" else 0.01, key="epa_input")
                with dha_col:
                    dha_input = st.number_input("DHA", min_value=0.0, step=1.0 if omega_unit=="mg" else 0.01, key="dha_input")
                epa_g = epa_input / 1000 if omega_unit == "mg" else epa_input
                dha_g = dha_input / 1000 if omega_unit == "mg" else dha_input
                supp_o3 = epa_g + dha_g
                if supp_o3 > 0:
                    st.caption(f"영양제 EPA+DHA 합계: {supp_o3*1000:.1f}mg ({supp_o3:.3f}g) → 오메가3 총량에 자동 합산")

            raw_request["supplement_totals"].update(epa=epa_input, dha=dha_input, omega_unit=omega_unit)
            raw_request["supplement_inputs"]["omega3"] = {"epa": epa_input, "dha": dha_input, "unit": omega_unit}
            _raw_result = calculate(raw_request, "calculator")
            omega3_final = _raw_result["omega3"]

            if omega6_total + omega3_final > 0:
                ratio_omega = _raw_result["ratios"]["omega6_3"] if omega3_final > 0 else float("inf")
                co1,co2,co3=st.columns(3)
                with co1: st.metric("오메가-6 등록분", f"{omega6_total:.2f} g" if has_omega_data else "미등록")
                with co2:
                    delta_str = f"+{supp_o3*1000:.0f}mg 영양제 포함" if supp_o3 > 0 else None
                    st.metric("오메가-3 등록분 + 보충",f"{omega3_final:.2f} g", delta=delta_str)
                with co3: st.metric("오메가 6:3 비율", f"{ratio_omega:.1f} : 1" if omega3_final > 0 and has_omega_data else "계산 불가")
                if not has_omega_data: st.info("식품 오메가 데이터 미등록으로 식단 비율을 표시할 수 없습니다. 보충량만 반영되었습니다.")
                elif omega3_final <= 0: st.info("오메가3 합계가 0이어서 비율을 계산할 수 없습니다.")
                elif ratio_omega<=5:   st.success(f"✅ {ratio_omega:.1f}:1 — 항염증 범위.")
                elif ratio_omega<=10: st.warning(f"⚠️ {ratio_omega:.1f}:1 — 허용범위. 정어리·말고기 추가 권장.")
                else:                 st.error(f"❌ {ratio_omega:.1f}:1 — 오메가-6 과잉. 정어리를 추가하세요.")
                od=[]
                for f in selected:
                    if amounts.get(f,0)>0 and f in omega_db:
                        o6_per100,o3_per100,ratio_str,note=omega_db[f]; g=amounts[f]
                        od.append({"재료명":f,"급여량(g)":g,"O6/100g(g)":f"{o6_per100:.3f}","O3/100g(g)":f"{o3_per100:.3f}","해당량 O6(g)":f"{o6_per100*g/100:.3f}","해당량 O3(g)":f"{o3_per100*g/100:.3f}","비율":ratio_str,"비고":note})
                if od: st.dataframe(pd.DataFrame(od),use_container_width=True)
                if supp_o3 > 0:
                    st.caption(f"📌 영양제 EPA {epa_g*1000:.0f}mg + DHA {dha_g*1000:.0f}mg = {supp_o3*1000:.0f}mg 포함한 최종 비율")
            else:
                st.info("오메가 데이터가 있는 재료를 선택하면 분석 결과가 나타납니다.")
            st.info("💡 정어리(생)·말고기·목초 소고기·야생 사슴이 오메가-3 비율 개선에 가장 효과적입니다.")

        # TAB 4 ─ 아연:구리 비율
        with tab4:
            st.subheader("🔬 아연:구리 비율 분석")
            st.caption("✨ 생식의 미네랄 균형을 확인하세요")
            with st.expander("📋 현재 판정에 적용하는 기준"):
                standards_df = pd.DataFrame([{"프로필": "calculator", "영양소": n, "최소(1000kcal당)": v["min"], "최대(1000kcal당)": v["max"]} for n, v in aafco_standards.items() if n in ("아연(mg)", "구리(mg)")])
                st.dataframe(standards_df, use_container_width=True)
                st.caption("기본 영양표와 같은 기준입니다. Zn:Cu 비율 평가는 별도의 기존 비율 범위를 사용합니다.")
            st.markdown("---")
            copper_value = total_stats["구리(mg)"] / total_kcal * 1000 if total_kcal > 0 else 0
            zinc_value   = total_stats["아연(mg)"] / total_kcal * 1000 if total_kcal > 0 else 0
            col1,col2,col3=st.columns(3)
            with col1:
                st.markdown("#### 구리")
                st.metric("현재 값",f"{copper_value:.2f} mg",delta=f"{copper_value-1.83:.2f}",delta_color="normal" if copper_value>=1.83 else "inverse")
                st.caption(f"calculator 최소: {aafco_standards['구리(mg)']['min']} mg/1000kcal")
            with col2:
                st.markdown("#### 아연")
                st.metric("현재 값",f"{zinc_value:.2f} mg",delta=f"{zinc_value-20:.2f}",delta_color="normal" if zinc_value>=15 else "inverse")
                st.caption(f"calculator 최소: {aafco_standards['아연(mg)']['min']} mg/1000kcal | 색상은 기존 표시 규칙 유지")
            with col3:
                st.markdown("#### 아연:구리 비율")
                if copper_value > 0:
                    ratio=_raw_result["ratios"]["zn_cu"]
                    if 5<=ratio<=12:   dt,dc="생식 기준 이상적","normal"
                    elif 12<ratio<=16: dt,dc="약간 높음","off"
                    else:              dt,dc="범위 벗어남","inverse"
                    st.metric("현재 비율",f"{ratio:.1f}:1",delta=dt,delta_color=dc)
                    st.caption("생식 권장: 5:1 ~ 12:1")
                else:
                    st.metric("현재 비율","계산 불가")
            st.markdown("---")
            if copper_value > 0:
                ratio=_raw_result["ratios"]["zn_cu"]
                st.markdown("### 🎯 평가 결과 (생식 기준)")
                if 5<=ratio<=12:
                    st.success(f"✅ 기존 생식 비율 범위 안입니다 ({ratio:.1f}:1). 아연·구리 절대량은 기본 영양표에서 별도로 확인하세요.")
                elif 12<ratio<=16:
                    st.info(f"ℹ️ 기존 생식 비율 허용 구간입니다 ({ratio:.1f}:1). 아연·구리 절대량은 기본 영양표에서 별도로 확인하세요.")
                elif ratio>16:
                    st.warning(f"⚠️ 기존 생식 비율 범위보다 높습니다 ({ratio:.1f}:1). 아연·구리 절대량은 기본 영양표에서 별도로 확인하세요.")
                elif 3<=ratio<5:
                    st.warning(f"⚠️ 기존 생식 비율 범위보다 낮습니다 ({ratio:.1f}:1). 아연·구리 절대량은 기본 영양표에서 별도로 확인하세요.")
                else:
                    st.error(f"❌ 기존 생식 비율 범위보다 크게 낮습니다 ({ratio:.1f}:1). 아연·구리 절대량은 기본 영양표에서 별도로 확인하세요.")
            else:
                st.info("ℹ️ 재료를 추가하여 구리와 아연 값을 확인하세요.")

        raw_snapshot = create_snapshot(raw_request, _raw_result, raw_request)
        st.download_button("📥 원본 입력·계산 결과 저장 (JSON)", dumps_snapshot(raw_snapshot),
                           "raw_nutrition_snapshot.json", "application/json", key="raw_snapshot_download")

    else:
        st.info("재료를 선택하면 분석 결과가 나타납니다.")

    st.markdown("---")
    st.caption("반려견영양연구소 | 생식 계산기 v5.3")

# ════════════════════════════════════════════════════════════════════════════
# 화식 탭
# ════════════════════════════════════════════════════════════════════════════
with tab_cooked:
    st.caption(
        "⚠️ **화식 계산 안내**: 조리 과정에서 발생하는 수분 변화와 일부 영양소 손실을 반영한 **추정치**입니다. "
        "실제 보존율은 재료의 종류, 조리 시간, 온도, 물 사용 여부에 따라 달라질 수 있습니다."
    )

    # ── 강아지 정보 ──────────────────────────────────────────────────────────
    cw1, cw2 = st.columns([1, 2])
    with cw1:
        st.subheader("🐶 강아지 정보")
        c_weight = st.number_input("몸무게 (kg)", 0.1, 60.0, 3.0, step=0.1, key="c_weight")
        c_der_options = {
            "3.0: 성장기 강아지 (퍼피)": 3.0,
            "2.0: 체중 증가 필요": 2.0,
            "2.0: 매우 활동적인 성견": 2.0,
            "1.8: 비중성화 성견 · 보통 활동량": 1.8,
            "1.6: 중성화 성견 · 보통 활동량 ⭐": 1.6,
            "1.4: 중성화 성견 · 낮은 활동량": 1.4,
            "1.4: 노견 · 활동적": 1.4,
            "1.2: 노견 · 보통": 1.2,
            "1.0: 노견 · 거의 안 움직임": 1.0,
            "1.0: 다이어트": 1.0,
        }
        c_sel_label = st.selectbox("강아지 상태", list(c_der_options.keys()), index=4, key="c_der_sel")
        c_activity = c_der_options[c_sel_label]
        c_rer, c_der = energy_requirements(c_weight, c_activity)
        st.metric("하루 목표 칼로리 (DER)", f"{c_der:.1f} kcal")

    with cw2:
        st.subheader("🍲 조리 방법 선택")
        cooking_method = st.radio(
            "조리 방법",
            ["저온찜", "삶기", "볶기/구이", "압력조리"],
            horizontal=True,
            key="cooking_method"
        )
        render_cooking_policy(st, cooking_method)

    st.divider()

    # ── 재료 선택 (뼈고기 제외) ───────────────────────────────────────────────
    st.subheader("🥩 재료 선택 (화식)")
    cooked_foods = food_df[food_df['category'] != 'bone']['재료명'].tolist()
    c_selected = st.multiselect("재료를 선택하세요 (뼈고기 제외)", cooked_foods, key="c_selected")
    st.caption("💡 화식에서는 뼈를 익히면 안 됩니다. 칼슘은 아래 보충제로 공급하세요.")
    st.caption(WEIGHT_BASIS_NOTE)

    # ── 급여량 + 조리 수율 ────────────────────────────────────────────────────
    c_amounts_raw = {}   # 생고기 입력값
    c_amounts_cooked = {}  # 조리 후 실제 계산에 쓸 값
    c_actual_weights = {}

    if c_selected:
        st.markdown("#### 재료 입력 중량 및 조리 후 예상 무게")
        for f in c_selected:
            if f in FRUIT_RAW_ITEMS or f in PREPARED_PUREE_ITEMS:
                raw_g = st.number_input(weight_label(f), 0, 1000, 50, step=5, key=f"craw_{f}")
                c_amounts_raw[f] = raw_g
                c_amounts_cooked[f] = raw_g
                st.caption("생과일 급여량 그대로 사용 (조리 보정 없음)" if f in FRUIT_RAW_ITEMS
                           else "완성 퓨레 급여량 그대로 사용 (추가 수율·실측 조리 중량 없음)")
                continue
            row_f = food_df[food_df['재료명'] == f].iloc[0]
            cat_f = row_f['category']
            yield_key = cat_f
            yield_ratio = COOKING_YIELD[cooking_method].get(yield_key, 0.85)

            fc1, fc2, fc3, fc4 = st.columns([3, 2, 2, 2])
            is_precooked = f in PRECOOKED_ITEMS
            with fc1:
                raw_label = weight_label(f)
                raw_g = st.number_input(raw_label, 0, 1000, 50, step=5, key=f"craw_{f}")
                c_amounts_raw[f] = raw_g
            with fc2:
                if is_precooked:
                    auto_cooked = raw_g  # 이미 익힌 상태 — 추가 수율 손실 없음
                    st.caption("이미 익힌 상태 그대로 사용")
                else:
                    auto_cooked = round(raw_g * yield_ratio)
                    st.metric("예상 조리 후", f"{auto_cooked}g", delta=f"수율 {int(yield_ratio*100)}%")
            with fc3:
                st.caption("☑ 조리 후 실제 무게를 알면 체크해서 입력하세요.")
                use_actual = st.checkbox("실제 무게 직접 입력", key=f"cactual_chk_{f}", disabled=is_precooked)
            with fc4:
                if use_actual:
                    actual_g = st.number_input("실제 조리 후 (g)", 0, 1000, auto_cooked, step=1, key=f"cactual_{f}")
                    c_amounts_cooked[f] = actual_g
                    c_actual_weights[f] = actual_g
                else:
                    c_amounts_cooked[f] = raw_g  # 영양 계산은 생고기 기준
                    c_actual_weights[f] = auto_cooked

    # ── 칼슘 보충제 ──────────────────────────────────────────────────────────
    st.divider()
    st.subheader("🦴 칼슘 보충")
    ca_sup1, ca_sup2, ca_sup3 = st.columns(3)

    with ca_sup1:
        use_eggshell = st.checkbox("난각가루 (달걀껍질 가루)", key="use_eggshell")
        eggshell_g = 0.0
        if use_eggshell:
            eggshell_g = st.number_input("난각가루 급여량 (g)", 0.0, 10.0, 0.5, step=0.1, key="eggshell_g")
            st.caption("기본값: 380mg Ca/g | 직접 입력 가능")
            eggshell_ca_per_g = st.number_input("난각가루 Ca 함량 (mg/g)", 100, 600, 380, step=10, key="eggshell_ca")
        else:
            eggshell_ca_per_g = 380

    with ca_sup2:
        use_ca_sup = st.checkbox("칼슘 보충제", key="use_ca_sup")
        ca_sup_g = 0.0
        if use_ca_sup:
            ca_sup_g = st.number_input("보충제 급여량 (g)", 0.0, 10.0, 0.5, step=0.1, key="ca_sup_g")
            ca_sup_mg_per_g = st.number_input("보충제 Ca 함량 (mg/g) — 제품 라벨 확인", 50, 600, 400, step=10, key="ca_sup_mgpg")
        else:
            ca_sup_mg_per_g = 400

    with ca_sup3:
        total_ca_supplement = 0.0
        if use_eggshell:
            total_ca_supplement += eggshell_g * eggshell_ca_per_g
        if use_ca_sup:
            total_ca_supplement += ca_sup_g * ca_sup_mg_per_g
        st.metric("칼슘 보충제 합계", f"{total_ca_supplement:.0f} mg")

    # ── 계산 ────────────────────────────────────────────────────────────────
    if c_selected:
        st.divider()
        cooked_request = make_request(c_amounts_raw, cooked=True, method=cooking_method,
            weight=c_weight, activity=c_activity, calcium=total_ca_supplement,
            actual_weights=c_actual_weights,
            supplements={"eggshell_enabled": use_eggshell, "eggshell_g": eggshell_g,
                         "eggshell_ca_mg_per_g": eggshell_ca_per_g, "calcium_enabled": use_ca_sup,
                         "calcium_g": ca_sup_g, "calcium_mg_per_g": ca_sup_mg_per_g},
            original_fields={"raw_amounts": dict(c_amounts_raw), "actual_weight_selection": {
                f: bool(st.session_state.get("cactual_chk_" + f, False)) for f in c_selected}})
        _cooked_result = calculate(cooked_request, "calculator")
        render_data_warnings(st, _cooked_result)
        render_scope(st, "calculator")
        c_total_grams_raw = _cooked_result["input_grams"]
        c_total_grams_cooked = _cooked_result["cooked_grams"]
        c_mass_breakdown = _cooked_result["mass"]
        c_total_stats = _cooked_result["nutrients"]
        c_total_kcal = _cooked_result["kcal"]
        c_omega6, c_omega3 = _cooked_result["omega6"], _cooked_result["omega3"]
        c_total_amino = _cooked_result["amino"]

        # ── 결과 표시 ────────────────────────────────────────────────────────
        ctab1, ctab2, ctab3, ctab4 = st.tabs(["📊 AAFCO 영양분석", "🐟 오메가 분석", "🧬 아미노산 분석", "🔬 아연:구리 비율"])

        with ctab1:
            rc1, rc2 = st.columns([1, 2])
            with rc1:
                st.subheader("⚖️ 식단 비율")
                st.metric("재료 입력 총량", f"{c_total_grams_raw:.0f}g")
                st.metric("조리 후 총량 (실측 입력 또는 예상)", f"{c_total_grams_cooked:.0f}g")
                if c_total_grams_raw > 0:
                    pm = c_mass_breakdown['muscle_meat'] / c_total_grams_raw * 100
                    po = c_mass_breakdown['organ']       / c_total_grams_raw * 100
                    pv = c_mass_breakdown['veggie']      / c_total_grams_raw * 100
                    st.write(f"🥩 **살코기 ({pm:.1f}%)** | 목표 60~70%"); st.progress(min(pm/100,1.0))
                    st.write(f"🫀 **내장 ({po:.1f}%)** | 목표 10~25%");   st.progress(min(po/40,1.0))
                    st.write(f"🥦 **야채 ({pv:.1f}%)** | 목표 5~10%");   st.progress(min(pv/20,1.0))
                    st.caption("🦴 뼈 비율: 칼슘 보충제로 대체")

            with rc2:
                st.subheader("📊 AAFCO 영양 분석")
                if c_total_kcal > 0:
                    kcal_pct = (c_total_kcal / c_der) * 100
                    kc1, kc2, kc3 = st.columns(3)
                    with kc1: st.metric("🔥 섭취 칼로리", f"{c_total_kcal:.0f} kcal")
                    with kc2: st.metric("🎯 목표 칼로리", f"{c_der:.0f} kcal")
                    with kc3: st.metric("📈 충족률", f"{kcal_pct:.1f}%", delta=f"{c_total_kcal-c_der:+.0f} kcal")
                    st.progress(min(kcal_pct/100, 1.0), text=f"칼로리 충족률: {kcal_pct:.1f}%")
                    st.divider()

                    # AAFCO 판정
                    ca = c_total_stats["칼슘(mg)"]
                    p  = c_total_stats["인(mg)"]
                    cap_ratio = _cooked_result["ratios"]["ca_p"] if p > 0 else 0
                    cap_ok = 1.1 <= cap_ratio <= 2.0

                    res_data = []
                    for nutri, std in aafco_standards.items():
                        val_1000 = _cooked_result["per_1000kcal"][nutri]
                        min_v, max_v = std['min'], std['max']
                        if basic_judgments(_cooked_result, "calculator")[nutri] == "unavailable":
                            status = "⚪ 판정 보류 (미등록 포함)"
                        elif basic_judgments(_cooked_result, "calculator")[nutri] == "low":
                            status = f"❌ 부족 (최소 {min_v})"
                        elif basic_judgments(_cooked_result, "calculator")[nutri] == "high":
                            status = f"⚠️ 과잉 (최대 {max_v})"
                        else:
                            status = "✅ 적합"
                        if nutri == "칼슘(mg)" and status == "✅ 적합" and not cap_ok:
                            status = f"⚠️ Ca:P 불균형 ({cap_ratio:.2f}:1, 권장 1.1~2:1)"
                        res_data.append({
                            "영양소": nutri,
                            "현재(1000kcal당)": nutrient_value_text(_cooked_result, nutri),
                            "AAFCO 기준": f"{min_v}~{max_v if max_v else ''}",
                            "판정": status
                        })
                    res_df = pd.DataFrame(res_data)
                    def c_color(val):
                        return f'color:{"green" if "적합" in val else "red" if "부족" in val else "orange"};font-weight:bold'
                    st.dataframe(res_df.style.map(c_color, subset=['판정']), use_container_width=True)

                    if p > 0:
                        if cap_ok:
                            st.info(f"🦴 **Ca:P 비율 = {cap_ratio:.2f} : 1** ✅ (권장 1.1~2 : 1)")
                        else:
                            st.warning(f"🦴 **Ca:P 비율 = {cap_ratio:.2f} : 1** ⚠️ 권장 범위 벗어남 — 칼슘 보충량을 조정하세요.")

                    st.caption(f"📌 조리법: **{cooking_method}** | 보존율 적용 (야채/퓨레 제외) | 칼슘 보충제 {total_ca_supplement:.0f}mg 포함")

        with ctab2:
            st.subheader("🐟 오메가 6:3 비율")
            has_c_omega = render_coverage(st, _cooked_result, "omega")
            if c_omega3 > 0 and has_c_omega:
                ratio_str = f"{_cooked_result['ratios']['omega6_3']:.1f} : 1"
                st.metric("오메가 6:3 비율", ratio_str)
                if _cooked_result['ratios']['omega6_3'] <= 5:
                    st.success(f"✅ {ratio_str} — 이상적 범위 (목표 ≤5:1)")
                elif _cooked_result['ratios']['omega6_3'] <= 10:
                    st.warning(f"⚠️ {ratio_str} — 오메가3 보충 권장")
                else:
                    st.error(f"❌ {ratio_str} — 오메가3 심각 부족")
                st.caption(f"등록분 오메가6: {c_omega6:.2f}g (보존율 미적용) | 오메가3: {c_omega3:.2f}g (현재 실효 보존율 적용, veggie·익힌 굴/홍합 제외)")
            else:
                st.info("오메가3 데이터가 있는 재료를 선택하면 분석됩니다.")

        with ctab3:
            st.subheader("🧬 아미노산 분석 (필수 아미노산)")
            st.caption(f"조리법: {cooking_method} | 단백질 보존율 적용 (veggie·익힌 굴/홍합 제외). 티로신 포함 기존 11개 항목을 표시합니다.")
            render_coverage(st, _cooked_result, "amino")
            has_amino = any(v > 0 for v in c_total_amino.values())
            if has_amino and c_total_kcal > 0:
                aa_display = []
                for aa, val in c_total_amino.items():
                    per1000 = val / c_total_kcal * 1000
                    aa_display.append({"아미노산": aa, "총량(mg)": f"{val:.0f}", "1000kcal당(mg)": f"{per1000:.0f}"})
                st.dataframe(pd.DataFrame(aa_display), use_container_width=True, hide_index=True)
            else:
                st.info("아미노산 데이터가 있는 재료(닭가슴살, 소고기 등)를 선택하면 분석됩니다.")

        with ctab4:
            st.subheader("🔬 아연 : 구리 비율")
            st.caption("비율 평가는 아연·구리 절대량의 부족/과잉 판정과 다릅니다. 기본 영양표를 함께 확인하세요.")
            c_zinc = c_total_stats.get("아연(mg)", 0)
            c_copper = c_total_stats.get("구리(mg)", 0)
            if c_copper > 0:
                ratio = _cooked_result["ratios"]["zn_cu"]
                st.metric("아연:구리 비율", f"{ratio:.1f} : 1")
                st.caption(f"아연: {c_zinc:.2f}mg | 구리: {c_copper:.2f}mg (조리 보존율 적용)")
                if ratio < 8:
                    st.error(f"❌ 기존 화식 비율 범위보다 낮습니다 ({ratio:.1f}:1). 비율만으로 아연 부족을 단정할 수 없습니다.")
                elif ratio <= 15:
                    st.success(f"✅ **적정 범위** ({ratio:.1f}:1) — 권장 8~15:1")
                elif ratio <= 20:
                    st.warning(f"⚠️ 기존 화식 비율 범위보다 높습니다 ({ratio:.1f}:1). 아연·구리 절대량을 함께 확인하세요.")
                else:
                    st.error(f"❌ 기존 화식 비율 범위보다 크게 높습니다 ({ratio:.1f}:1). 비율만으로 아연 과잉을 단정할 수 없습니다.")
            else:
                st.info("구리 함유 재료(간, 굴 등)를 선택하면 분석됩니다.")

        cooked_snapshot = create_snapshot(cooked_request, _cooked_result, cooked_request)
        st.download_button("📥 화식 원본·계산 결과 저장 (JSON)", dumps_snapshot(cooked_snapshot),
                           "cooked_nutrition_snapshot.json", "application/json", key="cooked_snapshot_download")
