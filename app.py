import streamlit as st
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
    # Seznam ciljev
    if 'goals_list' not in st.session_state:
        st.session_state['goals_list'] = [
            {'id': 'g1', 'name': 'Letni Plan', 'color': '#f1c40f', 'goal': 2500.0, 'type': 'Letni', 'unit': 'km', 'active': True},
            {'id': 'g2', 'name': 'Strava Izziv', 'color': '#FC4C02', 'goal': 300.0, 'type': 'Mesečni', 'unit': 'km', 'active': True},
            {'id': 'g3', 'name': 'Hribi', 'color': '#8e44ad', 'goal': 80000.0, 'type': 'Letni', 'unit': 'm', 'active': True},
        ]
    
    # Ločene nastavitve za razčlenitev
    if 'show_sub_month' not in st.session_state: st.session_state['show_sub_month'] = True
    if 'show_sub_week' not in st.session_state: st.session_state['show_sub_week'] = True

# --- APLIKACIJA ---
init_settings()
st.title("🏃‍♀️ Moj Planer")

tab1, tab2, tab3 = st.tabs(["📊 Koledar", "➕ Vnos", "⚙️ Nastavitve"])

# ==============================================================================
# ZAVIHEK 3: NASTAVITVE
# ==============================================================================
with tab3:
    st.header("📋 Urejanje")
    
    st.subheader("1. Kaj naj bo prikazano pod grafom?")
    c1, c2 = st.columns(2)
    with c1: 
        st.session_state['show_sub_month'] = st.checkbox("Mesečna analiza", value=st.session_state['show_sub_month'], help="Prikaže napredek v trenutnem mesecu za letne cilje.")
    with c2: 
        st.session_state['show_sub_week'] = st.checkbox("Tedenska analiza", value=st.session_state['show_sub_week'], help="Prikaže napredek v tem tednu.")
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
            
            g['active'] = st.checkbox("Prikaži na koledarju", value=g['active'], key=f"a_{g['id']}")
            
            if st.button(f"🗑️ Izbriši", key=f"del_{g['id']}"):
                goals_to_remove.append(i)

    if goals_to_remove:
        for index in sorted(goals_to_remove, reverse=True):
            del st.session_state['goals_list'][index]
        st.rerun()

    st.subheader("➕ Dodaj nov cilj")
    with st.form("new_goal"):
        n_name = st.text_input("Ime (npr. Dnevni tek)")
        c1, c2 = st.columns(2)
        with c1: n_goal = st.number_input("Vrednost", value=100.0)
        with c2: n_unit = st.selectbox("Enota", ["km", "m"])
        n_type = st.selectbox("Tip", ["Mesečni", "Letni"])
        n_color = st.color_picker("Barva", "#00ff00")
        
        if st.form_submit_button("Dodaj"):
            new_id = str(uuid.uuid4())[:8]
            st.session_state['goals_list'].append({
                'id': new_id, 'name': n_name, 'color': n_color, 'goal': n_goal, 
                'type': n_type, 'unit': n_unit, 'active': True
            })
            st.rerun()

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
# ZAVIHEK 1: VIZUALIZACIJA
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

    # Priprava parametrov
    day_of_year = today.timetuple().tm_yday
    day_of_month = today.day
    days_in_year = 366 if calendar.isleap(current_year) else 365
    days_in_month = calendar.monthrange(current_year, current_month)[1]
    
    current_week_num = today.isocalendar()[1]
    current_weekday_iso = today.isocalendar()[2] # 1=Pon
    
    active_goals = [g for g in st.session_state['goals_list'] if g['active']]
    
    # -----------------------------------------------------------
    # PRED-IZRAČUN (Banking logika za vsak cilj)
    # -----------------------------------------------------------
    goals_calc = []
    for g in st.session_state['goals_list']:
        g_val = g['goal']
        unit_key = 'elev' if g['unit'] == 'm' else 'run'
        
        # 1. Dnevno povprečje
        if g['type'] == 'Letni':
            daily_avg = g_val / days_in_year
            # Stanje celotnega leta za banking
            accum_total = df[df['dt'].dt.year == current_year][unit_key].sum()
            target_total_today = daily_avg * day_of_year
        else:
            daily_avg = g_val / days_in_month
            # Stanje meseca za banking
            accum_total = df_month_view[unit_key].sum()
            target_total_today = daily_avg * day_of_month
            
        # 2. Banking (Jutri)
        surplus = accum_total - target_total_today
        goal_tomorrow = daily_avg - surplus
        if goal_tomorrow < 0: goal_tomorrow = 0 # Ne more biti manj kot 0
        
        goals_calc.append({
            'meta': g,
            'daily_avg': daily_avg,
            'goal_tomorrow': goal_tomorrow,
            'surplus': surplus,
            'accum_total': accum_total
        })

    # -----------------------------------------------------------
    # RISANJE
    # -----------------------------------------------------------
    C_BG = '#ecf0f1'; C_PENDING = '#e67e22'; C_TEXT = '#2c3e50'; C_GOOD = '#27ae60'; C_BAD = '#c0392b'
    
    # Izračun višine: Osnova + (Cilji * faktor) + (Razčlenitve * faktor)
    bars_count = len(st.session_state['goals_list'])
    extra_rows = 0
    if st.session_state['show_sub_month']: 
        # Samo za letne cilje
        extra_rows += len([g for g in st.session_state['goals_list'] if g['type'] == 'Letni'])
    if st.session_state['show_sub_week']:
        extra_rows += bars_count

    # Povečali smo faktor višine, da ne bo stisnjeno
    fig_height = 11 + ((bars_count + extra_rows) * 1.5)
    fig, ax = plt.subplots(figsize=(12, fig_height))
    
    ax.set_xlim(0, 8); ax.set_ylim(-2 - (bars_count + extra_rows) * 1.5, 7.5); ax.axis('off')

    SLO_MONTHS = {1:"JANUAR", 2:"FEBRUAR", 3:"MAREC", 4:"APRIL", 5:"MAJ", 6:"JUNIJ", 7:"JULIJ", 8:"AVGUST", 9:"SEPTEMBER", 10:"OKTOBER", 11:"NOVEMBER", 12:"DECEMBER"}
    month_name = SLO_MONTHS.get(current_month, "")
    ax.text(4, 7.2, f'{month_name} {current_year}', fontsize=24, fontweight='bold', ha='center', color=C_TEXT)
    
    # Legenda (zgoraj)
    active_goals_count = len(active_goals)
    leg_y = 6.7
    if active_goals_count > 0:
        step = 8 / (active_goals_count + 1)
        for i, g in enumerate(active_goals):
            px = step * (i + 1)
            ax.add_patch(patches.Circle((px, leg_y), 0.15, color=g['color']))
            ax.text(px + 0.3, leg_y, g['name'], va='center', fontsize=11)

    ax.plot([0, 8], [6.4, 6.4], color='#bdc3c7', lw=2)

    # Koledar
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
            
            # --- LOGIKA KROGCEV ---
            if active_goals_count > 0:
                # Prostor za pike (od y+0.75 navzdol)
                space_per_dot = 0.6 / active_goals_count
                start_y_dots = y + 0.75
                
                daily_vals = data.get(day, {'run':0, 'elev':0, 'is_today':False})
                val_km = daily_vals['run']
                val_m = daily_vals['elev']
                is_today = daily_vals['is_today']
                
                w_sum_dist += val_km
                w_sum_elev += val_m
                
                # Iščemo ustrezen 'calc' objekt za ta aktivni cilj
                for i, g in enumerate(active_goals):
                    # Poišči ustrezen izračun
                    calc = next((c for c in goals_calc if c['meta']['id'] == g['id']), None)
                    if not calc: continue

                    dot_y = start_y_dots - (i * space_per_dot)
                    current_val = val_m if g['unit']=='m' else val_km
                    
                    # 1. PRETEKLOST (in DANES)
                    if day <= current_day_real:
                        daily_avg = calc['daily_avg']
                        has_data = current_val > 0
                        
                        if has_data or is_today:
                            ok = current_val >= daily_avg
                            col = g['color'] if ok else (C_PENDING if is_today else 'salmon')
                            
                            if ok:
                                ax.add_patch(patches.Circle((x+0.25, dot_y), 0.07, color=g['color']))
                                if active_goals_count <= 3: 
                                    ax.text(x+0.25, dot_y, '✓', ha='center', va='center', color='white', fontsize=7, fontweight='bold')
                            else:
                                ax.add_patch(patches.Circle((x+0.25, dot_y), 0.07, fill=False, edgecolor=col, lw=2))
                            
                            # Številka
                            txt = f"{int(current_val)}" if g['unit']=='m' else f"{current_val:.1f}"
                            ax.text(x+0.4, dot_y, txt, va='center', fontsize=8, color='black')

                    # 2. JUTRI (Banking napoved!)
                    elif day == current_day_real + 1:
                        target_tomorrow = calc['goal_tomorrow']
                        standard_avg = calc['daily_avg']
                        
                        # Barva teksta: Zelena če je cilj manjši od povprečja, Rdeča če je večji
                        txt_col = C_GOOD if target_tomorrow <= standard_avg else C_BAD
                        
                        # Sivo ozadje kroga
                        ax.add_patch(patches.Circle((x+0.25, dot_y), 0.07, color='#f2f4f4'))
                        # Izpis cilja
                        txt = f"{int(target_tomorrow)}" if g['unit']=='m' else f"{target_tomorrow:.1f}"
                        ax.text(x+0.4, dot_y, txt, va='center', fontsize=8, fontweight='bold', color=txt_col)

                    # 3. PRIHODNOST (Sivo povprečje)
                    else:
                        standard_avg = calc['daily_avg']
                        ax.add_patch(patches.Circle((x+0.25, dot_y), 0.07, color='#f2f4f4'))
                        # Samo pika, brez številk da ni gneče (razen če je zelo malo ciljev)
                        if active_goals_count <= 2:
                             txt = f"{int(standard_avg)}" if g['unit']=='m' else f"{standard_avg:.1f}"
                             ax.text(x+0.4, dot_y, txt, va='center', fontsize=7, color='#95a5a6')

        if w_sum_dist > 0:
            ax.text(7.5, 5 - week_idx + 0.5, f"{w_sum_dist:.1f}", ha='center', va='center', fontsize=10, fontweight='bold', color='#555')

    # -----------------------------------------------------------
    # STOLPCI SPODAJ
    # -----------------------------------------------------------
    ax.plot([0, 8], [-0.2, -0.2], color='#bdc3c7', lw=2) 
    ax.text(4, -0.8, 'NAPREDEK', fontsize=18, fontweight='bold', ha='center', color='#2c3e50')
    
    bar_x = 0.5; bar_width = 7; bar_height = 0.7; y_cursor = -2.2
    
    def draw_bar(y, val, goal, color, label, unit='km', indent=False):
        bx = bar_x + 0.4 if indent else bar_x
        bw = bar_width - 0.4 if indent else bar_width
        
        # Ozadje
        ax.add_patch(patches.Rectangle((bx, y), bw, bar_height, facecolor=C_BG, edgecolor='none'))
        # Polnilo
        pct = val / goal if goal > 0 else 0
        if pct > 1: pct = 1
        ax.add_patch(patches.Rectangle((bx, y), bw * pct, bar_height, facecolor=color, edgecolor='none'))
        
        # Tekst
        font_style = 'normal' if indent else 'bold'
        ax.text(bx, y + 0.8, label, fontsize=11, fontweight=font_style, color='#555')
        
        right_txt = f"{val:.1f} / {goal:.0f} {unit}"
        ax.text(bx + bw, y + 0.8, right_txt, fontsize=11, fontweight='bold', color='black', ha='right')

    # Iteracija čez VSE cilje v seznamu (ne glede na to ali so aktivni na koledarju)
    # Ker spodaj želimo videti napredek vseh
    for gd in goals_calc:
        meta = gd['meta']
        accum = gd['accum_total'] # To je vsota (letna ali mesečna, odvisno od tipa)
        
        # 1. Glavni stolpec
        lbl = f"{meta['name']} ({meta['type']})"
        draw_bar(y_cursor, accum, meta['goal'], meta['color'], lbl, unit=meta['unit'])
        y_cursor -= 1.4
        
        # 2. Mesečna analiza (Samo za letne cilje in če je vklopljeno)
        if st.session_state['show_sub_month'] and meta['type'] == 'Letni':
            # Cilj meseca = dnevno povprečje * dni v mesecu
            month_goal = gd['daily_avg'] * days_in_month
            month_accum = df_month_view['elev' if meta['unit']=='m' else 'run'].sum()
            
            draw_bar(y_cursor, month_accum, month_goal, meta['color'], "  Mesec", unit=meta['unit'], indent=True)
            y_cursor -= 1.4

        # 3. Tedenska analiza (Če je vklopljeno)
        if st.session_state['show_sub_week']:
            # Cilj tedna = dnevno povprečje * 7
            week_goal = gd['daily_avg'] * 7
            
            df['week_num'] = df['dt'].dt.isocalendar().week
            unit_key = 'elev' if meta['unit']=='m' else 'run'
            week_accum = df[(df['dt'].dt.year == current_year) & (df['week_num'] == current_week_num)][unit_key].sum()
            
            draw_bar(y_cursor, week_accum, week_goal, meta['color'], "  Teden", unit=meta['unit'], indent=True)
            y_cursor -= 1.4
            
        # Dodaten presledek med cilji
        y_cursor -= 0.5

    st.pyplot(fig)
