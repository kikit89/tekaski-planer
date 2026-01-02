import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import calendar
import os
import uuid
from datetime import date, datetime

# --- KONFIGURACIJA ---
st.set_page_config(page_title="Moj Planer", layout="centered", page_icon="🏃‍♀️")
FILE_NAME = 'teki_data.csv'

# --- PODATKI ---
def load_data():
    if os.path.exists(FILE_NAME):
        df = pd.read_csv(FILE_NAME)
        df['dt'] = pd.to_datetime(df['date'])
        return df
    else:
        # Začetni podatki
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
    # Inicializacija seznama ciljev (če še ne obstaja)
    if 'goals_list' not in st.session_state:
        st.session_state['goals_list'] = [
            # IDji so pomembni za brisanje
            {'id': 'g_main', 'name': 'Letni Plan', 'color': '#f1c40f', 'goal': 2500.0, 'type': 'Letni', 'unit': 'km', 'active': True},
            {'id': 'g_strava', 'name': 'Strava Izziv', 'color': '#FC4C02', 'goal': 300.0, 'type': 'Mesečni', 'unit': 'km', 'active': True},
            {'id': 'g_elev', 'name': 'Hribi', 'color': '#8e44ad', 'goal': 80000.0, 'type': 'Letni', 'unit': 'm', 'active': True},
        ]
    
    # Nastavitve analiz (spodaj)
    if 'show_analysis_year' not in st.session_state: st.session_state['show_analysis_year'] = True
    if 'show_analysis_month' not in st.session_state: st.session_state['show_analysis_month'] = True
    if 'show_analysis_week' not in st.session_state: st.session_state['show_analysis_week'] = True

# --- APLIKACIJA ---
init_settings()
st.title("🏃‍♀️ Moj Planer")

tab1, tab2, tab3 = st.tabs(["📊 Koledar", "➕ Vnos", "⚙️ Urejanje Ciljev"])

# ==============================================================================
# ZAVIHEK 3: UREJANJE CILJEV (ADD / DELETE)
# ==============================================================================
with tab3:
    st.header("📋 Moji Cilji")
    st.info("Tukaj lahko dodaš nove izzive ali izbrišeš stare. Za vsakega določi tip (Letni/Mesečni), da bo deloval 'semafor' +/-.")

    # 1. SEZNAM OBSTOJEČIH
    goals_to_remove = []
    
    for i, g in enumerate(st.session_state['goals_list']):
        with st.expander(f"{g['name']} ({g['type']})", expanded=False):
            c1, c2 = st.columns([1, 3])
            with c1: 
                new_color = st.color_picker("Barva", g['color'], key=f"c_{g['id']}")
                g['color'] = new_color
            with c2: 
                new_name = st.text_input("Ime", g['name'], key=f"n_{g['id']}")
                g['name'] = new_name
            
            c3, c4, c5 = st.columns(3)
            with c3:
                new_goal = st.number_input("Cilj", value=float(g['goal']), key=f"g_{g['id']}")
                g['goal'] = new_goal
            with c4:
                new_type = st.selectbox("Tip", ["Letni", "Mesečni"], index=0 if g['type']=="Letni" else 1, key=f"t_{g['id']}")
                g['type'] = new_type
            with c5:
                new_unit = st.selectbox("Enota", ["km", "m"], index=0 if g.get('unit','km')=="km" else 1, key=f"u_{g['id']}")
                g['unit'] = new_unit
                
            # Gumb za brisanje
            if st.button(f"🗑️ Izbriši {g['name']}", key=f"del_{g['id']}"):
                goals_to_remove.append(i)

    # Izvedba brisanja (zunaj zanke)
    if goals_to_remove:
        for index in sorted(goals_to_remove, reverse=True):
            del st.session_state['goals_list'][index]
        st.rerun()

    st.write("---")
    
    # 2. DODAJANJE NOVEGA
    st.subheader("➕ Dodaj nov cilj")
    with st.form("add_goal_form"):
        c1, c2 = st.columns(2)
        with c1: n_name = st.text_input("Ime cilja (npr. Zimski Izziv)")
        with c2: n_color = st.color_picker("Barva", "#00ff00")
        
        c3, c4, c5 = st.columns(3)
        with c3: n_goal = st.number_input("Cilj (vrednost)", min_value=1.0, value=100.0)
        with c4: n_type = st.selectbox("Tip cilja", ["Mesečni", "Letni"])
        with c5: n_unit = st.selectbox("Enota", ["km", "m"])
        
        if st.form_submit_button("Dodaj Cilj"):
            new_id = str(uuid.uuid4())[:8]
            new_obj = {
                'id': new_id,
                'name': n_name if n_name else "Nov Cilj",
                'color': n_color,
                'goal': n_goal,
                'type': n_type,
                'unit': n_unit,
                'active': True
            }
            st.session_state['goals_list'].append(new_obj)
            st.success("Dano!")
            st.rerun()

    st.write("---")
    st.subheader("Nastavitve Analize (Prvi stolpci)")
    c1, c2, c3 = st.columns(3)
    with c1: st.session_state['show_analysis_year'] = st.checkbox("Letni pregled", st.session_state['show_analysis_year'])
    with c2: st.session_state['show_analysis_month'] = st.checkbox("Mesečni pregled", st.session_state['show_analysis_month'])
    with c3: st.session_state['show_analysis_week'] = st.checkbox("Tedenski pregled", st.session_state['show_analysis_week'])


