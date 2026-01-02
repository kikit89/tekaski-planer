import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import calendar
import os
import uuid
from datetime import date, datetime

# --- KONFIGURACIJA ---
st.set_page_config(page_title="Tekaški Planer", layout="centered", page_icon="🏃‍♀️")
FILE_NAME = 'teki_data.csv'

# --- TVOJ KOLEDAR TEKEM ---
RACE_CALENDAR_URL = "https://calendar.google.com/calendar/u/0/embed?color=%2342d692&src=ebc83d7c094e5c61db2b0682a4da13734af4f2f381bafec7ccb37df56bdb1c92@group.calendar.google.com"

# --- PODATKI ---
def load_data():
    if os.path.exists(FILE_NAME):
        df = pd.read_csv(FILE_NAME)
        df['dt'] = pd.to_datetime(df['date'])
        return df
    else:
        data = {
            'date': ['2026-01-01', '2026-01-02'],
            'run': [6.93, 8.34],
            'walk': [1.6, 1.6],
            'elev': [76, 57],
            'note': ['Začetek', 'Nadaljevanje']
        }
        df = pd.DataFrame(data)
        df['dt'] = pd.to_datetime(df['date'])
        return df

def save_data(df):
    df_save = df.drop(columns=['dt'])
    df_save.to_csv(FILE_NAME, index=False)

def init_settings():
    if 'goals_list' not in st.session_state:
        st.session_state['goals_list'] = [
            {'id': 'g1', 'name': 'Letni Plan', 'color': '#f1c40f', 'goal': 2500.0, 'type': 'Letni', 'unit': 'km', 'active': True, 'show_progress': True},
            {'id': 'g2', 'name': 'Strava Izziv', 'color': '#FC4C02', 'goal': 300.0, 'type': 'Mesečni', 'unit': 'km', 'active': True, 'show_progress': True},
            {'id': 'g3', 'name': 'Hribi', 'color': '#8e44ad', 'goal': 80000.0, 'type': 'Letni', 'unit': 'm', 'active': True, 'show_progress': False},
        ]
    if 'show_sub_month' not in st.session_state: st.session_state['show_sub_month'] = True
    if 'show_sub_week' not in st.session_state: st.session_state['show_sub_week'] = True

# --- APLIKACIJA ---
init_settings()

tab1, tab2, tab_race, tab3 = st.tabs(["📊 Koledar", "➕ Vnos", "🏆 Tekme", "⚙️ Nastavitve"])

# ==============================================================================
# ZAVIHEK: TEKME
# ==============================================================================
with tab_race:
    st.header("🏆 Koledar Tekem")
    try:
        components.iframe(RACE_CALENDAR_URL, height=600, scrolling=True)
    except Exception as e:
        st.error("Napaka pri nalaganju koledarja.")

# ==============================================================================
# ZAVIHEK: NASTAVITVE
# ==============================================================================
with tab3:
    st.header("📋 Urejanje")
    
    st.subheader("1. Podrobnosti analiz")
    c1, c2 = st.columns(2)
    with c1: st.session_state['show_sub_month'] = st.checkbox("Mesečna analiza", value=st.session_state['show_sub_month'])
    with c2: st.session_state['show_sub_week'] = st.checkbox("Tedenska analiza", value=st.session_state['show_sub_week'])
    st.write("---")

    st.subheader("2. Moji Cilji")
    goals_to_remove = []
    for i, g in enumerate(st.session_state['goals_list']):
        with st.expander(f"{g['name']}", expanded=False):
            c1, c2 = st.columns([1, 3])
            with c1: g['color'] = st.color_picker("Barva", g['color'], key=f"c_{g['id']}")
            with c2: g['name'] = st.text_input("Ime", g['name'], key=f"n_{g['id']}")
            
            c3, c4, c5 = st.columns(3)
            with c3: g['goal'] = st.number_input("Cilj", value=float(g['goal']), key=f"g_{g['id']}")
            with c4: g['type'] = st.selectbox("Tip", ["Letni", "Mesečni"], index=0 if g['type']=="Letni" else 1, key=f"t_{g['id']}")
            with c5: g['unit'] = st.selectbox("Enota", ["km", "m"], index=0 if g.get('unit','km')=="km" else 1, key=f"u_{g['id']}")
            
            st.caption("Prikaz:")
            col_a, col_b = st.columns(2)
            with col_a:
                g['active'] = st.checkbox("Na koledarju", value=g.get('active', True), key=f"a_{g['id']}")
            with col_b:
                g['show_progress'] = st.checkbox("V spodnjem pregledu", value=g.get('show_progress', True), key=f"sp_{g['id']}")
            
            if st.button(f"🗑️ Izbriši cilj", key=f"del_{g['id']}"):
                goals_to_remove.append(i)

    if goals_to_remove:
        for index in sorted(goals_to_remove, reverse=True):
            del st.session_state['goals_list'][index]
        st.rerun()

    st.subheader("➕ Dodaj nov cilj")
    with st.form("new_goal"):
        n_name = st.text_input("Ime")
        c1, c2 = st.columns(2)
        with c1: n_goal = st.number_input("Vrednost", value=100.0)
        with c2: n_unit = st.selectbox("Enota", ["km", "m"])
        n_type = st.selectbox("Tip", ["Mesečni", "Letni"])
        n_color = st.color_picker("Barva", "#00ff00")
        
        if st.form_submit_button("Dodaj"):
            new_id = str(uuid.uuid4())[:8]
            st.session_state['goals_list'].append({
                'id': new_id, 'name': n_name, 'color': n_color, 'goal': n_goal, 
                'type': n_type, 'unit': n_unit, 'active': True, 'show_progress': True
            })
            st.rerun()

