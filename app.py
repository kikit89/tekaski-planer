import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import calendar
import os
from datetime import date

# --- KONFIGURACIJA ---
st.set_page_config(page_title="Tekaški Planer 2026", layout="centered", page_icon="🏃‍♀️")
FILE_NAME = 'teki_data.csv'

# --- PODATKOVNE FUNKCIJE ---
def load_data():
    if os.path.exists(FILE_NAME):
        return pd.read_csv(FILE_NAME)
    else:
        return pd.DataFrame(columns=['date', 'run', 'walk', 'elev', 'note'])

def save_data(df):
    df.to_csv(FILE_NAME, index=False)

def get_settings():
    if 'yearly_goal' not in st.session_state: st.session_state['yearly_goal'] = 2500.0
    if 'strava_goal' not in st.session_state: st.session_state['strava_goal'] = 300.0
    if 'elev_goal' not in st.session_state: st.session_state['elev_goal'] = 80000.0

# --- GLAVNI VMESNIK ---
st.title("🏃‍♀️ Moj Tekaški Trener")
get_settings()

tab1, tab2, tab3 = st.tabs(["📊 Koledar & Cilji", "➕ Vnos Teka", "⚙️ Nastavitve"])

# --- 3. ZAVIHEK: NASTAVITVE ---
with tab3:
    st.header("Moji Cilji")
    c1, c2 = st.columns(2)
    with c1:
        st.session_state['yearly_goal'] = st.number_input("Letni cilj (km)", value=st.session_state['yearly_goal'], step=50.0)
        st.session_state['strava_goal'] = st.number_input("Strava Jan (km)", value=st.session_state['strava_goal'], step=10.0)
    with c2:
        st.session_state['elev_goal'] = st.number_input("Letni višinci (m)", value=st.session_state['elev_goal'], step=1000.0)

# --- 2. ZAVIHEK: VNOS ---
with tab2:
    st.header("Zabeleži aktivnost")
    with st.form("entry"):
        d_date = st.date_input("Datum", value=date.today())
        run = st.number_input("Tek (km)", min_value=0.0, step=0.1, format="%.2f")
        elev = st.number_input("Višinci (m)", min_value=0, step=10)
        note = st.text_input("Opomba")
        
        if st.form_submit_button("Shrani Aktivnost"):
            df = load_data()
            d_str = d_date.strftime("%Y-%m-%d")
            if d_str in df['date'].values:
                df.loc[df['date'] == d_str, ['run', 'elev', 'note']] = [run, elev, note]
                st.success(f"Posodobljeno za {d_str}!")
            else:
                new = pd.DataFrame({'date': [d_str], 'run': [run], 'walk': [0], 'elev': [elev], 'note': [note]})
                df = pd.concat([df, new], ignore_index=True)
                st.success(f"Dodano za {d_str}!")
            save_data(df)

