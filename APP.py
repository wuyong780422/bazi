# ===================== APP.py 终极修复：支持双胞胎+嫁娶限2人+对齐main =====================
if st.session_state.bottom_nav_active == "吉日":
    st.markdown("<div style='text-align:center;margin-top:20px;'><h3>📅 良辰吉日</h3></div>", unsafe_allow_html=True)

    if "bazi_result" not in st.session_state or not st.session_state.bazi_result:
        st.warning("⚠️ 请先排盘再查询吉日")
        st.stop()

    r = st.session_state.bazi_result

    jiri_type = st.radio(
        "", ["开业择日","嫁娶择日","入宅择日","出行择日","祈福择日","订婚择日",
             "动工择日","动土择日","上任择日","安葬择日","修灶择日","财门择日"],
        horizontal=True, label_visibility="collapsed"
    )

    # 严格分类
    single_types = ["开业择日","出行择日","上任择日","祈福择日","修灶择日","财门择日"]
    double_types = ["嫁娶择日","订婚择日"]  # 限2人
    multi_types  = ["入宅择日","动工择日","动土择日","安葬择日"]

    is_single = jiri_type in single_types
    is_double = jiri_type in double_types
    is_multi  = jiri_type in multi_types

    # 双人/多人界面
    if not is_single:
        st.markdown("---")
        if is_double:
            st.markdown("🔴 **嫁娶/订婚择日：仅限 2 人（男女双方），支持双胞胎同盘**")
        else:
            st.markdown("🔹 **多人择日：可添加多人，支持双胞胎重复添加同盘**")

        col_add, col_clear, col_start = st.columns(3)

        with col_add:
            if st.button("➕ 添加当前八字", use_container_width=True):
                if "jiri_list" not in st.session_state:
                    st.session_state.jiri_list = []
                # ===================== 修复：允许重复添加（支持双胞胎） =====================
                st.session_state.jiri_list.append(r)
                # 嫁娶/订婚 强制限2人
                if is_double:
                    if len(st.session_state.jiri_list) > 2:
                        st.session_state.jiri_list = st.session_state.jiri_list[-2:]
                        st.warning("⚠️ 嫁娶/订婚仅限2人，已自动保留最后2个")
                    else:
                        st.success("✅ 已添加")
                else:
                    st.success("✅ 已添加")

        with col_clear:
            if st.button("🧹 清空列表", use_container_width=True):
                st.session_state.jiri_list = []
                st.success("🗑️ 已清空")

        with col_start:
            start_jiri = st.button("🚀 开始择日", use_container_width=True)

        # 显示列表
        if st.session_state.get("jiri_list"):
            st.markdown("**📋 参与择日八字**")
            for i, item in enumerate(st.session_state.jiri_list):
                st.write(f"{i+1}. {item['八字_str']}")

    # 权限判断
    query_btn = st.button("🔍 查询5年内吉日", use_container_width=True) if is_single else start_jiri
    allow_query = False

    if is_single:
        allow_query = True
    elif is_double:
        allow_query = len(st.session_state.get("jiri_list", [])) == 2
    else:
        allow_query = len(st.session_state.get("jiri_list", [])) >= 2

    # 防错提示
    if query_btn and not allow_query:
        if is_double:
            st.warning("⚠️ 嫁娶/订婚必须添加 **恰好2个八字**！")
        else:
            st.warning("⚠️ 请先添加至少 **2个八字**！")
        st.stop()

    # 100%对齐main运算逻辑
    if query_btn and allow_query:
        with st.spinner("正在筛选吉日..."):
            from datetime import datetime, timedelta
            import sqlite3

            # main原版常量（完全一致）
            chong_map = {"子":"午","丑":"未","寅":"申","卯":"酉","辰":"戌","巳":"亥","午":"子","未":"丑","申":"寅","酉":"卯","戌":"辰","亥":"巳"}
            sx_map = {"鼠":"子","牛":"丑","虎":"寅","兔":"卯","龙":"辰","蛇":"巳","马":"午","羊":"未","猴":"申","鸡":"酉","狗":"戌","猪":"亥"}
            sili_jue = [(3,20),(6,21),(9,23),(12,22),(2,4),(5,6),(8,8),(11,8)]
            sanniang = [3,7,13,18,22,27]
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

            # main原版函数（完全一致）
            def get_huangdao(zhi):
                hd = {"子":"青龙","丑":"明堂","寅":"天刑","卯":"朱雀","辰":"金匮","巳":"天德","午":"白虎","未":"玉堂","申":"天牢","酉":"玄武","戌":"司命","亥":"勾陈"}
                return hd.get(zhi) in ["青龙","明堂","金匮","天德","玉堂","司命"]
            def is_yue_po(month, zhi):
                yz = ["","寅","卯","辰","巳","午","未","申","酉","戌","亥","子","丑"]
                return chong_map.get(yz[month],"") == zhi
            def match_type(zhi, t):
                if t in ["开业择日","上任择日","出行择日","财门择日"]:return zhi in ["寅","申","巳","亥"]
                if t in ["嫁娶择日","订婚择日","修灶择日"]:return zhi in ["子","午","卯","酉"]
                if t in ["入宅择日","祈福择日","动工择日","动土择日"]:return zhi in ["辰","戌","丑","未"]
                if t in ["安葬择日"]:return zhi in ["子","丑","辰","未","申","酉"]
                return True
            def check_god(dg, dz, yue_zhi_main, nian_gan):
                lu={"甲":"寅","乙":"卯","丙":"巳","丁":"午","戊":"巳","己":"午","庚":"申","辛":"酉","壬":"亥","癸":"子"}
                tx={"寅":"戌","卯":"亥","辰":"子","巳":"丑","午":"寅","未":"卯","申":"辰","酉":"巳","戌":"午","亥":"未","子":"申","丑":"酉"}
                ye={"寅":"亥","卯":"子","辰":"丑","巳":"寅","午":"卯","未":"辰","申":"巳","酉":"午","戌":"未","亥":"申","子":"酉","丑":"戌"}
                td={"甲":["寅","午"],"乙":["申","子"],"丙":["卯","亥"],"丁":["巳","丑"],"戊":["卯","亥"],"己":["巳","丑"],"庚":["子","申"],"辛":["寅","午"],"壬":["巳","丑"],"癸":["卯","亥"]}
                return dz==lu.get(dg,"") or dz==tx.get(yue_zhi_main,"") or dz==ye.get(yue_zhi_main,"") or dz in td.get(nian_gan,[])

            # main原版参数
            ri_zhi = r["八字"][2][1]
            shengxiao = r["生肖"]
            yue_zhi_main = r["八字"][1][1]
            nian_gan = r["八字"][0][0]

            today = datetime.now()
            sun_best, perfect, safe = [], [], []
            conn = sqlite3.connect(resource_path("bazi_calendar.db"), timeout=10)
            cursor = conn.cursor()

            for i in range(1, 1826):
                dt = today + timedelta(days=i)
                date_str = dt.strftime("%Y-%m-%d")
                m, d = dt.month, dt.day

                # 数据库查询（完全一致）
                cursor.execute("SELECT 纳音,农历日,红砂 FROM calendar WHERE 国历 LIKE ? LIMIT 1", (date_str+"%",))
                res = cursor.fetchone()
                if not res: continue
                day_gz, lunar_day, hongsha = res
                if len(day_gz)!=2: continue
                dg, dz = day_gz[0], day_gz[1]

                if hongsha and hongsha.strip()=="红砂": continue

                # 单人冲煞
                sx_zhi = sx_map.get(shengxiao,"")
                if dz == chong_map.get(sx_zhi,"") or dz == chong_map.get(ri_zhi,""): continue

                # ===================== 修复：多人冲煞（与main完全一致） =====================
                if not is_single:
                    skip = False
                    for b in st.session_state.jiri_list:
                        try:
                            if dz == chong_map.get(b["八字"][2][1],""):
                                skip = True
                                break
                        except:
                            continue
                    if skip: continue

                if (m,d) in sili_jue or d in sanniang or is_yue_po(m, dz): continue
                if not get_huangdao(dz) or not match_type(dz, jiri_type): continue

                # 太阳星
                first_str = dt.replace(day=1).strftime("%Y-%m-%d")
                cursor.execute("SELECT 纳音 FROM calendar WHERE 国历 LIKE ? LIMIT 1", (first_str+"%",))
                frow = cursor.fetchone()
                first_gz = frow[0] if frow else ""

                is_sun, sun_time = False, ""
                if first_gz in sun_star_table and lunar_day in sun_star_table[first_gz][0]:
                    is_sun = True
                    sun_time = sun_star_table[first_gz][1]

                has_god = check_god(dg, dz, yue_zhi_main, nian_gan)
                line = f"{date_str}({day_gz})"
                if has_god: line += "⭐吉"
                if is_sun:
                    sun_best.append(f"{line} 太阳吉时:{sun_time}")
                elif has_god:
                    perfect.append(line)
                else:
                    safe.append(line)

            conn.close()

            st.markdown("---")
            st.success(f"✅ {jiri_type} 筛选完成")
            if sun_best:
                st.markdown("<center><font color=#D4AF37>☀️ 太阳吉日</font></center>", unsafe_allow_html=True)
                for s in sun_best[:3]: st.write(s)
            if perfect:
                st.markdown("<center><font color=#ff6666>🌟 完美吉日</font></center>", unsafe_allow_html=True)
                for s in perfect[:5]: st.write(s)
            if safe:
                st.markdown("<center><font color=#007fff>🛡️ 平安吉日</font></center>", unsafe_allow_html=True)
                for s in safe[:10]: st.write(s)
            if not sun_best and not perfect and not safe:
                st.info("未找到符合条件的吉日")
