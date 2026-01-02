import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import calendar
import os
from datetime import date, datetime, timedelta

# --- KONFIGURACIJA ---
st.set_page_config(page_title="Tekaški Planer", layout="centered", page_icon="🏃‍♀️")
FILE_NAME = 'teki_data.csv'

# --- SLOVENSKA IMENA MESECEV ---
SLO_MONTHS = {
    1: "JANUAR", 2: "FEBRUAR", 3: "MAREC", 4: "APRIL", 5: "MAJ", 6: "JUNIJ",
    7: "JULIJ", 8: "AVGUST", 9: "SEPTEMBER", 10: "OKTOBER", 11: "NOVEMBER", 12: "DECEMBER"
}

# --- PODATKI ---
def load_data():
    if os.path.exists(FILE_NAME):
        df = pd.read_csv(FILE_NAME)
        df['dt'] = pd.to_datetime(df['date'])
        return df
    else:
        # ZAČETNI PODATKI
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
    # KATEGORIJE
    if 'cat1_name' not in st.session_state: st.session_state['cat1_name'] = "Tek (1.6km)"
    if 'cat1_color' not in st.session_state: st.session_state['cat1_color'] = "#3498db"
    if 'cat1_goal' not in st.session_state: st.session_state['cat1_goal'] = 1.6
    if 'cat1_active' not in st.session_state: st.session_state['cat1_active'] = True

    if 'cat2_name' not in st.session_state: st.session_state['cat2_name'] = "Letni Plan"
    if 'cat2_color' not in st.session_state: st.session_state['cat2_color'] = "#f1c40f"
    if 'cat2_goal' not in st.session_state: st.session_state['cat2_goal'] = 2500.0
    if 'cat2_active' not in st.session_state: st.session_state['cat2_active'] = True

    if 'cat3_name' not in st.session_state: st.session_state['cat3_name'] = "Strava Izziv"
    if 'cat3_color' not in st.session_state: st.session_state['cat3_color'] = "#FC4C02"
    if 'cat3_goal' not in st.session_state: st.session_state['cat3_goal'] = 300.0
    if 'cat3_active' not in st.session_state: st.session_state['cat3_active'] = True

    if 'cat4_name' not in st.session_state: st.session_state['cat4_name'] = "Hribi"
    if 'cat4_color' not in st.session_state: st.session_state['cat4_color'] = "#8e44ad"
    if 'cat4_goal' not in st.session_state: st.session_state['cat4_goal'] = 80000.0
    if 'cat4_active' not in st.session_state: st.session_state['cat4_active'] = True 
    
    # PRIKAZ STOLPCEV SPODAJ (Toggle)
    if 'breakdown_year' not in st.session_state: st.session_state['breakdown_year'] = True
    if 'breakdown_month' not in st.session_state: st.session_state['breakdown_month'] = True
    if 'breakdown_week' not in st.session_state: st.session_state['breakdown_week'] = True
    
    if 'extra_bars' not in st.session_state: st.session_state['extra_bars'] = ["cat3", "cat4"]

# --- APLIKACIJA (Brez naslova, direktno zavihki) ---
init_settings()

tab1, tab2, tab3 = st.tabs(["📊 Koledar", "➕ Vnos", "⚙️ Nastavitve"])