# --- 1. ZAVIHEK: VIZUALIZACIJA (Originalni Dizajn) ---
with tab1:
    df = load_data()
    # Priprava podatkov
    df['dt'] = pd.to_datetime(df['date'])
    df_jan = df[(df['dt'].dt.year == 2026) & (df['dt'].dt.month == 1)]
    
    # Slovar podatkov za hitro iskanje
    data = {}
    for _, row in df_jan.iterrows():
        data[row['dt'].day] = {'run': row['run'], 'elev': row['elev']}

    # Cilji in vsote
    YEAR_GOAL = st.session_state['yearly_goal']
    STRAVA_GOAL = st.session_state['strava_goal']
    ELEV_GOAL = st.session_state['elev_goal']
    DAILY_QUOTA = YEAR_GOAL / 365.0
    MONTHLY_GOAL = DAILY_QUOTA * 31
    
    total_run_so_far = df_jan['run'].sum()
    total_elev_so_far = df_jan['elev'].sum()
    total_run_year = df[df['dt'].dt.year == 2026]['run'].sum() # Vsi teki v letu

    # --- RISANJE GRAFA (Matplotlib) ---
    # Nastavitev barv
    C_RUN = '#3498db'; C_QUOTA = '#f1c40f'; C_STRAVA = '#FC4C02'; C_ELEV = '#8e44ad'
    C_BG = '#ecf0f1'; C_SUCCESS = '#2ecc71'; C_FAIL = '#e74c3c'; C_PENDING = '#e67e22'
    
    fig, ax = plt.subplots(figsize=(10, 16)) # Visok format za telefon
    ax.set_xlim(0, 8); ax.set_ylim(-4.5, 7.5); ax.axis('off')

    # Naslov
    ax.text(4, 7.2, 'JANUAR 2026', fontsize=22, fontweight='bold', ha='center', color='#2c3e50')
    
    # Legenda (Krogci zgoraj)
    leg_y = 6.7
    ax.add_patch(patches.Circle((1.0, leg_y), 0.15, color=C_RUN)); ax.text(1.3, leg_y, 'Tek', va='center', fontsize=11)
    ax.add_patch(patches.Circle((3.0, leg_y), 0.15, color=C_QUOTA)); ax.text(3.3, leg_y, 'Kvota', va='center', fontsize=11)
    ax.add_patch(patches.Circle((5.0, leg_y), 0.15, color=C_STRAVA)); ax.text(5.3, leg_y, 'Strava', va='center', fontsize=11)
    ax.add_patch(patches.Circle((7.0, leg_y), 0.15, color=C_ELEV)); ax.text(7.3, leg_y, 'Višinci', va='center', fontsize=11)
    ax.plot([0, 8], [6.4, 6.4], color='#bdc3c7', lw=2)

    # Koledar
    cal = calendar.monthcalendar(2026, 1)
    days_of_week = ['Pon', 'Tor', 'Sre', 'Čet', 'Pet', 'Sob', 'Ned', 'Vsota']
    for i, dname in enumerate(days_of_week):
        ax.text(i + 0.5, 6.1, dname, ha='center', va='center', fontsize=12, fontweight='bold', color='#34495e')

    strava_daily_target = STRAVA_GOAL / 31.0

    for week_idx, week in enumerate(cal):
        weekly_sum = 0
        for day_idx, day in enumerate(week):
            x = day_idx; y = 5 - week_idx
            # Kvadratek
            rect = patches.Rectangle((x, y), 1, 1, fill=True, facecolor='white', edgecolor='#ecf0f1', linewidth=2)
            ax.add_patch(rect)
            
            if day == 0: continue
            
            ax.text(x + 0.05, y + 0.85, str(day), fontsize=14, fontweight='bold', color='#7f8c8d')
            
            pos_run = (x + 0.25, y + 0.72); pos_quota = (x + 0.25, y + 0.56)
            pos_strava = (x + 0.25, y + 0.40); pos_elev = (x + 0.25, y + 0.24)
            
            if day in data:
                d = data[day]; run_km = d['run']; elev = d['elev']
                weekly_sum += run_km
                
                # 1. RUN
                if run_km >= 1.6: 
                    ax.add_patch(patches.Circle(pos_run, 0.07, color=C_RUN))
                    ax.text(pos_run[0]+0.15, pos_run[1], f"{run_km:.1f}", va='center', fontsize=9, fontweight='bold')
                
                # 2. QUOTA
                if run_km >= DAILY_QUOTA: 
                    ax.add_patch(patches.Circle(pos_quota, 0.07, color=C_QUOTA))
                
                # 3. STRAVA
                if run_km >= strava_daily_target: 
                    ax.add_patch(patches.Circle(pos_strava, 0.07, color=C_STRAVA))
                
                # 4. ELEV
                if elev > 0: 
                    ax.add_patch(patches.Circle(pos_elev, 0.07, color=C_ELEV))
                    ax.text(pos_elev[0]+0.15, pos_elev[1], f"{int(elev)}", va='center', fontsize=9, color=C_ELEV)
        
        # Tedenska vsota
        if weekly_sum > 0:
            ax.text(7.5, 5 - week_idx + 0.5, f"{weekly_sum:.1f}", ha='center', va='center', fontsize=11, fontweight='bold')

    # Spodnji del - Stolpci (Custom Bars)
    ax.plot([0, 8], [-0.2, -0.2], color='#bdc3c7', lw=2) 
    ax.text(4, -0.6, 'NAPREDEK DO CILJA', fontsize=16, fontweight='bold', ha='center', color='#2c3e50')

    bar_x = 0.5; bar_width = 7; bar_height = 0.5
    
    def draw_bar_custom(y, val, goal, color, label, unit='km'):
        # Ozadje
        ax.add_patch(patches.Rectangle((bar_x, y), bar_width, bar_height, facecolor=C_BG, edgecolor='none'))
        # Polnilo
        pct = val / goal if goal > 0 else 0
        pct = 1 if pct > 1 else pct
        ax.add_patch(patches.Rectangle((bar_x, y), bar_width * pct, bar_height, facecolor=color, edgecolor='none'))
        # Tekst
        ax.text(bar_x, y + 0.6, f"{label}", fontsize=11, fontweight='bold', color='#555')
        ax.text(bar_x + bar_width, y + 0.6, f"{val:.1f} / {goal:.0f} {unit}", fontsize=11, fontweight='bold', color='black', ha='right')

    draw_bar_custom(-1.3, total_run_so_far, MONTHLY_GOAL, C_RUN, "MESEČNI CILJ (Jan)")
    draw_bar_custom(-2.3, total_run_so_far, STRAVA_GOAL, C_STRAVA, "STRAVA IZZIV")
    draw_bar_custom(-3.3, total_run_year, YEAR_GOAL, C_QUOTA, "LETNI CILJ (2026)")
    draw_bar_custom(-4.3, total_elev_so_far, ELEV_GOAL, C_ELEV, "VIŠINSKI METRI", "m")

    st.pyplot(fig)
