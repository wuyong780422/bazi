# ===================== 【最终修复版】吉日模块（100%复刻电脑版） =====================
if st.session_state.bottom_nav_active == "吉日":
    st.markdown("<div style='text-align:center; margin-top:20px;'><h3>📅 吉日·择时指南</h3></div>", unsafe_allow_html=True)
    if "jiri_list" not in st.session_state:
        st.session_state.jiri_list = []
    if "bazi_result" not in st.session_state or not st.session_state.bazi_result:
        st.warning("⚠️ 请先在排盘页完成排盘，再查询吉日")
    else:
        r = st.session_state.bazi_result
        jiri_type = st.radio(" ", ["开业择日", "嫁娶择日", "入宅择日", "出行择日", "祈福择日", "订婚择日", "动工择日", "动土择日", "上任择日", "安葬择日", "修灶择日", "财门择日"], horizontal=True, label_visibility="collapsed")
        single_types = ["开业择日", "出行择日", "上任择日", "祈福择日", "修灶择日", "财门择日"]
        double_types = ["嫁娶择日", "订婚择日"]
        multi_types = ["入宅择日", "动工择日", "动土择日", "安葬择日"]
        is_single = jiri_type in single_types
        is_double = jiri_type in double_types
        is_multi = jiri_type in multi_types

        if is_double or is_multi:
            st.markdown("---")
            st.markdown("🔹 **双人/多人择日**：先排盘 → 添加当前八字到列表 → 开始择日")
            col_add, col_clear, col_start = st.columns(3)
            with col_add:
                if st.button("➕ 添加当前八字", use_container_width=True):
                    if st.session_state.bazi_result not in st.session_state.jiri_list:
                        st.session_state.jiri_list.append(st.session_state.bazi_result)
                        st.success(f"✅ 已添加：{st.session_state.bazi_result['八字_str']}")
                    else:
                        st.warning("⚠️ 该八字已在列表中")
            with col_clear:
                if st.button("🧹 清空列表", use_container_width=True):
                    st.session_state.jiri_list = []
                    st.success("🗑️ 已清空所有八字")
            with col_start:
                start_jiri = st.button("🚀 开始择日", use_container_width=True)
            if st.session_state.jiri_list:
                st.markdown("**📋 已添加参与择日的八字**")
                for i, item in enumerate(st.session_state.jiri_list):
                    st.markdown(f"{i + 1}. {item['八字_str']} | {item['农历']}")
            else:
                st.info("👆 请点击「添加当前八字」加入参与择日人员")

        can_query = False
        if is_single:
            can_query = True
        else:
            can_query = len(st.session_state.jiri_list) >= 2
        query_btn = False
        if is_single:
            query_btn = st.button("🔍 查询5年内顶级吉日", use_container_width=True)
        else:
            query_btn = start_jiri if 'start_jiri' in locals() else False

        if can_query and query_btn:
            with st.spinner("正在筛选顶级吉日..."):
                from datetime import datetime, timedelta
                import sqlite3
                ri_zhi = r["八字"][2][1]
                shengxiao = r["生肖"]
                yue_zhi = r["八字"][1][1]
                ri_gan = r["日干"]

                chong = {"子":"午","丑":"未","寅":"申","卯":"酉","辰":"戌","巳":"亥","午":"子","未":"丑","申":"寅","酉":"卯","戌":"辰","亥":"巳"}
                sx_map = {"鼠":"子","牛":"丑","虎":"寅","兔":"卯","龙":"辰","蛇":"巳","马":"午","羊":"未","猴":"申","鸡":"酉","狗":"戌","猪":"亥"}
                sx_zhi = sx_map.get(shengxiao, "")
                chong_sx = chong.get(sx_zhi, "")
                chong_rz = chong.get(ri_zhi, "")

                SHI_ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
                PENGZU_RI = {"甲":"不开仓","乙":"不栽植","丙":"不修灶","丁":"不剃头","戊":"不受田","己":"不破券","庚":"不安床","辛":"不合酱","壬":"不祷神","癸":"不诉讼"}

                # 农历日文本转数字（完全适配你的数据库）
                lunar_day_map = {
                    "初一":1,"初二":2,"初三":3,"初四":4,"初五":5,"初六":6,"初七":7,"初八":8,"初九":9,"初十":10,
                    "十一":11,"十二":12,"十三":13,"十四":14,"十五":15,"十六":16,"十七":17,"十八":18,"十九":19,"二十":20,
                    "廿一":21,"廿二":22,"廿三":23,"廿四":24,"廿五":25,"廿六":26,"廿七":27,"廿八":28,"廿九":29,"卅":30
                }

                # 黄道十二神（电脑版正统）
                def get_huangdao_by_dizhi(zhi):
                    hd = {"子":"青龙","丑":"明堂","寅":"天刑","卯":"朱雀","辰":"金匮","巳":"天德","午":"白虎","未":"玉堂","申":"天牢","酉":"玄武","戌":"司命","亥":"勾陈"}
                    return hd.get(zhi) in ["青龙","明堂","金匮","天德","玉堂","司命"]

                # 建星
                def get_jianxing(yue_zhi, day_zhi):
                    jx_list = ["建","除","满","平","定","执","破","危","成","收","开","闭"]
                    if yue_zhi not in SHI_ZHI or day_zhi not in SHI_ZHI:
                        return "无效"
                    idx = (SHI_ZHI.index(day_zhi) - SHI_ZHI.index(yue_zhi)) % 12
                    return jx_list[idx]

                # 事项匹配（电脑版完全一致）
                def match_type(zhi, t):
                    if t in ["开业择日","上任择日"]:
                        return zhi in ["寅","申","巳","亥"]
                    if t in ["嫁娶择日","订婚择日"]:
                        return zhi in ["子","午","卯","酉"]
                    if t in ["入宅择日","祈福择日"]:
                        return zhi in ["辰","戌","丑","未"]
                    if t in ["出行择日"]:
                        return zhi in ["寅","申","巳","亥"]
                    if t in ["动工择日","动土择日"]:
                        return zhi in ["辰","戌","丑","未"]
                    if t in ["安葬择日"]:
                        return zhi in ["子","丑","辰","未","申","酉"]
                    if t in ["修灶择日"]:
                        return zhi in ["子","午","卯","酉","辰","戌","丑","未"]
                    if t in ["财门择日"]:
                        return zhi in ["寅","申","巳","亥","子","午","卯","酉"]
                    return True

                today = datetime.now()
                sun_best, perfect, safe = [], [], []
                conn = sqlite3.connect(resource_path("bazi_calendar.db"), timeout=10)
                cursor = conn.cursor()

                # 【修复点1】先获取表字段，动态适配数据库
                cursor.execute("PRAGMA table_info(calendar)")
                cols = [c[1] for c in cursor.fetchall()]

                for i in range(1, 1826):
                    dt = today + timedelta(days=i)
                    date_str = dt.strftime("%Y-%m-%d")

                    # 【修复点2】通用查询，适配你的数据库字段名
                    cursor.execute(f'''SELECT * FROM calendar WHERE 国历 = ? LIMIT 1''', (date_str,))
                    res = cursor.fetchone()
                    if not res:
                        continue
                    row = dict(zip(cols, res))

                    红砂值 = row.get("红砂", "")
                    lunar_day_text = row.get("农历日", "")
                    day_gz = row.get("纳音", "")
                    first_gz = row.get("年", "")

                    if 红砂值 == "红砂":
                        continue
                    if not day_gz or len(day_gz)!=2:
                        continue
                    day_gan, day_zhi = day_gz[0], day_gz[1]

                    # 农历日数字转换
                    lunar_day = lunar_day_map.get(str(lunar_day_text).strip(), None)
                    if not lunar_day:
                        continue

                    # 【修复点3】太阳星查表，和电脑版完全一致
                    is_sun_day = False
                    sun_time = ""
                    if first_gz in sun_star_table:
                        sun_days, st = sun_star_table[first_gz]
                        if lunar_day in sun_days:
                            is_sun_day = True
                            sun_time = st

                    # 冲煞过滤
                    if day_zhi == chong_sx or day_zhi == chong_rz:
                        continue

                    # 黄道、建星、事项匹配
                    is_huangdao = get_huangdao_by_dizhi(day_zhi)
                    jx = get_jianxing(yue_zhi, day_zhi)
                    if jx == "破" or jx == "无效":
                        continue
                    if not match_type(day_zhi, jiri_type):
                        continue

                    # 显示文本
                    peng = PENGZU_RI.get(day_gan, "")
                    base = f"{dt.strftime('%Y-%m-%d')}({day_gz})【{jx}】"
                    if peng:
                        base += f"({peng})"

                    # 分级（电脑版完全一致）
                    if is_sun_day and is_huangdao:
                        sun_best.append(f"{base} ★吉 ★太阳吉时：{sun_time}")
                    elif is_huangdao:
                        perfect.append(f"{base} ★吉")
                    else:
                        safe.append(base)

                conn.close()

                st.markdown("---")
                st.success(f"✅ {jiri_type} · 筛选完成")

                if sun_best:
                    st.markdown("<div style='text-align:center;color:#D4AF37;font-weight:bold;'>☀️【首选】太阳星+吉神吉日（最吉·最灵）</div>", unsafe_allow_html=True)
                    for s in sun_best[:3]:
                        st.markdown(f"<div style='text-align:center;'>{s}</div>", unsafe_allow_html=True)
                if perfect:
                    st.markdown("<div style='text-align:center;color:#ff6666;font-weight:bold;'>🌟完美吉日（助运·黄道·无煞）</div>", unsafe_allow_html=True)
                    for s in perfect[:2]:
                        st.markdown(f"<div style='text-align:center;'>{s}</div>", unsafe_allow_html=True)
                if safe:
                    st.markdown("<div style='text-align:center;color:#28a2a7;font-weight:bold;'>🛡️安全吉日（不冲·不犯红砂）</div>", unsafe_allow_html=True)
                    for s in safe[:6]:
                        st.markdown(f"<div style='text-align:center;'>{s}</div>", unsafe_allow_html=True)