# --- ZAVIHEK 3: UREJANJE ---
with tab3:
    st.header("🎚️ Analiza & Cilji")
    
    # 1. GLAVNI CILJ
    st.caption("Glavni letni cilj (km):")
    st.session_state['cat2_goal'] = st.number_input("Letni cilj", value=st.session_state['cat2_goal'], step=50.0, label_visibility="collapsed")
    
    # 2. VKLOP/IZKLOP ANALIZ
    st.subheader("Kaj želiš spremljati?")
    c1, c2, c3 = st.columns(3)
    with c1: st.session_state['breakdown_year'] = st.checkbox("Letni", value=st.session_state['breakdown_year'])
    with c2: st.session_state['breakdown_month'] = st.checkbox("Mesečni", value=st.session_state['breakdown_month'])
    with c3: st.session_state['breakdown_week'] = st.checkbox("Tedenski", value=st.session_state['breakdown_week'])

    st.write("---")
    st.subheader("Dodatni stolpci")
    opts = {"cat1": st.session_state['cat1_name'], "cat3": st.session_state['cat3_name'], "cat4": st.session_state['cat4_name']}
    st.session_state['extra_bars'] = st.multiselect("Prikaži še:", options=["cat1", "cat3", "cat4"], 
                                                  format_func=lambda x: opts[x], default=st.session_state['extra_bars'])

    st.write("---")
    with st.expander("🎨 Barve in Imena Krogcev"):
        c1, c2 = st.columns([1,3])
        with c1: st.session_state['cat1_color'] = st.color_picker("B1", st.session_state['cat1_color'])
        with c2: st.session_state['cat1_name'] = st.text_input("Ime #1", st.session_state['cat1_name'])
        st.session_state['cat1_active'] = st.checkbox("Na koledarju #1", st.session_state['cat1_active'])
        st.write("-")

        c1, c2 = st.columns([1,3])
        with c1: st.session_state['cat2_color'] = st.color_picker("B2", st.session_state['cat2_color'])
        with c2: st.session_state['cat2_name'] = st.text_input("Ime #2", st.session_state['cat2_name'])
        st.session_state['cat2_active'] = st.checkbox("Na koledarju #2", st.session_state['cat2_active'])
        st.write("-")

        c1, c2 = st.columns([1,3])
        with c1: st.session_state['cat3_color'] = st.color_picker("B3", st.session_state['cat3_color'])
        with c2: st.session_state['cat3_name'] = st.text_input("Ime #3", st.session_state['cat3_name'])
        st.session_state['cat3_goal'] = st.number_input("Cilj #3", st.session_state['cat3_goal'])
        st.session_state['cat3_active'] = st.checkbox("Na koledarju #3", st.session_state['cat3_active'])
        st.write("-")

        c1, c2 = st.columns([1,3])
        with c1: st.session_state['cat4_color'] = st.color_picker("B4", st.session_state['cat4_color'])
        with c2: st.session_state['cat4_name'] = st.text_input("Ime #4", st.session_state['cat4_name'])
        st.session_state['cat4_goal'] = st.number_input("Cilj #4", st.session_state['cat4_goal'])
        st.session_state['cat4_active'] = st.checkbox("Na koledarju #4", st.session_state['cat4_active'])


# --- ZAVIHEK 2: VNOS ---
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

