import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import calendar
import os
from datetime import date, timedelta

# --- KONFIGURACIJA ---
st.set_page_config(page_title="Moj Tekaški Planer", layout="centered", page_icon="🏃‍♀️")
FILE_NAME = 'teki_data.csv'

# --- PODATKI ---
def load_data():
    if os.path.exists(FILE_NAME):
        return pd.read_csv(FILE_NAME)
    else:
        # ZAČETNI PODATKI (Varnostna kopija)
        data = {
            'date': ['2026-01-01', '2026-01-02'],
            'run': [6.93, 8.34],
            'walk': [1.6, 1.6],
            'elev': [76, 57],
            'note': ['Začetek', 'Nadaljevanje']
        }
        return pd.DataFrame(data)

def save_data(df):
    df.to_csv(FILE_NAME, index=False)

def init_settings():
    # --- Nastavitve kategorij ---
    # KROGREC 1: Dnevni Minimum
    if 'cat1_name' not in st.session_state: st.session_state['cat1_name'] = "Tek (1.6km)"
    if 'cat1_color' not in st.session_state: st.session_state['cat1_color'] = "#3498db"
    if 'cat1_goal' not in st.session_state: st.session_state['cat1_goal'] = 1.6
    if 'cat1_active' not in st.session_state: st.session_state['cat1_active'] = True

    # KROGREC 2: Letni Cilj (Banking)
    if 'cat2_name' not in st.session_state: st.session_state['cat2_name'] = "Letni Plan"
    if 'cat2_color' not in st.session_state: st.session_state['cat2_color'] = "#f1c40f"
    if 'cat2_goal' not in st.session_state: st.session_state['cat2_goal'] = 2500.0
    if 'cat2_active' not in st.session_state: st.session_state['cat2_active'] = True

    # KROGREC 3: Mesečni Cilj
    if 'cat3_name' not in st.session_state: st.session_state['cat3_name'] = "Strava Izziv"
    if 'cat3_color' not in st.session_state: st.session_state['cat3_color'] = "#FC4C02"
    if 'cat3_goal' not in st.session_state: st.session_state['cat3_goal'] = 300.0
    if 'cat3_active' not in st.session_state: st.session_state['cat3_active'] = True

    # KROGREC 4: Višinci
    if 'cat4_name' not in st.session_state: st.session_state['cat4_name'] = "Hribi"
    if 'cat4_color' not in st.session_state: st.session_state['cat4_color'] = "#8e44ad"
    if 'cat4_goal' not in st.session_state: st.session_state['cat4_goal'] = 80000.0
    if 'cat4_active' not in st.session_state: st.session_state['cat4_active'] = True # Na koledarju
    
    if 'show_bars' not in st.session_state: 
        st.session_state['show_bars'] = ["cat2", "cat3", "cat4"]

# --- APLIKACIJA ---
st.title("🏃‍♀️ Pametni Planer")
init_settings()

tab1, tab2, tab3 = st.tabs(["📊 Koledar", "➕ Vnos", "⚙️ Urejanje"])