# ==============================================================================
# ZAVIHEK: VNOS
# ==============================================================================
with tab2:
    st.header("Nov vnos")
    with st.form("entry"):
        d_date = st.date_input("Datum", value=date.today())
        run = st.number_input("Razdalja (km)", min_value=0.0, step=0.1, format="%.2f")
        elev = st.number_input("Višina (m)", min_value=0, step=10)
        note = st.text_input("Opomba")
        
        if st.form_submit_button("Shrani"):
            df = load_data()
            d_str = d_date.strftime("%Y-%m-%d")
            if d_str in df['date'].values:
                df.loc[df['date'] == d_str, ['run', 'elev', 'note']] = [run, elev, note]
                st.toast(f"Posodobljeno!")
            else:
                new = pd.DataFrame({'date': [d_str], 'run': [run], 'walk': [0], 'elev': [elev], 'note': [note]})
                new['dt'] = pd.to_datetime(new['date'])
                df = pd.concat([df, new], ignore_index=True)
                st.toast(f"Shranjeno!")
            save_data(df)

# ==============================================================================
# ZAVIHEK: VIZUALIZACIJA (KOLEDAR + ANALIZA)
# ==============================================================================
with tab1:
    df = load_data()
    if 'dt' not in df.columns: df['dt'] = pd.to_datetime(df['date'])
    
    today = date.today()
    current_year = today.year
    current_month = today.month
    
    df_month_view = df[(df['dt'].dt.year == current_year) & (df['dt'].dt.month == current_month)]
    
    data = {}
    for _, row in df_month_view.iterrows():
        data[row['dt'].day] = {'run': row['run'], 'elev': row['elev'], 'is_today': (row['dt'].date() == today)}

    # Parametri
    day_of_year = today.timetuple().tm_yday
    day_of_month = today.day
    days_in_year = 366 if calendar.isleap(current_year) else 365
    days_in_month = calendar.monthrange(current_year, current_month)[1]
    
    current_week_num = today.isocalendar()[1]
    current_weekday_iso = today.isocalendar()[2] 
    
    active_goals_cal = [g for g in st.session_state['goals_list'] if g.get('active', True)]
    
    # --- PRED-IZRAČUN ---
    goals_calc = []
    for g in st.session_state['goals_list']:
        g_val = g['goal']
        unit_key = 'elev' if g['unit'] == 'm' else 'run'
        
        if g['type'] == 'Letni':
            daily_avg = g_val / days_in_year
            accum_total = df[df['dt'].dt.year == current_year][unit_key].sum()
            target_total_today = daily_avg * day_of_year
        else:
            daily_avg = g_val / days_in_month
            accum_total = df_month_view[unit_key].sum()
            target_total_today = daily_avg * day_of_month
            
        surplus = accum_total - target_total_today
        goal_tomorrow = daily_avg - surplus
        if goal_tomorrow < 0: goal_tomorrow = 0
        
        goals_calc.append({
            'meta': g,
            'daily_avg': daily_avg,
            'goal_tomorrow': goal_tomorrow,
            'surplus': surplus,
            'accum_total': accum_total
        })

    # --- RISANJE ---
    C_BG = '#ecf0f1'; C_PENDING = '#e67e22'; C_TEXT = '#2c3e50'; C_GOOD = '#27ae60'; C_BAD = '#c0392b'
    
    # DINAMIČNA VIŠINA (ZELO POMEMBNO)
    # Preštejemo vrstice, ki jih bomo narisali spodaj
    visible_rows = 0
    for g in st.session_state['goals_list']:
        if g.get('show_progress', True):
            visible_rows += 1
            if st.session_state['show_sub_month'] and g['type'] == 'Letni': visible_rows += 1
            if st.session_state['show_sub_week']: visible_rows += 1

    # Base height = Koledar (cca 12) + (št_vrstic * višina_vrstice)
    # Zmanjšal sem faktorje za bolj kompakten izgled
    fig_height = 13 + (visible_rows * 1.0) 

    fig, ax = plt.subplots(figsize=(12, fig_height))
    
    # Y-limit se prilagodi številu vrstic. 
    # Če je visible_rows = 5, rabimo cca -5 prostora spodaj
    bottom_limit = -2 - (visible_rows * 1.0)
    ax.set_xlim(0, 7); ax.set_ylim(bottom_limit, 7.5); ax.axis('off')

    SLO_MONTHS = {1:"JANUAR", 2:"FEBRUAR", 3:"MAREC", 4:"APRIL", 5:"MAJ", 6:"JUNIJ", 7:"JULIJ", 8:"AVGUST", 9:"SEPTEMBER", 10:"OKTOBER", 11:"NOVEMBER", 12:"DECEMBER"}
    month_name = SLO_MONTHS.get(current_month, "")
    ax.text(3.5, 7.2, f'{month_name} {current_year}', fontsize=30, fontweight='bold', ha='center', color=C_TEXT)
    
    active_len = len(active_goals_cal)
    leg_y = 6.7
    if active_len > 0:
        step = 7 / (active_len + 1)
        for i, g in enumerate(active_goals_cal):
            px = step * (i + 1)
            ax.add_patch(patches.Circle((px, leg_y), 0.15, color=g['color']))
            ax.text(px + 0.3, leg_y, g['name'], va='center', fontsize=14)

    ax.plot([0, 7], [6.4, 6.4], color='#bdc3c7', lw=2)

    cal = calendar.monthcalendar(current_year, current_month)
    days_of_week = ['Pon', 'Tor', 'Sre', 'Čet', 'Pet', 'Sob', 'Ned']
    for i, dname in enumerate(days_of_week):
        ax.text(i + 0.5, 6.1, dname, ha='center', va='center', fontsize=16, fontweight='bold', color='#34495e')

    current_day_real = today.day

    for week_idx, week in enumerate(cal):
        w_sum_dist = 0; w_sum_elev = 0
        for day_idx, day in enumerate(week):
            x = day_idx; y = 5 - week_idx
            rect = patches.Rectangle((x, y), 1, 1, fill=True, facecolor='white', edgecolor='#ecf0f1', linewidth=2)
            ax.add_patch(rect)
            if day == 0: continue
            
            ax.text(x + 0.05, y + 0.85, str(day), fontsize=16, fontweight='bold', color='#7f8c8d')
            
            if active_len > 0:
                spacing = 0.75 / max(active_len, 1)
                daily_vals = data.get(day, {'run':0, 'elev':0, 'is_today':False})
                val_km = daily_vals['run']; val_m = daily_vals['elev']; is_today = daily_vals['is_today']
                w_sum_dist += val_km; w_sum_elev += val_m
                
                for i, g in enumerate(active_goals_cal):
                    calc = next((c for c in goals_calc if c['meta']['id'] == g['id']), None)
                    if not calc: continue

                    dot_y = (y + 0.70) - (i * spacing)
                    current_val = val_m if g['unit']=='m' else val_km
                    
                    if g['unit'] == 'm':
                         if current_val > 0:
                             ax.text(x+0.5, dot_y, f"{int(current_val)} m", ha='center', va='center', fontsize=11, color=g['color'], fontweight='bold')
                         continue 

                    if day <= current_day_real:
                        daily_avg = calc['daily_avg']
                        has_data = current_val > 0
                        txt_col = C_GOOD if current_val >= daily_avg else C_BAD
                        
                        if has_data or is_today:
                            ok = current_val >= daily_avg
                            col = g['color'] if ok else (C_PENDING if is_today else 'salmon')
                            
                            if ok:
                                ax.add_patch(patches.Circle((x+0.15, dot_y), 0.06, color=g['color']))
                                if active_len <= 4: 
                                    ax.text(x+0.15, dot_y, '✓', ha='center', va='center', color='white', fontsize=7, fontweight='bold')
                            else:
                                ax.add_patch(patches.Circle((x+0.15, dot_y), 0.06, fill=False, edgecolor=col, lw=2))
                            
                            label_txt = f"{current_val:.1f} / {daily_avg:.1f}"
                            ax.text(x+0.25, dot_y, label_txt, va='center', fontsize=10, color=txt_col, fontweight='bold')

                    elif day == current_day_real + 1:
                        target_tomorrow = calc['goal_tomorrow']
                        standard_avg = calc['daily_avg']
                        txt_col = C_GOOD if target_tomorrow <= standard_avg else C_BAD
                        ax.text(x+0.5, dot_y, f"Cilj: {target_tomorrow:.1f}", ha='center', va='center', fontsize=10, fontweight='bold', color=txt_col)

                    else:
                        standard_avg = calc['daily_avg']
                        ax.add_patch(patches.Circle((x+0.15, dot_y), 0.04, color='#ecf0f1'))
                        ax.text(x+0.25, dot_y, f"{standard_avg:.1f}", va='center', fontsize=9, color='#95a5a6')

    # STOLPCI SPODAJ
    ax.plot([0, 7], [-0.2, -0.2], color='#bdc3c7', lw=2) 
    
    # NASLOV "NAPREDEK" MALO VIŠJE
    ax.text(3.5, -0.7, 'NAPREDEK', fontsize=20, fontweight='bold', ha='center', color='#2c3e50')
    
    # ZAČETEK STOLPCEV
    bar_x = 0.2; bar_width = 6.6; bar_height = 0.5
    y_cursor = -1.5 # Začnemo višje, takoj pod naslovom
    
    def draw_bar_status(y, val, goal, color, label, target_val=None, unit='km'):
        ax.add_patch(patches.Rectangle((bar_x, y), bar_width, bar_height, facecolor=C_BG, edgecolor='none'))
        pct = val / goal if goal > 0 else 0
        if pct > 1: pct = 1
        ax.add_patch(patches.Rectangle((bar_x, y), bar_width * pct, bar_height, facecolor=color, edgecolor='none'))
        
        status_txt = ""
        status_col = 'black'
        if target_val is not None:
            diff = val - target_val
            sign = "+" if diff >= 0 else ""
            status_txt = f"{sign}{diff:.1f} {unit}"
            status_col = C_GOOD if diff >= 0 else C_BAD 
            
            tpct = target_val / goal if goal > 0 else 0
            if tpct > 1: tpct = 1
            tpos = bar_x + (bar_width * tpct)
            ax.plot([tpos, tpos], [y, y+bar_height], color='black', alpha=0.5, lw=1.5, linestyle=':')

        ax.text(bar_x, y + 0.6, label, fontsize=13, fontweight='bold', color='#555')
        right_txt = f"{val:.1f}/{goal:.0f} {unit}"
        ax.text(bar_x + bar_width, y + 0.6, right_txt, fontsize=13, fontweight='bold', color='black', ha='right')
        
        if status_txt:
            ax.text(bar_x + bar_width, y + 0.1, f"Stanje: {status_txt}", fontsize=11, fontweight='bold', color=status_col, ha='right')

    for gd in goals_calc:
        meta = gd['meta']
        if not meta.get('show_progress', True): continue

        accum = gd['accum_total'] 
        days_passed = day_of_year if meta['type'] == 'Letni' else day_of_month
        main_target = gd['daily_avg'] * days_passed
        
        # Glavni
        draw_bar_status(y_cursor, accum, meta['goal'], meta['color'], f"{meta['name']}", target_val=main_target, unit=meta['unit'])
        y_cursor -= 0.9 # ZELO KOMPAKTEN RAZMAK (prej 1.2 ali 1.4)
        
        # Mesec
        if st.session_state['show_sub_month'] and meta['type'] == 'Letni':
            month_goal = gd['daily_avg'] * days_in_month
            month_accum = df_month_view['elev' if meta['unit']=='m' else 'run'].sum()
            month_target = gd['daily_avg'] * day_of_month
            draw_bar_status(y_cursor, month_accum, month_goal, meta['color'], f"{meta['name']} (Ta mesec)", target_val=month_target, unit=meta['unit'])
            y_cursor -= 0.9

        # Teden (FIX 1. TEDEN)
        if st.session_state['show_sub_week']:
            week_goal_display = gd['daily_avg'] * 7
            
            if current_week_num == 1:
                jan1_weekday = date(current_year, 1, 1).isocalendar()[2]
                active_days_total = 7 - jan1_weekday + 1
                week_goal_display = gd['daily_avg'] * active_days_total
                
            df['week_num'] = df['dt'].dt.isocalendar().week
            unit_key = 'elev' if meta['unit']=='m' else 'run'
            week_accum = df[(df['dt'].dt.year == current_year) & (df['week_num'] == current_week_num)][unit_key].sum()
            
            if current_week_num == 1:
                jan1_weekday = date(current_year, 1, 1).isocalendar()[2]
                active_days_so_far = current_weekday_iso - jan1_weekday + 1
                if active_days_so_far < 0: active_days_so_far = 0
                week_target_marker = gd['daily_avg'] * active_days_so_far
            else:
                week_target_marker = gd['daily_avg'] * current_weekday_iso
                
            draw_bar_status(y_cursor, week_accum, week_goal_display, meta['color'], f"{meta['name']} (Ta teden)", target_val=week_target_marker, unit=meta['unit'])
            y_cursor -= 0.9
            
        y_cursor -= 0.15 # Minimalen razmak med skupinami (prej 0.3)

    st.pyplot(fig)
