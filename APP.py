# ===================== 【100%复刻main·结果完全一致】终极吉日模块 =====================
if st.session_state.get("bottom_nav_active", "") == "吉日":
    st.markdown("<div style='text-align:center; margin-top:20px;'><h3>📅 良辰吉日</h3></div>", unsafe_allow_html=True)
    if "bazi_result" not in st.session_state or not st.session_state.bazi_result:
        st.warning("⚠️ 请先排盘再查询吉日")
    else:
        r = st.session_state.bazi_result
        jiri_type = st.radio(
            "", ["开业择日","嫁娶择日","入宅择日","出行择日","祈福择日","订婚择日","动工择日","动土择日","上任择日","安葬择日","修灶择日","财门择日"],
            horizontal=True, label_visibility="collapsed"
        )

        if st.button("🔍 查询5年内顶级吉日", use_container_width=True):
            from datetime import datetime, timedelta
            import sqlite3

            # ===================== 只定义函数，绝不重复常量 =====================
            def get_huangdao(zhi):
                hd = {"子":"青龙","丑":"明堂","寅":"天刑","卯":"朱雀","辰":"金匮","巳":"天德","午":"白虎","未":"玉堂","申":"天牢","酉":"玄武","戌":"司命","亥":"勾陈"}
                return hd.get(zhi) in ["青龙","明堂","金匮","天德","玉堂","司命"]

            def is_yue_po(month, zhi):
                yue_zhi = ["", "寅","卯","辰","巳","午","未","申","酉","戌","亥","子","丑"][month]
                return chong_map.get(yue_zhi, "") == zhi

            def match_type(zhi, t):
                if t in ["开业择日","上任择日","出行择日","财门择日"]:
                    return zhi in ["寅","申","巳","亥"]
                if t in ["嫁娶择日","订婚择日","修灶择日"]:
                    return zhi in ["子","午","卯","酉"]
                if t in ["入宅择日","祈福择日","动工择日","动土择日"]:
                    return zhi in ["辰","戌","丑","未"]
                if t in ["安葬择日"]:
                    return zhi in ["子","丑","辰","未","申","酉"]
                return True

            # ===================== 与main完全一致：取命主参数 =====================
            ri_zhi = r["八字"][2][1]
            shengxiao = r["生肖"]
            sx_zhi = sx_map.get(shengxiao, "")
            chong_sx = chong_map.get(sx_zhi, "")
            chong_rz = chong_map.get(ri_zhi, "")

            today = datetime.now()
            sun_best, perfect = [], []
            conn = sqlite3.connect(resource_path("bazi_calendar.db"), timeout=10)
            cursor = conn.cursor()

            # ===================== 与main完全一致：遍历5年 =====================
            for i in range(1, 1826):
                dt = today + timedelta(days=i)
                date_str = dt.strftime("%Y-%m-%d")
                m, d = dt.month, dt.day

                # ----------------===== 【修复1】查询方式和main完全一样 =====----------------
                cursor.execute("SELECT 红砂,农历日 FROM calendar WHERE 国历 LIKE ? LIMIT 1", (date_str + "%",))
                res = cursor.fetchone()
                if not res: continue
                红砂值, lunar_day = res
                if str(红砂值).strip() == "红砂": continue

                # ----------------===== 【修复2】取当月初一干支（和main完全一样） =====----------------
                first_day = dt.replace(day=1)
                first_str = first_day.strftime("%Y-%m-%d")
                cursor.execute("SELECT 年 FROM calendar WHERE 国历 LIKE ? LIMIT 1", (first_str + "%",))
                f_res = cursor.fetchone()
                first_gz = f_res[0] if f_res else ""

                # ----------------===== 【修复3】从数据库取日干支（绝不推算） =====----------------
                cursor.execute("SELECT 纳音 FROM calendar WHERE 国历 LIKE ? LIMIT 1", (date_str + "%",))
                gz_res = cursor.fetchone()
                if not gz_res or len(gz_res[0]) != 2: continue
                day_gan, day_zhi = gz_res[0][0], gz_res[0][1]

                # ----------------===== 【修复4】过滤顺序和main完全一致 =====----------------
                if day_zhi == chong_sx or day_zhi == chong_rz: continue
                if (m,d) in sili_jue or d in sanniang or is_yue_po(m, day_zhi): continue
                if not get_huangdao(day_zhi): continue
                if not match_type(day_zhi, jiri_type): continue

                # 太阳星（和main完全一样）
                is_sun_day, sun_time = False, ""
                if first_gz in sun_star_table:
                    sun_days, sun_time = sun_star_table[first_gz]
                    if lunar_day in sun_days:
                        is_sun_day = True

                # 拼接结果（和main完全一样）
                base = f"{date_str}({day_gan}{day_zhi})"
                if is_sun_day:
                    sun_best.append(f"{base} ★吉 ★太阳吉时：{sun_time}")
                else:
                    perfect.append(f"{base} ★吉")

            conn.close()

            # 输出格式完全一致
            st.markdown("---")
            st.success(f"✅ {jiri_type} 筛选完成")
            if sun_best:
                st.markdown("<div style='text-align:center;color:#D4AF37;font-weight:bold;'>☀️【首选】太阳星+黄道吉日</div>", unsafe_allow_html=True)
                for s in sun_best[:3]: st.write(s)
            if perfect:
                st.markdown("<div style='text-align:center;color:#ff6666;font-weight:bold;'>🌟完美吉日</div>", unsafe_allow_html=True)
                for s in perfect[:5]: st.write(s)
            if not sun_best and not perfect:
                st.info("未找到符合条件的吉日")
