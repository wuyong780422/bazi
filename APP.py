# ==========================================================
# 真命盘专业版 —— 固定顶部标题+全功能原版+手机端历法一行优化版
# 本地/云端通用，不修改数据库逻辑，不破坏现有功能 运行命令>> streamlit run APP.py
# ==========================================================
import streamlit as st
import sqlite3
import os
import sys
from datetime import datetime

# ===================== 资源路径（和APP0完全一样） =====================
def resource_path(relative_path: str) -> str:
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ===================== 命理常量（完全不变） =====================
SHICHEN_DETAIL = [
    "子时 23:00-01:00", "丑时 01:00-03:00", "寅时 03:00-05:00", "卯时 05:00-07:00",
    "辰时 07:00-09:00", "巳时 09:00-11:00", "午时 11:00-13:00", "未时 13:00-15:00",
    "申时 15:00-17:00", "酉时 17:00-19:00", "戌时 19:00-21:00", "亥时 21:00-23:00"
]
SHICHEN_TIME = [s.split(" ")[0] for s in SHICHEN_DETAIL]
TIANGAN_WUXING = {"甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土", "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"}
YUELING_WUXING = {"寅": "木", "卯": "木", "辰": "土", "巳": "火", "午": "火", "未": "土", "申": "金", "酉": "金", "戌": "土", "亥": "水", "子": "水", "丑": "土"}
NAYIN_TABLE = {
    "甲子": "海中金", "乙丑": "海中金", "丙寅": "炉中火", "丁卯": "炉中火", "戊辰": "大林木", "己巳": "大林木",
    "庚午": "路旁土", "辛未": "路旁土", "壬申": "剑锋金", "癸酉": "剑锋金", "甲戌": "山头火", "乙亥": "山头火",
    "丙子": "涧下水", "丁丑": "涧下水", "戊寅": "城头土", "己卯": "城头土", "庚辰": "白蜡金", "辛巳": "白蜡金",
    "壬午": "杨柳木", "癸未": "杨柳木", "甲申": "泉中水", "乙酉": "泉中水", "丙戌": "屋上土", "丁亥": "屋上土",
    "戊子": "霹雳火", "己丑": "霹雳火", "庚寅": "松柏木", "辛卯": "松柏木", "壬辰": "长流水", "癸巳": "长流水",
    "甲午": "沙中金", "乙未": "沙中金", "丙申": "山下火", "丁酉": "山下火", "戊戌": "平地木", "己亥": "平地木",
    "庚子": "壁上土", "辛丑": "壁上土", "壬寅": "金箔金", "癸卯": "金箔金", "甲辰": "佛灯火", "乙巳": "佛灯火",
    "丙午": "天河水", "丁未": "天河水", "戊申": "大驿土", "己酉": "大驿土", "庚戌": "钗钏金", "辛亥": "钗钏金",
    "壬子": "桑柘木", "癸丑": "桑柘木", "甲寅": "大溪水", "乙卯": "大溪水", "丙辰": "沙中土", "丁巳": "沙中土",
    "戊午": "天上火", "己未": "天上火", "庚申": "石榴木", "辛酉": "石榴木", "壬戌": "大海水", "癸亥": "大海水"
}

# ===================== 数据库函数（100% 复制 APP0 正确版） =====================
def query_db_ganzhi(solar_date_str: str) -> tuple[str, str, str]:
    try:
        conn = sqlite3.connect(resource_path("bazi_calendar.db"), timeout=10)
        cursor = conn.cursor()
        cursor.execute('SELECT 年, 月建, 纳音 FROM calendar WHERE 国历 = ? LIMIT 1', (solar_date_str,))
        result = cursor.fetchone()
        conn.close()
        return result if result else ("甲子", "甲子", "甲子")
    except Exception:
        return "甲子", "甲子", "甲子"

def solar_to_lunar_from_db(solar_date_str: str) -> dict[str, str]:
    try:
        conn = sqlite3.connect(resource_path("bazi_calendar.db"), timeout=10)
        cursor = conn.cursor()
        cursor.execute('SELECT 农历年,农历月,农历日,生肖 FROM calendar WHERE 国历 = ? LIMIT 1', (solar_date_str,))
        res = cursor.fetchone()
        conn.close()
        if res:
            return {"农历完整信息": f"{res[0]}年{res[1]}月{res[2]}日", "生肖": res[3]}
        else:
            return {"农历完整信息": "2026年三月初十", "生肖": "马"}
    except Exception:
        return {"农历完整信息": "2026年三月初十", "生肖": "马"}