# --- ZAVIHEK 1: VIZUALIZACIJA ---
with tab1:
    df = load_data()
    if 'dt' not in df.columns: df['dt'] = pd.to_datetime(df['date'])
    
    # AVTOMATSKI MESEC: Ugotovi današnji mesec in leto
    today = date.today()
    current_year = today.year
    current_month = today.month
    
    # Filtriraj podatke SAMO za ta mesec (za koledar)
    df_month_view = df[(df['dt'].dt.year == current_year) & (df['dt'].dt.month == current_month)]
    
    data = {}
    for _, row in df_month_view.iterrows():
        is_today = (row['dt'].date() == today)
        data[row['dt'].day] = {'run': row['run'], 'elev': row['elev'], 'is_today': is_today}

    # SPREMENLJIVKE
    C1_N = st.session_state['cat1_name']; C1_C = st.session_state['cat1_color']; C1_G = st.session_state['cat1_goal']; C1_A = st.session_state['cat1_active']
    C2_N = st.session_state['cat2_name']; C2_C = st.session_state['cat2_color']; C2_G = st.session_state['cat2_goal']; C2_A = st.session_state['cat2_active']
    C3_N = st.session_state['cat3_name']; C3_C = st.session_state['cat3_color']; C3_G = st.session_state['cat3_goal']; C3_A = st.session_state['cat3_active']
    C4_N = st.session_state['cat4_name']; C4_C = st.session_state['cat4_color']; C4_G = st.session_state['cat4_goal']; C4_A = st.session_state['cat4_active']

    # IZRAČUNI
    day_of_year = today.timetuple().tm_yday
    day_of_month = today.day
    current_week_num = today.isocalendar()[1]
    current_weekday = today.isocalendar()[2] 

    # 1. LETNI (Gleda celo leto, ne samo mesec!)
    daily_avg_req = C2_G / 365.0 if (current_year % 4 != 0) else C2_G / 366.0
    year_accum = df[df['dt'].dt.year == current_year]['run'].sum()
    year_target_today = daily_avg_req * day_of_year

    # 2. MESEČNI (Dinamično glede na št dni v mesecu)
    days_in_month = calendar.monthrange(current_year, current_month)[1]
    month_goal_derived = daily_avg_req * days_in_month
    month_accum = df_month_view['run'].sum()
    month_target_today = daily_avg_req * day_of_month
    
    # 3. TEDENSKI
    week_goal_derived = daily_avg_req * 7
    df['week_num'] = df['dt'].dt.isocalendar().week
    week_accum = df[(df['dt'].dt.year == current_year) & (df['week_num'] == current_week_num)]['run'].sum()
    week_target_today = daily_avg_req * current_weekday

    # BANKING JUTRI
    surplus_year = year_accum - year_target_today
    next_goal_val = daily_avg_req - surplus_year

    # RISANJE
    C_BG = '#ecf0f1'; C_PENDING = '#e67e22'; C_TEXT = '#2c3e50'; C_GOOD = '#27ae60'; C_BAD = '#c0392b'
    
    # Višina grafa
    num_bars = 0
    if st.session_state['breakdown_year']: num_bars += 1
    if st.session_state['breakdown_month']: num_bars += 1
    if st.session_state['breakdown_week']: num_bars += 1
    num_bars += len(st.session_state['extra_bars'])

    fig_height = 13 + (num_bars * 1.2)
    fig, ax = plt.subplots(figsize=(12, fig_height))
    ax.set_xlim(0, 8); ax.set_ylim(-2 - num_bars, 7.5); ax.axis('off')

    # DINAMIČEN NASLOV (SLOVENŠČINA)
    month_name = SLO_MONTHS.get(current_month, "MESEC")
    ax.text(4, 7.2, f'{month_name} {current_year}', fontsize=24, fontweight='bold', ha='center', color=C_TEXT)
    
    # LEGENDA
    active_legends = []
    if C1_A: active_legends.append((C1_N, C1_C))
    if C2_A: active_legends.append((C2_N, C2_C))
    if C3_A: active_legends.append((C3_N, C3_C))
    if C4_A: active_legends.append((C4_N, C4_C))
    
    num_leg = len(active_legends)
    leg_y = 6.7
    if num_leg == 1: leg_pos = [4]
    elif num_leg == 2: leg_pos = [2.5, 5.5]
    elif num_leg == 3: leg_pos = [2, 4, 6]
    else: leg_pos = [1, 3, 5, 7]

    for i, (name, col) in enumerate(active_legends):
        px = leg_pos[i]
        ax.add_patch(patches.Circle((px, leg_y), 0.15, color=col))
        ax.text(px + 0.3, leg_y, name, va='center', fontsize=12)

    ax.plot([0, 8], [6.4, 6.4], color='#bdc3c7', lw=2)

    cal = calendar.monthcalendar(current_year, current_month)
    days_of_week = ['Pon', 'Tor', 'Sre', 'Čet', 'Pet', 'Sob', 'Ned', 'Vsota']
    for i, dname in enumerate(days_of_week):
        ax.text(i + 0.5, 6.1, dname, ha='center', va='center', fontsize=14, fontweight='bold', color='#34495e')

    current_day_real = today.day

    for week_idx, week in enumerate(cal):
        w_sum_dist = 0; w_sum_elev = 0
        for day_idx, day in enumerate(week):
            x = day_idx; y = 5 - week_idx
            rect = patches.Rectangle((x, y), 1, 1, fill=True, facecolor='white', edgecolor='#ecf0f1', linewidth=2)
            ax.add_patch(rect)
            if day == 0: continue
            
            ax.text(x + 0.05, y + 0.85, str(day), fontsize=14, fontweight='bold', color='#7f8c8d')
            
            # Dinamične pozicije
            if C1_A:
                pos_1 = (x+0.25, y+0.72); pos_2 = (x+0.25, y+0.56); pos_3 = (x+0.25, y+0.40); pos_4 = (x+0.25, y+0.24)
                f_sz = 9
            else:
                pos_1 = (0,0); pos_2 = (x+0.25, y+0.70); pos_3 = (x+0.25, y+0.50); pos_4 = (x+0.25, y+0.30)
                f_sz = 10.5
            
            # PODATKI
            if day in data:
                d = data[day]; val1 = d['run']; val2 = d['elev']; is_today = d['is_today']
                w_sum_dist += val1; w_sum_elev += val2
                
                # C1
                if C1_A:
                    ok = val1 >= C1_G
                    col = C1_C if ok else (C_PENDING if is_today else C_BG)
                    if ok: ax.add_patch(patches.Circle(pos_1, 0.07, color=col)); ax.text(pos_1[0], pos_1[1], '✓', ha='center', va='center', color='white', fontweight='bold', fontsize=9)
                    else: ax.add_patch(patches.Circle(pos_1, 0.07, fill=False, edgecolor=col, lw=2))
                    ax.text(pos_1[0]+0.15, pos_1[1], f"{val1:.1f} km", va='center', fontsize=9, fontweight='bold', color='#333')

                # C2
                if C2_A:
                    ok = val1 >= daily_avg_req
                    col = C2_C if ok else (C_PENDING if is_today else 'salmon')
                    if ok: ax.add_patch(patches.Circle(pos_2, 0.07, color=col)); ax.text(pos_2[0], pos_2[1], '✓', ha='center', va='center', color='white', fontweight='bold', fontsize=9)
                    else: ax.add_patch(patches.Circle(pos_2, 0.07, fill=False, edgecolor=col, lw=2)); ax.text(pos_2[0], pos_2[1], '!', ha='center', va='center', color=col, fontweight='bold', fontsize=9)
                    ax.text(pos_2[0]+0.15, pos_2[1], f"{val1:.1f}/{daily_avg_req:.1f}", va='center', fontsize=f_sz-1)

                # C3
                if C3_A:
                    avg_3 = C3_G / days_in_month # Preračun na dni v mesecu
                    ok = val1 >= avg_3
                    col = C3_C if ok else (C_PENDING if is_today else 'salmon')
                    if ok: ax.add_patch(patches.Circle(pos_3, 0.07, color=col))
                    else: ax.add_patch(patches.Circle(pos_3, 0.07, fill=False, edgecolor=col, lw=2))
                    ax.text(pos_3[0]+0.15, pos_3[1], f"{val1:.1f}/{avg_3:.1f}", va='center', fontsize=f_sz-1)

                # C4
                if C4_A and val2 > 0:
                     ax.add_patch(patches.Circle(pos_4, 0.07, color=C4_C))
                     ax.text(pos_4[0]+0.15, pos_4[1], f"+{int(val2)}", va='center', fontsize=f_sz, color=C4_C)
            
            # NAPOVED
            elif day > today.day:
                is_tomorrow = (day == today.day + 1)
                
                if C2_A: # Letni plan napoved
                    val_show = next_goal_val if is_tomorrow else daily_avg_req
                    col_txt = C_GOOD if next_goal_val <= daily_avg_req else C_BAD
                    if not is_tomorrow: col_txt = '#95a5a6'
                    
                    ax.add_patch(patches.Circle(pos_2, 0.07, color='#f2f4f4'))
                    ax.text(pos_2[0]+0.15, pos_2[1], f"Cilj: {val_show:.1f}", va='center', fontsize=f_sz-1, fontweight='bold', color=col_txt)

        if w_sum_dist > 0:
            ax.text(7.5, 5 - week_idx + 0.6, f"{w_sum_dist:.1f} km", ha='center', va='center', fontsize=11, fontweight='bold', color='#555')
            if w_sum_elev > 0:
                ax.text(7.5, 5 - week_idx + 0.3, f"{int(w_sum_elev)} m", ha='center', va='center', fontsize=11, fontweight='bold', color=C4_C)

    # SPODNJI STOLPCI
    ax.plot([0, 8], [-0.2, -0.2], color='#bdc3c7', lw=2) 
    ax.text(4, -0.8, 'RAZČLENITEV CILJEV', fontsize=18, fontweight='bold', ha='center', color='#2c3e50')
    
    bar_x = 0.5; bar_width = 7; bar_height = 0.6; y_start = -1.8
    
    def draw_bar(y, val, goal, color, label, target_val=None, unit='km'):
        ax.add_patch(patches.Rectangle((bar_x, y), bar_width, bar_height, facecolor=C_BG, edgecolor='none'))
        pct = val / goal if goal > 0 else 0; pct = 1 if pct > 1 else pct
        ax.add_patch(patches.Rectangle((bar_x, y), bar_width * pct, bar_height, facecolor=color, edgecolor='none'))
        ax.text(bar_x, y + 0.7, f"{label}", fontsize=12, fontweight='bold', color='#555')
        ax.text(bar_x + bar_width, y + 0.7, f"{val:.1f} / {goal:.0f} {unit}", fontsize=12, fontweight='bold', color='black', ha='right')
        ax.text(bar_x + bar_width, y + 0.1, f"Manjka: {goal - val:.1f}", fontsize=10, color='red', ha='right')
        
        if target_val is not None:
            t_pct = target_val / goal if goal > 0 else 0
            if t_pct > 1: t_pct = 1
            t_pos_x = bar_x + (bar_width * t_pct)
            ax.plot([t_pos_x, t_pos_x], [y, y + bar_height], color='black', lw=2, linestyle='--')
            ax.text(t_pos_x, y - 0.2, f"Plan: {target_val:.0f}", ha='center', fontsize=9, fontweight='bold', color='black')

    current_y = y_start
    
    if st.session_state['breakdown_year']:
        draw_bar(current_y, year_accum, C2_G, C2_C, f"LETNI CILJ ({C2_N})", target_val=year_target_today)
        current_y -= 1.4
    
    if st.session_state['breakdown_month']:
        draw_bar(current_y, month_accum, month_goal_derived, C2_C, f"MESEČNI CILJ (Iz letnega)", target_val=month_target_today)
        current_y -= 1.4
        
    if st.session_state['breakdown_week']:
        draw_bar(current_y, week_accum, week_goal_derived, C2_C, f"TEDENSKI CILJ (Iz letnega)", target_val=week_target_today)
        current_y -= 1.4

    extras = st.session_state['extra_bars']
    if "cat1" in extras: draw_bar(current_y, month_accum, C1_G * days_in_month, C1_C, C1_N); current_y -= 1.4
    if "cat3" in extras: draw_bar(current_y, month_accum, C3_G, C3_C, C3_N); current_y -= 1.4
    if "cat4" in extras: draw_bar(current_y, df['elev'].sum(), C4_G, C4_C, C4_N, unit="m"); current_y -= 1.4

    st.pyplot(fig)
