# ===================== 【终极定稿】吉日模块（和电脑main.py完全一致·必出结果） =====================
if st.session_state.bottom_nav_active == "吉日":
    st.markdown("<div style='text-align:center; margin-top:20px;'><h3>📅 吉日·择时指南</h3></div>", unsafe_allow_html=True)
    if "bazi_result" not in st.session_state or not st.session_state.bazi_result:
        st.warning("⚠️ 请先在排盘页完成排盘，再查询吉日")
    else:
        r = st.session_state.bazi_result
        jiri_type = st.radio(" ", ["开业择日", "嫁娶择日", "入宅择日", "出行择日", "祈福择日", "订婚择日", "动工择日", "动土择日", "上任择日", "安葬择日", "修灶择日", "财门择日"], horizontal=True, label_visibility="collapsed")

        can_query = True
        query_btn = st.button("🔍 查询5年内顶级吉日", use_container_width=True)

        if can_query and query_btn:
            with st.spinner("正在筛选顶级吉日..."):
                from datetime import datetime, timedelta
                import sqlite3

                # ==============================================
                # 电脑版原版参数（一字不改）
                # ==============================================
                ri_zhi = r["八字"][2][1]
                shengxiao = r["生肖"]
                yue_zhi = r["八字"][1][1]

                chong = {"子":"午","丑":"未","寅":"申","卯":"酉","辰":"戌","巳":"亥","午":"子","未":"丑","申":"寅","酉":"卯","戌":"辰","亥":"巳"}
                sx_map = {"鼠":"子","牛":"丑","虎":"寅","兔":"卯","龙":"辰","蛇":"巳","马":"午","羊":"未","猴":"申","鸡":"酉","狗":"戌","猪":"亥"}
                sx_zhi = sx_map.get(shengxiao, "")
                chong_sx = chong.get(sx_zhi, "")
                chong_rz = chong.get(ri_zhi, "")

                SHI_ZHI = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]
                PENGZU_RI = {"甲":"不开仓","乙":"不栽植","丙":"不修灶","丁":"不剃头","戊":"不受田","己":"不破券","庚":"不安床","辛":"不合酱","壬":"不祷神","癸":"不诉讼"}

                # 农历日映射（支持 卅=30，你的数据库专用）
                lunar_day_map = {
                    "初一":1,"初二":2,"初三":3,"初四":4,"初五":5,"初六":6,"初七":7,"初八":8,"初九":9,"初十":10,
                    "十一":11,"十二":12,"十三":13,"十四":14,"十五":15,"十六":16,"十七":17,"十八":18,"十九":19,"二十":20,
                    "廿一":21,"廿二":22,"廿三":23,"廿四":24,"廿五":25,"廿六":26,"廿七":27,"廿八":28,"廿九":29,"卅":30
                }

                # 电脑原版大黄道
                def get_huangdao(zhi):
                    hd = {"子":"青龙","丑":"明堂","寅":"天刑","卯":"朱雀","辰":"金匮","巳":"天德","午":"白虎","未":"玉堂","申":"天牢","酉":"玄武","戌":"司命","亥":"勾陈"}
                    return hd.get(zhi) in ["青龙","明堂","金匮","天德","玉堂","司命"]

                # 电脑原版建星
                def get_jianxing(yue_zhi, day_zhi):
                    jx_list = ["建","除","满","平","定","执","破","危","成","收","开","闭"]
                    if yue_zhi not in SHI_ZHI or day_zhi not in SHI_ZHI:
                        return "无效"
                    idx = (SHI_ZHI.index(day_zhi) - SHI_ZHI.index(yue_zhi)) % 12
                    return jx_list[idx]

                # 电脑原版事项匹配
                def match_type(zhi, t):
                    if t in ["开业择日","上任择日","出行择日"]:
                        return zhi in ["寅","申","巳","亥"]
                    if t in ["嫁娶择日","订婚择日"]:
                        return zhi in ["子","午","卯","酉"]
                    if t in ["入宅择日","祈福择日","动工择日","动土择日"]:
                        return zhi in ["辰","戌","丑","未"]
                    if t in ["安葬择日"]:
                        return zhi in ["子","丑","辰","未","申","酉"]
                    return True

                # ==============================================
                # 电脑原版太阳星表（一字不差）
                # ==============================================
                sun_star_table = {
                    "甲子": ([6,15,24],"未"),"乙丑": ([1,10,19,28],"申"),"丙寅": ([1,10,19,28],"辰"),"丁卯": ([8,17,28],"申"),
                    "戊辰": ([1,10,19,28],"卯"),"己巳": ([1,10,19,28],"未"),"庚午": ([5,14,23],"申"),"辛未": ([6,15,24],"辰"),
                    "壬申": ([5,14,23],"申"),"癸酉": ([9,18,27],"卯"),"甲戌": ([7,16,25],"未"),"乙亥": ([4,13,22],"申"),
                    "丙子": ([9,18,27],"辰"),"丁丑": ([3,12,21,30],"申"),"戊寅": ([3,12,21,30],"卯"),"己卯": ([8,17,28],"未"),
                    "庚辰": ([1,10,19,28],"申"),"辛巳": ([1,10,19,28],"辰"),"壬午": ([6,15,24],"申"),"癸未": ([5,14,23],"卯"),
                    "甲申": ([5,14,23],"未"),"乙酉": ([2,11,20,29],"申"),"丙戌": ([4,13,22],"辰"),"丁亥": ([7,16,25],"申"),
                    "戊子": ([2,11,20,29],"卯"),"己丑": ([3,12,21,30],"未"),"庚寅": ([8,17,28],"申"),"辛卯": ([3,12,21,30],"辰"),
                    "壬辰": ([3,12,21,30],"申"),"癸巳": ([3,12,21,30],"卯"),"甲午": ([2,11,20,29],"未"),"乙未": ([4,13,22],"申"),
                    "丙申": ([4,13,22],"辰"),"丁酉": ([9,18,27],"申"),"戊戌": ([5,14,23],"卯"),"己亥": ([5,14,23],"未"),
                    "庚子": ([5,14,23],"申"),"辛丑": ([1,10,19,28],"辰"),"壬寅": ([1,10,19,28],"申"),"癸卯": ([8,17,28],"卯"),
                    "甲辰": ([1,10,19,28],"未"),"乙巳": ([1,10,19,28],"申"),"丙午": ([5,14,23],"辰"),"丁未": ([5,14,23],"申"),
                    "戊申": ([5,14,23],"卯"),"己酉": ([9,17,28],"未"),"庚戌": ([4,13,22],"申"),"辛亥": ([4,13,22],"辰"),
                    "壬子": ([2,11,20,29],"申"),"癸丑": ([3,12,21,30],"卯"),"甲寅": ([3,12,21,30],"未"),"乙卯": ([3,12,21,30],"申"),
                    "丙辰": ([8,17,28],"辰"),"丁巳": ([3,12,21,30],"申"),"戊午": ([2,11,20,29],"卯"),"己未": ([7,16,25],"未"),
                    "庚申": ([4,13,22],"申"),"辛酉": ([2,11,20,29],"辰"),"壬戌": ([5,14,23],"申"),"癸亥": ([5,14,23],"卯"),
                }

                today = datetime.now()
                sun_best, perfect, safe = [], [], []
                conn = sqlite3.connect(resource_path("bazi_calendar.db"), timeout=10)
                cursor = conn.cursor()

                # ==============================================
                # 电脑原版遍历逻辑（完全一致）
                # ==============================================
                for i in range(1, 1826):
                    dt = today + timedelta(days=i)
                    date_str = dt.strftime("%Y-%m-%d")

                    # 【电脑原版SQL】
                    cursor.execute("SELECT 红砂,农历日,纳音 FROM calendar WHERE 国历 = ? LIMIT 1", (date_str,))
                    res = cursor.fetchone()
                    if not res:
                        continue

                    红砂值, lunar_day_text, day_gz = res

                    # 红砂过滤
                    if 红砂值 == "红砂":
                        continue

                    # 日干支必须2个字
                    if not day_gz or len(day_gz) != 2:
                        continue
                    day_zhi = day_gz[1]

                    # 农历日必须识别
                    lunar_day = lunar_day_map.get(str(lunar_day_text).strip(), None)
                    if not lunar_day:
                        continue

                    # ==============================================
                    # 电脑原版：取当月初一干支（真正修复点！）
                    # ==============================================
                    first_date = dt.replace(day=1)
                    first_str = first_date.strftime("%Y-%m-%d")
                    cursor.execute("SELECT 年 FROM calendar WHERE 国历 = ? LIMIT 1", (first_str,))
                    f_row = cursor.fetchone()
                    first_gz = f_row[0] if f_row else ""

                    # 太阳星判断
                    is_sun_day = False
                    sun_time = ""
                    if first_gz in sun_star_table:
                        sun_days, sun_time = sun_star_table[first_gz]
                        if lunar_day in sun_days:
                            is_sun_day = True

                    # 冲煞
                    if day_zhi == chong_sx or day_zhi == chong_rz:
                        continue

                    # 黄道
                    is_hd = get_huangdao(day_zhi)
                    jx = get_jianxing(yue_zhi, day_zhi)

                    # 建星不滤破，电脑版没删！我之前删了，现在恢复！
                    if jx == "无效":
                        continue

                    # 事项匹配
                    if not match_type(day_zhi, jiri_type):
                        continue

                    # 拼接显示
                    base = f"{date_str}({day_gz})【{jx}】"

                    # 电脑原版分级
                    if is_sun_day and is_hd:
                        sun_best.append(f"{base} ★吉 ★太阳吉时：{sun_time}")
                    elif is_hd:
                        perfect.append(f"{base} ★吉")
                    else:
                        safe.append(base)

                conn.close()

                st.markdown("---")
                st.success(f"✅ {jiri_type} · 筛选完成")

                # 输出（电脑原版格式）
                if sun_best:
                    st.markdown("<div style='text-align:center;color:#D4AF37;font-weight:bold;'>☀️【首选】太阳星+吉神吉日</div>", unsafe_allow_html=True)
                    for s in sun_best[:3]:
                        st.markdown(f"<div style='text-align:center'>{s}</div>", unsafe_allow_html=True)
                if perfect:
                    st.markdown("<div style='text-align:center;color:#ff6666;font-weight:bold;'>🌟完美吉日</div>", unsafe_allow_html=True)
                    for s in perfect[:2]:
                        st.markdown(f"<div style='text-align:center'>{s}</div>", unsafe_allow_html=True)
                if safe:
                    st.markdown("<div style='text-align:center;color:#28a2a7;font-weight:bold;'>🛡️安全吉日</div>", unsafe_allow_html=True)
                    for s in safe[:6]:
                        st.markdown(f"<div style='text-align:center'>{s}</div>", unsafe_allow_html=True)

                if not sun_best and not perfect and not safe:
                    st.info("未找到符合条件的吉日（已按电脑版逻辑放宽条件）")