def lunar_to_solar_from_db(lunar_year: int, lunar_month: int, lunar_day: int, is_leap: int) -> str:
    try:
        conn = sqlite3.connect(resource_path("bazi_calendar.db"), timeout=10)
        cursor = conn.cursor()
        cursor.execute('''SELECT 国历 FROM calendar WHERE 农历年=? AND 农历月=? AND 农历日=? AND 闰月=? LIMIT 1''',
                       (lunar_year, lunar_month, lunar_day, is_leap))
        res = cursor.fetchone()
        conn.close()
        return res[0] if res else "1990-01-01"
    except Exception:
        return "1990-01-01"

def calculate_shichen_ganzhi(ri_gan: str, shichen: str) -> str:
    shichen_zhi_map = {"子时": "子", "丑时": "丑", "寅时": "寅", "卯时": "卯", "辰时": "辰", "巳时": "巳", "午时": "午",
                       "未时": "未", "申时": "申", "酉时": "酉", "戌时": "戌", "亥时": "亥"}
    rigan_zi_shigan_map = {"甲": "甲", "己": "甲", "乙": "丙", "庚": "丙", "丙": "戊", "辛": "戊", "丁": "庚",
                           "壬": "庚", "戊": "壬", "癸": "壬"}
    gan_list = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    shichen_index = list(shichen_zhi_map.keys()).index(shichen)
    zi_gan_index = gan_list.index(rigan_zi_shigan_map[ri_gan])
    return gan_list[(zi_gan_index + shichen_index) % 10] + shichen_zhi_map[shichen]

# ===================== 八字核心计算（完全不变） =====================
class BaziCalculator:
    @staticmethod
    def generate_bazi(target_date: str, shichen: str) -> dict:
        nian, yue, ri = query_db_ganzhi(target_date)
        ri_gan = ri[0]
        shi = calculate_shichen_ganzhi(ri_gan, shichen)
        lunar = solar_to_lunar_from_db(target_date)
        wuxing = {"金": 0, "木": 0, "水": 0, "火": 0, "土": 0}
        for g in [nian[0], yue[0], ri[0], shi[0]]:
            wuxing[TIANGAN_WUXING[g]] += 1
        for z in [nian[1], yue[1], ri[1], shi[1]]:
            wuxing[YUELING_WUXING[z]] += 1
        return {
            "公历": target_date, "农历": lunar["农历完整信息"], "生肖": lunar["生肖"],
            "时辰": shichen, "八字": [nian, yue, ri, shi], "八字_str": f"{nian} {yue} {ri} {shi}",
            "日干": ri_gan, "五行": wuxing,
            "纳音": [NAYIN_TABLE.get(nian, ""), NAYIN_TABLE.get(yue, ""), NAYIN_TABLE.get(ri, ""), NAYIN_TABLE.get(shi, "")]
        }

    @staticmethod
    def get_current_bazi() -> dict:
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_hour = now.hour
        shichen_map = {23: "子时", 0: "子时", 1: "丑时", 2: "丑时", 3: "寅时", 4: "寅时", 5: "卯时", 6: "卯时",
                       7: "辰时", 8: "辰时", 9: "巳时", 10: "巳时", 11: "午时", 12: "午时", 13: "未时", 14: "未时",
                       15: "申时", 16: "申时", 17: "酉时", 18: "酉时", 19: "戌时", 20: "戌时", 21: "亥时", 22: "亥时"}
        current_shichen = shichen_map.get(current_hour, "亥时")
        return BaziCalculator.generate_bazi(current_date, current_shichen)