# ==============================================================================
# ZAVIHEK 2: VNOS
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
# ZAVIHEK 1: VIZUALIZACIJA (KOLEDAR & BAR)
# ==============================================================================
with tab1:
    df = load_data()
    if 'dt' not in df.columns: df['dt'] = pd.to_datetime(df['date'])
    
    today = date.today()
    current_year = today.year
    current_month = today.month
    
    # Podatki za tekoči mesec
    df_month_view = df[(df['dt'].dt.year == current_year) & (df['dt'].dt.month == current_month)]
    
    data = {}
    for _, row in df_month_view.iterrows():
        data[row['dt'].day] = {'run': row['run'], 'elev': row['elev'], 'is_today': (row['dt'].date() == today)}

    # Priprava parametrov za izračune
    day_of_year = today.timetuple().tm_yday
    day_of_month = today.day
    days_in_year = 366 if calendar.isleap(current_year) else 365
    days_in_month = calendar.monthrange(current_year, current_month)[1]
    
    # -----------------------------------------------------------
    # IZRAČUNI CILJEV (Dinamično glede na seznam)
    # -----------------------------------------------------------
    goals_data = [] # Tu bomo shranili preračunane vrednosti za risanje
    
    # Najprej poiščimo "Glavni letni cilj" za prvo analizo (običajno prvi v seznamu ali prvi z tipom Letni)
    main_annual_goal = next((g for g in st.session_state['goals_list'] if g['type'] == 'Letni' and g['unit'] == 'km'), None)
    
    # Preračunajmo status za vsak cilj v seznamu
    for g in st.session_state['goals_list']:
        g_val = g['goal']
        
        # 1. Dnevno povprečje (Daily Requirement)
        if g['type'] == 'Letni':
            daily_req = g_val / days_in_year
            target_today = daily_req * day_of_year
            current_accum = df[df['dt'].dt.year == current_year][ 'elev' if g['unit']=='m' else 'run' ].sum()
        else: # Mesečni
            daily_req = g_val / days_in_month
            target_today = daily_req * day_of_month
            current_accum = df_month_view[ 'elev' if g['unit']=='m' else 'run' ].sum()
            
        # 2. Banking (Jutri)
        surplus = current_accum - target_today
        next_day_goal = daily_req - surplus
        
        goals_data.append({
            'conf': g,
            'daily_req': daily_req,
            'target_today': target_today,
            'current_accum': current_accum,
            'next_day_goal': next_day_goal,
            'surplus': surplus
        })

    # -----------------------------------------------------------
    # RISANJE KOLEDARJA
    # -----------------------------------------------------------
    C_BG = '#ecf0f1'; C_PENDING = '#e67e22'; C_TEXT = '#2c3e50'; C_GOOD = '#27ae60'; C_BAD = '#c0392b'
    
    # Višina grafa: odvisna od števila stolpcev spodaj
    # Preštejemo stolpce
    num_bars = 0
    if st.session_state['show_analysis_year']: num_bars += 1
    if st.session_state['show_analysis_month']: num_bars += 1
    if st.session_state['show_analysis_week']: num_bars += 1
    num_bars += len(goals_data) # Za vsak cilj en stolpec

    fig_height = 13 + (num_bars * 1.3)
    fig, ax = plt.subplots(figsize=(12, fig_height))
    ax.set_xlim(0, 8); ax.set_ylim(-2 - num_bars, 7.5); ax.axis('off')

    SLO_MONTHS = {1:"JANUAR", 2:"FEBRUAR", 3:"MAREC", 4:"APRIL", 5:"MAJ", 6:"JUNIJ", 7:"JULIJ", 8:"AVGUST", 9:"SEPTEMBER", 10:"OKTOBER", 11:"NOVEMBER", 12:"DECEMBER"}
    month_name = SLO_MONTHS.get(current_month, "MESEC")
    ax.text(4, 7.2, f'{month_name} {current_year}', fontsize=24, fontweight='bold', ha='center', color=C_TEXT)
    
    # LEGENDA (Dinamična)
    num_leg = len(goals_data)
    leg_y = 6.7
    # Preprosta razporeditev
    if num_leg > 0:
        step = 8 / (num_leg + 1)
        for i, gd in enumerate(goals_data):
            px = step * (i + 1)
            col = gd['conf']['color']
            name = gd['conf']['name']
            ax.add_patch(patches.Circle((px, leg_y), 0.15, color=col))
            ax.text(px + 0.3, leg_y, name, va='center', fontsize=11)

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
            
            # --- Dinamične pozicije pikic znotraj dneva ---
            # Razdelimo vertikalni prostor (0.2 do 0.8) glede na število ciljev
            if num_leg > 0:
                space_per_dot = 0.6 / num_leg
                # Začnemo zgoraj
                start_y = 0.8 - (space_per_dot / 2)
            
            # 1. PRETEKLOST (Podatki obstajajo)
            if day in data:
                d = data[day]; val_km = d['run']; val_m = d['elev']; is_today = d['is_today']
                w_sum_dist += val_km; w_sum_elev += val_m
                
                for i, gd in enumerate(goals_data):
                    conf = gd['conf']
                    # Katero vrednost preverjamo? (km ali m)
                    act_val = val_m if conf['unit'] == 'm' else val_km
                    daily_goal = gd['daily_req']
                    
                    # Ali je cilj dosežen? (Za prikaz kljukice/klicaja)
                    # POZOR: Pri banking logiki je to malo bolj kompleksno, 
                    # ampak za preprostost koledarja: ali sem danes naredil povprečje?
                    ok = act_val >= daily_goal
                    col = conf['color'] if ok else (C_PENDING if is_today else 'salmon')
                    
                    py = start_y - (i * space_per_dot)
                    
                    if ok:
                        ax.add_patch(patches.Circle((x+0.25, py), 0.07, color=conf['color']))
                        # Kljukica samo če je prostor (če je malo ciljev)
                        if num_leg <= 4: ax.text(x+0.25, py, '✓', ha='center', va='center', color='white', fontsize=8, fontweight='bold')
                    else:
                        # Klicaj
                        ax.add_patch(patches.Circle((x+0.25, py), 0.07, fill=False, edgecolor=col, lw=2))
                    
                    # Izpis številke zraven (samo če je vrednost > 0 ali je to glavna kategorija)
                    # Da ne delamo gneče, izpišemo vrednost samo pri prvem, ali pa če je m
                    if i == 0 or conf['unit'] == 'm':
                         txt = f"{act_val:.1f}" if conf['unit'] == 'km' else f"{int(act_val)}"
                         ax.text(x+0.4, py, txt, va='center', fontsize=9, color='black')

            # 2. PRIHODNOST (Napovedi za VSE cilje)
            elif day > current_day_real:
                is_tomorrow = (day == current_day_real + 1)
                
                for i, gd in enumerate(goals_data):
                    conf = gd['conf']
                    py = start_y - (i * space_per_dot)
                    
                    # Samo za tomorrow pokažemo barvno/številko, naprej sivo
                    if is_tomorrow:
                        # Barva teksta: Zelena če je kredit, Rdeča če je dolg
                        next_val = gd['next_day_goal']
                        # Če je naslednji cilj manjši od povprečja -> Zeleno (Dobro)
                        txt_col = C_GOOD if next_val <= gd['daily_req'] else C_BAD
                        
                        ax.add_patch(patches.Circle((x+0.25, py), 0.07, color='#f2f4f4'))
                        ax.text(x+0.4, py, f"{next_val:.1f}", va='center', fontsize=8, fontweight='bold', color=txt_col)
                    else:
                        # Pojutrišnjem -> samo siva povprečna vrednost
                        # Razen za 'Dnevni' tip, ampak recimo da vsi bankingajo
                        ax.add_patch(patches.Circle((x+0.25, py), 0.07, color='#f2f4f4'))
                        # Ne izpisujemo številk za pojutrišnjem da ni gneče, samo piko


        # Tedenske vsote
        if w_sum_dist > 0:
            ax.text(7.5, 5 - week_idx + 0.6, f"{w_sum_dist:.1f}", ha='center', va='center', fontsize=10, fontweight='bold', color='#555')
            if w_sum_elev > 0:
                ax.text(7.5, 5 - week_idx + 0.3, f"{int(w_sum_elev)}", ha='center', va='center', fontsize=9, color='#8e44ad')

    # -----------------------------------------------------------
    # SPODNJI STOLPCI (SEMAFOR 🚦)
    # -----------------------------------------------------------
    ax.plot([0, 8], [-0.2, -0.2], color='#bdc3c7', lw=2) 
    ax.text(4, -0.8, 'NAPREDEK & STANJE', fontsize=18, fontweight='bold', ha='center', color='#2c3e50')
    
    bar_x = 0.5; bar_width = 7; bar_height = 0.6; y_start = -1.8
    
    def draw_bar_status(y, val, goal, color, label, target_val=None, unit='km'):
        # Ozadje
        ax.add_patch(patches.Rectangle((bar_x, y), bar_width, bar_height, facecolor=C_BG, edgecolor='none'))
        # Napredek
        pct = val / goal if goal > 0 else 0
        if pct > 1: pct = 1
        ax.add_patch(patches.Rectangle((bar_x, y), bar_width * pct, bar_height, facecolor=color, edgecolor='none'))
        
        # STATUS (Semafor)
        if target_val is not None:
            diff = val - target_val
            diff_text = f"{diff:+.1f} {unit}"
            status_color = C_GOOD if diff >= 0 else C_BAD # Zelena če plus, Rdeča če minus
            
            # Izris "Luknje" (če je minus)
            if diff < 0:
                pct_target = target_val / goal if goal > 0 else 0
                if pct_target > 1: pct_target = 1
                rect_start = bar_x + (bar_width * pct)
                rect_width = (bar_width * pct_target) - (bar_width * pct)
                if rect_width > 0:
                    ax.add_patch(patches.Rectangle((rect_start, y), rect_width, bar_height, 
                                                 facecolor=C_BAD, alpha=0.3, edgecolor=C_BAD, hatch='//'))
            
            # Marker planirane pozicije
            t_pct = target_val / goal if goal > 0 else 0
            if t_pct > 1: t_pct = 1
            t_pos = bar_x + (bar_width * t_pct)
            ax.plot([t_pos, t_pos], [y, y + bar_height], color='black', alpha=0.5, lw=1.5, linestyle=':')

            # Izpis statusa DESNO
            ax.text(bar_x + bar_width, y + 0.1, f"{diff_text}", fontsize=11, fontweight='bold', color=status_color, ha='right')

        # Ime in vrednosti
        ax.text(bar_x, y + 0.7, f"{label}", fontsize=11, fontweight='bold', color='#555')
        ax.text(bar_x + bar_width, y + 0.7, f"{val:.1f} / {goal:.0f}", fontsize=11, fontweight='bold', color='black', ha='right')

    current_y = y_start
    
    # 1. ANALIZA GLAVNEGA CILJA (Če obstaja in je vklopljena)
    if main_annual_goal:
        # Priprava podatkov za glavni cilj
        g_val = main_annual_goal['goal']
        g_col = main_annual_goal['color']
        # Letni podatki
        year_accum = df[df['dt'].dt.year == current_year]['run'].sum()
        year_target = (g_val / days_in_year) * day_of_year
        # Mesečni podatki
        month_target_total = (g_val / days_in_year) * days_in_month
        month_accum = df_month_view['run'].sum()
        month_target_now = (g_val / days_in_year) * day_of_month
        # Tedenski podatki
        current_week_num = today.isocalendar()[1]
        jan1_weekday = date(current_year, 1, 1).isocalendar()[2]
        current_weekday = today.isocalendar()[2]
        
        # Fix za prvi teden
        week_target_total = (g_val / days_in_year) * 7
        if current_week_num == 1:
             active_days = current_weekday - jan1_weekday + 1
             if active_days < 0: active_days = 0
             week_target_now = (g_val / days_in_year) * active_days
        else:
             week_target_now = (g_val / days_in_year) * current_weekday
        
        df['week_num'] = df['dt'].dt.isocalendar().week
        week_accum = df[(df['dt'].dt.year == current_year) & (df['week_num'] == current_week_num)]['run'].sum()

        if st.session_state['show_analysis_year']:
            draw_bar_status(current_y, year_accum, g_val, g_col, "LETNI PREGLED", target_val=year_target); current_y -= 1.3
        if st.session_state['show_analysis_month']:
            draw_bar_status(current_y, month_accum, month_target_total, g_col, "MESEČNI DEL", target_val=month_target_now); current_y -= 1.3
        if st.session_state['show_analysis_week']:
            draw_bar_status(current_y, week_accum, week_target_total, g_col, "TEDENSKI DEL", target_val=week_target_now); current_y -= 1.3
            
    # 2. VSI CILJI IZ SEZNAMA (Tudi Strava!)
    for gd in goals_data:
        conf = gd['conf']
        # Uporabimo target_today, ki smo ga izračunali na začetku (spoštuje Tip: Letni/Mesečni)
        
        # Prikažemo bar. Za cilj (max vrednost) vzamemo:
        # Če je mesečni -> conf['goal']
        # Če je letni -> conf['goal']
        # Pri akumulaciji (val) pa:
        # Če je mesečni -> current_accum (ki je seštevek meseca)
        # Če je letni -> current_accum (ki je seštevek leta)
        # To smo že uredili v zanki goals_data zgoraj!
        
        draw_bar_status(
            current_y, 
            gd['current_accum'], 
            conf['goal'], 
            conf['color'], 
            conf['name'], 
            target_val=gd['target_today'], 
            unit=conf['unit']
        )
        current_y -= 1.3

    st.pyplot(fig)