# --- ZAVIHEK 3: UREJANJE ---
with tab3:
    st.header("Nastavitve")
    
    with st.expander(f"🔹 {st.session_state['cat1_name']}", expanded=False):
        c1, c2 = st.columns([1, 3])
        with c1: st.session_state['cat1_color'] = st.color_picker("Barva #1", st.session_state['cat1_color'])
        with c2: st.session_state['cat1_name'] = st.text_input("Ime #1", st.session_state['cat1_name'])
        st.session_state['cat1_goal'] = st.number_input("Cilj 1 (Dnevni km)", value=st.session_state['cat1_goal'])
        st.session_state['cat1_active'] = st.checkbox("Prikaži na koledarju #1", value=st.session_state['cat1_active'])

    with st.expander(f"🔸 {st.session_state['cat2_name']}", expanded=False):
        c1, c2 = st.columns([1, 3])
        with c1: st.session_state['cat2_color'] = st.color_picker("Barva #2", st.session_state['cat2_color'])
        with c2: st.session_state['cat2_name'] = st.text_input("Ime #2", st.session_state['cat2_name'])
        st.session_state['cat2_goal'] = st.number_input("Cilj 2 (Letni km)", value=st.session_state['cat2_goal'])
        st.session_state['cat2_active'] = st.checkbox("Prikaži na koledarju #2", value=st.session_state['cat2_active'])

    with st.expander(f"🔸 {st.session_state['cat3_name']}", expanded=False):
        c1, c2 = st.columns([1, 3])
        with c1: st.session_state['cat3_color'] = st.color_picker("Barva #3", st.session_state['cat3_color'])
        with c2: st.session_state['cat3_name'] = st.text_input("Ime #3", st.session_state['cat3_name'])
        st.session_state['cat3_goal'] = st.number_input("Cilj 3 (Mesečni km)", value=st.session_state['cat3_goal'])
        st.session_state['cat3_active'] = st.checkbox("Prikaži na koledarju #3", value=st.session_state['cat3_active'])

    with st.expander(f"🔸 {st.session_state['cat4_name']}", expanded=False):
        c1, c2 = st.columns([1, 3])
        with c1: st.session_state['cat4_color'] = st.color_picker("Barva #4", st.session_state['cat4_color'])
        with c2: st.session_state['cat4_name'] = st.text_input("Ime #4", st.session_state['cat4_name'])
        st.session_state['cat4_goal'] = st.number_input("Cilj 4 (Letni Višinci)", value=st.session_state['cat4_goal'])
        st.session_state['cat4_active'] = st.checkbox("Prikaži na koledarju #4", value=st.session_state['cat4_active'])

    st.write("---")
    opts = {"cat1": st.session_state['cat1_name'], "cat2": st.session_state['cat2_name'], 
            "cat3": st.session_state['cat3_name'], "cat4": st.session_state['cat4_name']}
    st.session_state['show_bars'] = st.multiselect("Stolpci na dnu:", options=["cat1", "cat2", "cat3", "cat4"], 
                                                 format_func=lambda x: opts[x], default=st.session_state['show_bars'])

# --- ZAVIHEK 2: VNOS ---
with tab2:
    st.header("Nov vnos")
    with st.form("entry"):
        d_date = st.date_input("Datum", value=date.today())
        st.caption(f"Vnos kilometrov:")
        run = st.number_input("Razdalja (km)", min_value=0.0, step=0.1, format="%.2f")
        st.caption(f"Vnos višincev:")
        elev = st.number_input("Višina (m)", min_value=0, step=10)
        note = st.text_input("Opomba")
        
        if st.form_submit_button("Shrani"):
            df = load_data()
            d_str = d_date.strftime("%Y-%m-%d")
            if d_str in df['date'].values:
                df.loc[df['date'] == d_str, ['run', 'elev', 'note']] = [run, elev, note]
                st.success(f"Posodobljeno!")
            else:
                new = pd.DataFrame({'date': [d_str], 'run': [run], 'walk': [0], 'elev': [elev], 'note': [note]})
                df = pd.concat([df, new], ignore_index=True)
                st.success(f"Shranjeno!")
            save_data(df)