# ===================== 页面样式（完全保留你的原版，仅优化手机端历法布局） =====================
st.set_page_config(page_title="真命盘专业版", page_icon="☯️", layout="centered")
page_bg = """
<style>
body {margin: 0;padding: 0;background-color:#E5E5E5;}
.stApp {background-color:#E5E5E5;padding: 0;}
div.block-container {padding-top: 50px !important;padding-left:20px !important;padding-right:20px !important;padding-bottom:60px !important;}
div.stContainer {background:#F0F0F0;border-radius:12px;padding:15px;}
div.stTextInput>div>div {border-radius:8px; background:#FFF;}
div.stSelectbox>div>div {border-radius:8px; background:#FFF;}
div.stDateInput>div>div {border-radius:8px; background:#FFF;}
div.stNumberInput>div>div {border-radius:8px; background:#FFF;}
/* 关键修复：只让radio自适应，不影响按钮 */
div.stRadio>div {display:flex;gap:8px;justify-content:center;flex-wrap:wrap !important;max-width:100%;}
div.stRadio label {background:#FFF;border-radius:20px;padding:8px 16px;border:1px solid #EEE;font-size:14px;white-space:nowrap;box-sizing:border-box;}
div.stRadio [role="radio"]:checked + label {background:#D4AF37;color:#FFF;border-color:#D4AF37;}
div.stButton>button {background-color:#222222;color:#D4AF37;border-radius:30px;height:68px;font-size:18px;font-weight:bold;width:100%;}
.footer-nav {position:fixed;bottom:0;left:0;right:0;background:#FFF;display:flex;justify-content:space-around;padding:10px 0;border-top:1px solid #EEE;z-index:100;}
.nav-item {text-align:center;font-size:12px;color:#666;}
.nav-item.active {color:#9370DB;}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)
# ===================== 界面与功能（仅优化性别/历法布局，和性别一样一行显示） =====================
with st.container(border=True):
    col_name_label, col_name_input = st.columns([1, 4])
    with col_name_label: st.markdown("**姓名**")
    with col_name_input: name = st.text_input("", placeholder="请输入姓名", label_visibility="collapsed")

    # 优化点：性别和历法放在同一行两列，和性别一样一行显示
    col_gender, col_cal = st.columns(2)
    with col_gender:
        st.markdown("**性别**")
        gender = st.radio("", ["先生", "女士"], horizontal=True, label_visibility="collapsed")
    with col_cal:
        st.markdown("**历法**")
        calendar_type = st.radio("", ["公历", "农历"], horizontal=True, label_visibility="collapsed")

    if calendar_type == "公历":
        st.markdown("**出生时间（必填）**")
        birth_date = st.date_input("", datetime(2000, 1, 1), min_value=datetime(1900, 1, 1), max_value=datetime(2100, 12, 31), label_visibility="collapsed")
        date_str = birth_date.strftime("%Y-%m-%d")
    else:
        col_lun_year, col_lun_month, col_lun_day = st.columns(3)
        with col_lun_year:
            st.markdown("**农历年**")
            lunar_year_input = st.number_input("", 1900, 2100, 2000, label_visibility="collapsed")
        with col_lun_month:
            st.markdown("**农历月**")
            lunar_month_input = st.number_input("", 1, 12, 6, label_visibility="collapsed")
        with col_lun_day:
            st.markdown("**农历日**")
            lunar_day_input = st.number_input("", 1, 30, 15, label_visibility="collapsed")
        st.markdown("**平月/闰月**")
        leap_option = st.radio("", ["平月", "闰月"], horizontal=True, label_visibility="collapsed")
        is_leap_input = 1 if leap_option == "闰月" else 0
        date_str = lunar_to_solar_from_db(lunar_year_input, lunar_month_input, lunar_day_input, is_leap_input)

    st.markdown("**出生地区**")
    birth_area = st.selectbox("", ["北京", "成都", "上海", "广州", "深圳"], index=0, label_visibility="collapsed")
    true_sun_time = "1990-01-01 00:00"
    lat, lon = "北纬39.93", "东经116.42"

    # 🔴 修复：手机端下拉框显示完整12时辰（含亥时）
    st.markdown("""
    <style>
    /* 强制下拉菜单高度足够，显示全部时辰 */
    div[data-baseweb="popover"] { max-height: 400px !important; }
    div[data-baseweb="select"] ul { max-height: 380px !important; height: auto !important; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("**出生时辰**")

    # 把12个时辰分成两列，在手机上也能完全显示
    col1, col2 = st.columns(2)
    with col1:
        shichen1 = st.radio(
            "",
            ["子时 23:00-01:00", "丑时 01:00-03:00", "寅时 03:00-05:00", "卯时 05:00-07:00", "辰时 07:00-09:00",
             "巳时 09:00-11:00"],
            index=5,  # 对应"巳时"，和你原来的index=6（午时）错开
            label_visibility="collapsed"
        )
    with col2:
        shichen2 = st.radio(
            "",
            ["午时 11:00-13:00", "未时 13:00-15:00", "申时 15:00-17:00", "酉时 17:00-19:00", "戌时 19:00-21:00",
             "亥时 21:00-23:00"],
            index=0,  # 默认选中"午时"，和原来的index=6效果一致
            label_visibility="collapsed"
        )

    # 处理用户的选择：判断是选了左边还是右边
    if shichen1 != "":
        selected_shichen_detail = shichen1
    else:
        selected_shichen_detail = shichen2

    shichen_input = selected_shichen_detail.split(" ")[0]

    # 按钮布局优化版：1:1等宽 + 小间距，仅作用于这两个按钮
    col_btn1, col_btn2 = st.columns(2, gap="small")
    with col_btn1:
        if st.button("开始排盘", use_container_width=True):
            st.session_state.bazi_result = BaziCalculator.generate_bazi(date_str, shichen_input)
    with col_btn2:
        if st.button("即时排盘", use_container_width=True):
            st.session_state.bazi_result = BaziCalculator.get_current_bazi()

    col_info, col_save = st.columns([3, 1])
    with col_info:
        st.markdown(f"""<div style="color:#666;font-size:12px;">真太阳时：{true_sun_time}<br>地址经纬：{lat} {lon}</div>""", unsafe_allow_html=True)
    with col_save:
        save_toggle = st.toggle("保存", value=False)

# ========== 四柱显示：居中+字体大小自由控制 ==========
if "bazi_result" in st.session_state and st.session_state.bazi_result:
        r = st.session_state.bazi_result
        st.markdown("---")
        st.success("✅ 排盘完成")

        # 用HTML表格，完全自定义样式
        pillars_html = f"""
        <style>
        .custom-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        .custom-table th, .custom-table td {{
            border: 1px solid #ddd;
            padding: 12px 8px;
            text-align: center;
        }}
        .custom-table th {{
            font-size: 14px; /* 表头文字大小 */
            color: #666;
            background-color: #f8f8f8;
        }}
        .custom-table td {{
            font-size: 28px; /* ← 八字文字大小，改这里！ */
            font-weight: bold;
            color: #333;
        }}
        @media (max-width: 600px) {{
            .custom-table th {{ font-size: 12px; }}
            .custom-table td {{ font-size: 28px; /* 手机端八字大小 */ }}
        }}
        </style>

        <table class="custom-table">
            <thead>
                <tr>
                    <th>年柱</th>
                    <th>月柱</th>
                    <th>日柱</th>
                    <th>时柱</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>{r['八字'][0]}</td>
                    <td>{r['八字'][1]}</td>
                    <td>{r['八字'][2]}</td>
                    <td>{r['八字'][3]}</td>
                </tr>
            </tbody>
        </table>
        """
        st.markdown(pillars_html, unsafe_allow_html=True)

        # 以下内容保持不变
        st.markdown(f"**公历**：{r['公历']}")
        st.markdown(f"**农历**：{r['农历']}")
        st.markdown(f"**生肖**：{r['生肖']}　**时辰**：{r['时辰']}　**日干**：{r['日干']}")
        st.markdown(
            f"**五行**：金{r['五行']['金']} 木{r['五行']['木']} 水{r['五行']['水']} 火{r['五行']['火']} 土{r['五行']['土']}")

st.markdown("---")
tab1, tab2, tab3, tab4 = st.tabs(["📆 万年历", "💰 八字论财", "🌀 八字合盘", "🔍 多盘对比"])
with tab1:
    d = st.date_input("选择日期", datetime.now(), min_value=datetime(1900, 1, 1), max_value=datetime(2100, 12, 31))
    if st.button("查询万年历"):
        s = d.strftime("%Y-%m-%d")
        lu = solar_to_lunar_from_db(s)
        n, y, r = query_db_ganzhi(s)
        st.write(f"公历：{s}")
        st.write(f"农历：{lu['农历完整信息']}")
        st.write(f"生肖：{lu['生肖']}")
        st.write(f"年柱：{n}　月柱：{y}　日柱：{r}")
with tab2:
    if "bazi_result" in st.session_state and st.session_state.bazi_result:
        r = st.session_state.bazi_result
        w = r["五行"]
        caixing = "财星旺" if w["金"] + w["土"] > 3 else "财星弱"
        st.markdown(f"**日干**：{r['日干']}")
        st.markdown(f"**财运**：{caixing}")
        st.markdown("正财：稳定收入　偏财：投资外快")
    else:
        st.warning("请先排盘")
with tab3:
    st.markdown("#### 双人八字合盘")
    col_a, col_b = st.columns(2)
    with col_a:
        a_date = st.date_input("A公历生日", key="a_date")
        a_shichen = st.selectbox("A出生时辰", SHICHEN_DETAIL, key="a_shi")
        a_shichen_name = a_shichen.split(" ")[0]
    with col_b:
        b_date = st.date_input("B公历生日", key="b_date")
        b_shichen = st.selectbox("B出生时辰", SHICHEN_DETAIL, key="b_shi")
        b_shichen_name = b_shichen.split(" ")[0]
    if st.button("开始合盘"):
        a_data = BaziCalculator.generate_bazi(a_date.strftime("%Y-%m-%d"), a_shichen_name)
        b_data = BaziCalculator.generate_bazi(b_date.strftime("%Y-%m-%d"), b_shichen_name)
        score = 0
        common_elements = 0
        for k in ["金", "木", "水", "火", "土"]:
            if a_data["五行"][k] > 0 and b_data["五行"][k] > 0:
                common_elements += 1
            if (a_data["五行"][k] > 0 and b_data["五行"][k] == 0) or (a_data["五行"][k] == 0 and b_data["五行"][k] > 0):
                score += 10
        score += common_elements * 5
        if score >= 40:
            level, desc = "上等婚配｜天生一对", "五行高度互补，气场契合度高"
        elif score >= 30:
            level, desc = "中等婚配｜和谐美满", "五行互补良好，相处轻松愉快"
        else:
            level, desc = "普通婚配｜需磨合", "五行互补一般，需要多沟通理解"
        st.markdown(f"**A方八字**：{a_data['八字_str']}")
        st.markdown(f"**B方八字**：{b_data['八字_str']}")
        st.markdown(f"**合盘评分**：{score}/50")
        st.markdown(f"**婚配等级**：{level}")
        st.markdown(f"**说明**：{desc}")
with tab4:
    st.markdown("#### 多盘对比（支持添加多个八字）")
    if "duopan_list" not in st.session_state:
        st.session_state.duopan_list = []
    col_btn_add, col_btn_clear, col_btn_compare = st.columns(3)
    with col_btn_add:
        if st.button("添加当前八字到对比列表", use_container_width=True):
            if "bazi_result" in st.session_state and st.session_state.bazi_result:
                st.session_state.duopan_list.append(st.session_state.bazi_result)
                st.success("添加成功！")
    with col_btn_clear:
        if st.button("清空对比列表", use_container_width=True):
            st.session_state.duopan_list = []
            st.success("已清空！")
    with col_btn_compare:
        if st.button("开始对比", use_container_width=True):
            if len(st.session_state.duopan_list) < 2:
                st.warning("请至少添加2个八字进行对比！")
            else:
                st.success("对比执行中...")
                all_elements = []
                for data in st.session_state.duopan_list:
                    all_elements.append(data["五行"])
                avg_wuxing = {"金": 0.0, "木": 0.0, "水": 0.0, "火": 0.0, "土": 0.0}
                for k in avg_wuxing:
                    avg_wuxing[k] = sum(d[k] for d in all_elements) / len(all_elements)
                for k in avg_wuxing:
                    st.markdown(f"**{k}**：平均值 {avg_wuxing[k]:.1f}，差异范围 {min(d[k] for d in all_elements)} - {max(d[k] for d in all_elements)}")
    if st.session_state.duopan_list:
        for i, data in enumerate(st.session_state.duopan_list):
            st.markdown(f"**第{i + 1}个八字**：{data['八字_str']} | {data['农历']}")
    else:
        st.info("请先排盘，再添加到对比列表")

st.markdown("""
<div class="footer-nav">
    <div class="nav-item active">☯️<br>排盘</div>
    <div class="nav-item">📄<br>解读</div>
    <div class="nav-item">⏱️<br>吉日</div>
    <div class="nav-item">🏮<br>风水</div>
    <div class="nav-item"><br>..</div>
    <div class="nav-item"><br>..</div>
    <div class="nav-item"><br>..</div>
</div>
""", unsafe_allow_html=True)