# --- ZAVIHEK 1: VIZUALIZACIJA ---
with tab1:
    df = load_data()
    df['dt'] = pd.to_datetime(df['date'])
    df_jan = df[(df['dt'].dt.year == 2026) & (df['dt'].dt.month == 1)]
    
    data = {}
    total_run_real = 0
    for _, row in df_jan.iterrows():
        is_today = (row['dt'].date() == date.today())
        data[row['dt'].day] = {'run': row['run'], 'elev': row['elev'], 'is_today': is_today}

    # Nastavitve
    C1_N = st.session_state['cat1_name']; C1_C = st.session_state['cat1_color']; C1_G = st.session_state['cat1_goal']; C1_A = st.session_state['cat1_active']
    C2_N = st.session_state['cat2_name']; C2_C = st.session_state['cat2_color']; C2_G = st.session_state['cat2_goal']; C2_A = st.session_state['cat2_active']
    C3_N = st.session_state['cat3_name']; C3_C = st.session_state['cat3_color']; C3_G = st.session_state['cat3_goal']; C3_A = st.session_state['cat3_active']
    C4_N = st.session_state['cat4_name']; C4_C = st.session_state['cat4_color']; C4_G = st.session_state['cat4_goal']; C4_A = st.session_state['cat4_active']

    # --- BANKING LOGIC ---
    today_day_year = date.today().timetuple().tm_yday
    today_day_month = date.today().day
    
    # 1. LETNI (K2)
    daily_avg_2 = C2_G / 365.0
    target_today_2 = daily_avg_2 * today_day_year
    actual_year = df[df['dt'].dt.year == 2026]['run'].sum()
    surplus_2 = actual_year - target_today_2
    next_goal_2 = daily_avg_2 - surplus_2 # To je cilj SAMO za jutri

    # 2. MESEČNI (K3)
    daily_avg_3 = C3_G / 31.0
    target_today_3 = daily_avg_3 * today_day_month
    actual_month = df_jan[df_jan['dt'].dt.date <= date.today()]['run'].sum()
    surplus_3 = actual_month - target_today_3
    next_goal_3 = daily_avg_3 - surplus_3

    # --- RISANJE ---
    C_BG = '#ecf0f1'; C_PENDING = '#e67e22'; C_TEXT = '#2c3e50'; C_GOOD = '#27ae60'; C_BAD = '#c0392b'
    
    active_bars = st.session_state['show_bars']
    fig_height = 13 + (len(active_bars) * 1)
    fig, ax = plt.subplots(figsize=(12, fig_height))
    ax.set_xlim(0, 8); ax.set_ylim(-2 - len(active_bars), 7.5); ax.axis('off')

    ax.text(4, 7.2, 'JANUAR 2026', fontsize=24, fontweight='bold', ha='center', color=C_TEXT)
    
    # --- CENTRIRANA LEGENDA ---
    active_legends = []
    if C1_A: active_legends.append((C1_N, C1_C))
    if C2_A: active_legends.append((C2_N, C2_C))
    if C3_A: active_legends.append((C3_N, C3_C))
    if C4_A: active_legends.append((C4_N, C4_C))
    
    num_leg = len(active_legends)
    leg_y = 6.7
    # Logika za pozicije: Če je 1 (sredina=4), če 2 (2.5, 5.5), če 3 (2, 4, 6), če 4 (1, 3, 5, 7)
    if num_leg == 1: leg_pos = [4]
    elif num_leg == 2: leg_pos = [2.5, 5.5]
    elif num_leg == 3: leg_pos = [2, 4, 6]
    else: leg_pos = [1, 3, 5, 7]

    for i, (name, col) in enumerate(active_legends):
        px = leg_pos[i]
        ax.add_patch(patches.Circle((px, leg_y), 0.15, color=col))
        ax.text(px + 0.3, leg_y, name, va='center', fontsize=12)

    ax.plot([0, 8], [6.4, 6.4], color='#bdc3c7', lw=2)

    cal = calendar.monthcalendar(2026, 1)
    days_of_week = ['Pon', 'Tor', 'Sre', 'Čet', 'Pet', 'Sob', 'Ned', 'Vsota']
    for i, dname in enumerate(days_of_week):
        ax.text(i + 0.5, 6.1, dname, ha='center', va='center', fontsize=14, fontweight='bold', color='#34495e')

    current_day_real = date.today().day

    for week_idx, week in enumerate(cal):
        w_sum_dist = 0; w_sum_elev = 0
        for day_idx, day in enumerate(week):
            x = day_idx; y = 5 - week_idx
            rect = patches.Rectangle((x, y), 1, 1, fill=True, facecolor='white', edgecolor='#ecf0f1', linewidth=2)
            ax.add_patch(rect)
            if day == 0: continue
            
            ax.text(x + 0.05, y + 0.85, str(day), fontsize=14, fontweight='bold', color='#7f8c8d')
            
            # Dinamične pozicije znotraj dneva
            if C1_A:
                pos_1 = (x+0.25, y+0.72); pos_2 = (x+0.25, y+0.56); pos_3 = (x+0.25, y+0.40); pos_4 = (x+0.25, y+0.24)
                f_sz = 9
            else:
                pos_1 = (0,0); pos_2 = (x+0.25, y+0.70); pos_3 = (x+0.25, y+0.50); pos_4 = (x+0.25, y+0.30)
                f_sz = 10.5
            
            # 1. PRETEKLOST (Podatki obstajajo)
            if day in data:
                d = data[day]; val1 = d['run']; val2 = d['elev']; is_today = d['is_today']
                w_sum_dist += val1; w_sum_elev += val2
                
                # CILJ 1
                if C1_A:
                    ok = val1 >= C1_G
                    col = C1_C if ok else (C_PENDING if is_today else C_BG)
                    if ok: ax.add_patch(patches.Circle(pos_1, 0.07, color=col)); ax.text(pos_1[0], pos_1[1], '✓', ha='center', va='center', color='white', fontweight='bold', fontsize=9)
                    else: ax.add_patch(patches.Circle(pos_1, 0.07, fill=False, edgecolor=col, lw=2))
                    ax.text(pos_1[0]+0.15, pos_1[1], f"{val1:.1f} km", va='center', fontsize=9, fontweight='bold', color='#333')

                # CILJ 2 (Fiksna kvota preteklosti)
                if C2_A:
                    ok = val1 >= daily_avg_2
                    col = C2_C if ok else (C_PENDING if is_today else 'salmon')
                    if ok: ax.add_patch(patches.Circle(pos_2, 0.07, color=col)); ax.text(pos_2[0], pos_2[1], '✓', ha='center', va='center', color='white', fontweight='bold', fontsize=9)
                    else: ax.add_patch(patches.Circle(pos_2, 0.07, fill=False, edgecolor=col, lw=2)); ax.text(pos_2[0], pos_2[1], '!', ha='center', va='center', color=col, fontweight='bold', fontsize=9)
                    ax.text(pos_2[0]+0.15, pos_2[1], f"{val1:.1f}/{daily_avg_2:.1f}", va='center', fontsize=f_sz-1)

                # CILJ 3
                if C3_A:
                    ok = val1 >= daily_avg_3
                    col = C3_C if ok else (C_PENDING if is_today else 'salmon')
                    if ok: ax.add_patch(patches.Circle(pos_3, 0.07, color=col))
                    else: ax.add_patch(patches.Circle(pos_3, 0.07, fill=False, edgecolor=col, lw=2))
                    ax.text(pos_3[0]+0.15, pos_3[1], f"{val1:.1f}/{daily_avg_3:.1f}", va='center', fontsize=f_sz-1)

                # CILJ 4
                if C4_A and val2 > 0:
                     ax.add_patch(patches.Circle(pos_4, 0.07, color=C4_C))
                     ax.text(pos_4[0]+0.15, pos_4[1], f"+{int(val2)}", va='center', fontsize=f_sz, color=C4_C)
            
            # 2. PRIHODNOST
            elif day > current_day_real:
                is_tomorrow = (day == current_day_real + 1)
                
                # CILJ 2
                if C2_A:
                    # Jutri: Preračunan cilj z barvo. Pojutrišnjem: Navadno povprečje, sivo.
                    val_show = next_goal_2 if is_tomorrow else daily_avg_2
                    col_show = '#f2f4f4'
                    if is_tomorrow:
                        txt_col = C_GOOD if next_goal_2 <= daily_avg_2 else C_BAD
                    else:
                        txt_col = '#95a5a6' # Siva

                    ax.add_patch(patches.Circle(pos_2, 0.07, color=col_show))
                    ax.text(pos_2[0]+0.15, pos_2[1], f"Cilj: {val_show:.1f}", va='center', fontsize=f_sz-1, fontweight='bold', color=txt_col)
                
                # CILJ 3
                if C3_A:
                    val_show = next_goal_3 if is_tomorrow else daily_avg_3
                    if is_tomorrow:
                        txt_col = C_GOOD if next_goal_3 <= daily_avg_3 else C_BAD
                    else:
                        txt_col = '#95a5a6'

                    ax.add_patch(patches.Circle(pos_3, 0.07, color='#f2f4f4'))
                    ax.text(pos_3[0]+0.15, pos_3[1], f"Cilj: {val_show:.1f}", va='center', fontsize=f_sz-1, fontweight='bold', color=txt_col)

        if w_sum_dist > 0:
            ax.text(7.5, 5 - week_idx + 0.6, f"{w_sum_dist:.1f} km", ha='center', va='center', fontsize=11, fontweight='bold', color='#555')
            if w_sum_elev > 0:
                ax.text(7.5, 5 - week_idx + 0.3, f"{int(w_sum_elev)} m", ha='center', va='center', fontsize=11, fontweight='bold', color=C4_C)

    # SPODNJI STOLPCI
    ax.plot([0, 8], [-0.2, -0.2], color='#bdc3c7', lw=2) 
    ax.text(4, -0.8, 'NAPREDEK DO CILJA', fontsize=18, fontweight='bold', ha='center', color='#2c3e50')
    
    bar_x = 0.5; bar_width = 7; bar_height = 0.6; y_start = -1.8
    total_run_so_far = df_jan['run'].sum(); total_elev_so_far = df_jan['elev'].sum()
    total_run_year = df[df['dt'].dt.year == 2026]['run'].sum()
    
    def draw_bar(y, val, goal, color, label, target_val=None, unit='km'):
        # Ozadje
        ax.add_patch(patches.Rectangle((bar_x, y), bar_width, bar_height, facecolor=C_BG, edgecolor='none'))
        # Napredek
        pct = val / goal if goal > 0 else 0; pct = 1 if pct > 1 else pct
        ax.add_patch(patches.Rectangle((bar_x, y), bar_width * pct, bar_height, facecolor=color, edgecolor='none'))
        # Tekst
        ax.text(bar_x, y + 0.7, f"{label}", fontsize=12, fontweight='bold', color='#555')
        ax.text(bar_x + bar_width, y + 0.7, f"{val:.1f} / {goal:.0f} {unit}", fontsize=12, fontweight='bold', color='black', ha='right')
        # Manjka
        ax.text(bar_x + bar_width, y + 0.1, f"Manjka: {goal - val:.1f}", fontsize=10, color='red', ha='right')
        
        # --- MARKER "PLAN DO DANES" ---
        if target_val is not None:
            # Kje je ta točka na grafu (procentualno glede na celoten cilj)
            t_pct = target_val / goal if goal > 0 else 0
            if t_pct > 1: t_pct = 1
            t_pos_x = bar_x + (bar_width * t_pct)
            
            # Narišemo črno črtico
            ax.plot([t_pos_x, t_pos_x], [y, y + bar_height], color='black', lw=2, linestyle='--')
            # Napišemo nad njo
            ax.text(t_pos_x, y - 0.2, f"Plan: {target_val:.0f}", ha='center', fontsize=9, fontweight='bold', color='black')

    current_y = y_start
    if "cat1" in active_bars: 
        # C1 je običajno dnevni cilj, tu ga prikažemo kot mesečno vsoto če je izbran
        draw_bar(current_y, total_run_so_far, C1_G * 31, C1_C, C1_N); current_y -= 1.4
    
    if "cat2" in active_bars:
        # LETNI PLAN: Cilj do danes = povprečje * št. dni v letu
        draw_bar(current_y, total_run_year, C2_G, C2_C, C2_N, target_val=target_today_2); current_y -= 1.4
    
    if "cat3" in active_bars:
        # MESEČNI PLAN: Cilj do danes = povprečje * št. dni v mesecu
        draw_bar(current_y, total_run_so_far, C3_G, C3_C, C3_N, target_val=target_today_3); current_y -= 1.4
        
    if "cat4" in active_bars:
        draw_bar(current_y, total_elev_so_far, C4_G, C4_C, C4_N, unit="m"); current_y -= 1.4

    st.pyplot(fig)
