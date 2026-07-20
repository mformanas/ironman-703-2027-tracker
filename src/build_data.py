import json
import os
from datetime import date, timedelta

START = date(2026, 6, 15)
RACE  = date(2027, 12, 5)
race_week_monday = RACE - timedelta(days=RACE.weekday())
N_WEEKS = (race_week_monday - START).days // 7 + 1

def phase_of(w):
    if w <= 16: return "Foundation"
    if w <= 36: return "Base"
    if w <= 55: return "Build & Integrate"
    if w <= 71: return "Peak"
    return "Taper & Race"

PHASE_HRS = {"Foundation": (6.0, 8.0), "Base": (8.0, 10.0),
             "Build & Integrate": (9.5, 11.5), "Peak": (10.5, 12.0)}
FRACT = {
    "Foundation":        (0.30, 0.30, 0.20, 0.20, 0.00),
    "Base":              (0.25, 0.35, 0.25, 0.13, 0.02),
    "Build & Integrate": (0.20, 0.38, 0.24, 0.07, 0.11),
    "Peak":              (0.18, 0.40, 0.23, 0.05, 0.14),
    "Taper & Race":      (0.20, 0.38, 0.27, 0.05, 0.10),
}
def is_deload(w):
    if w >= 72: return False
    return w % 4 == 0
def q(x): return round(x*4)/4
def total_hours(w):
    ph = phase_of(w)
    if ph == "Taper & Race":
        offset = w - 72
        seq = [9.0, 7.5, 6.0, 5.0, 4.5, 4.0]
        if w == N_WEEKS: return 4.0
        return seq[min(offset, len(seq)-1)]
    lo, hi = PHASE_HRS[ph]
    bounds = {"Foundation":(1,16),"Base":(17,36),"Build & Integrate":(37,55),"Peak":(56,71)}
    s,e = bounds[ph]
    frac = (w-s)/(e-s) if e>s else 0
    base = lo + (hi-lo)*frac
    if is_deload(w): base *= 0.65
    return base

MILES = {
    1:  "START \u2014 learn freestyle technique; run/walk method; pro bike fit. Build the habit.",
    16: "Recovery + skills test: time-trial swim/bike/run to set your baseline.",
    17: "BASE phase begins \u2014 build continuous swim distance & long ride/run.",
    37: "INTEGRATION begins \u2014 add ONE weekly brick (bike then short run).",
    45: "Open-water swim practice begins (wetsuit, sighting).",
    50: "TUNE-UP RACE: enter a Sprint triathlon to rehearse logistics.",
    56: "PEAK phase \u2014 race-specific bricks; dial in race-day nutrition.",
    64: "TUNE-UP RACE: Olympic-distance triathlon (dress rehearsal).",
    68: "HALF-DISTANCE SIMULATION: ~75% of race volume this weekend.",
    72: "TAPER begins \u2014 cut volume ~30%/wk, keep intensity short & sharp.",
}
def focus_note(w):
    ph = phase_of(w)
    if w in MILES: return MILES[w]
    if is_deload(w): return "Recovery week \u2014 easy aerobic only; prioritise sleep & technique."
    if w == N_WEEKS: return "RACE WEEK \u2014 IRONMAN 70.3 La Quinta, Sun Dec 5. Short openers, rest, race!"
    notes = {
        "Foundation": "Skill + easy aerobic. Form over effort in all three sports.",
        "Base": "Three midweek bricks (bike\u2192run) + long weekend ride & run. Build steady aerobic volume.",
        "Build & Integrate": "Add tempo/threshold + weekly brick. Practise fuelling.",
        "Peak": "Race-pace efforts, long brick, OW swim. Rehearse race day.",
        "Taper & Race": "Maintain frequency, slash duration. Stay loose and rested.",
    }
    return notes[ph]
def key_session(w):
    ph = phase_of(w)
    if w == N_WEEKS: return "RACE DAY"
    return {
        "Foundation":"Long easy ride (skills) + longest run/walk",
        "Base":"Midweek bricks (bike\u2192run) + weekend long ride & run",
        "Build & Integrate":"Weekend brick: long ride \u2192 transition run",
        "Peak":"Race-specific brick: race-pace ride + run off the bike",
        "Taper & Race":"Short race-pace openers",
    }[ph]

TEMPLATES = {
 "Foundation":[("Strength 40\u201345 min + mobility","strength"),
   ("Run #1 \u2014 easy 35\u201350 min (run/walk \u2192 continuous)","run"),
   ("Swim \u2014 technique 45\u201360 min","swim"),
   ("Rest / mobility","rest"),
   ("Run #2 \u2014 easy 35\u201350 min (run/walk \u2192 continuous)","run"),
   ("Long bike 1.5\u20133 h easy (skills + fuelling)","bike"),
   ("Rest / mobility","rest")],
 "Base":[("Easy swim 30 min + mobility (or rest)","swim"),("Run 40\u201350 min easy + short strength","run"),
   ("Swim 45\u201360 min endurance + bike 45 min easy","swim"),("Run 40\u201350 min easy + strides","run"),
   ("Swim 45\u201360 min + strength","swim"),("Long bike 90\u2013150 min Zone 2","bike"),("Long run 50\u201375 min Zone 2","run")],
 "Build & Integrate":[("Mobility / rest","rest"),("Bike intervals 60\u201375 min + short swim","bike"),
   ("Swim 60 min + easy run 40 min","swim"),("Run tempo 50\u201360 min","run"),
   ("Swim 60 min (open water) + strength","swim"),("BRICK: long bike 2\u20133 h \u2192 run 15\u201330 min","brick"),("Long run 75\u201390 min easy","run")],
 "Peak":[("Mobility / rest","rest"),("Bike race-pace intervals 75\u201390 min + short swim","bike"),
   ("Swim 60\u201375 min + easy run 40 min","swim"),("Run threshold 60 min","run"),
   ("Open-water swim 60\u201375 min + light spin","swim"),("RACE BRICK: bike 3\u20133.5 h \u2192 run 30\u201345 min","brick"),("Long run 90\u2013120 min (fuel practice)","run")],
 "Taper & Race":[("Mobility / rest","rest"),("Bike 45\u201360 min + race-pace bursts","bike"),
   ("Swim 40 min + run 30 min strides","swim"),("Bike 40 min easy / swim 30 min","bike"),
   ("Run 20\u201330 min easy openers","run"),("Short swim + spin / pre-race","swim"),("Long session if >2 wks out, else rest","run")],
}
RACE_WEEK = [("Mobility / short swim openers","swim"),("Bike 30 min easy + 3\u00d72 min race pace","bike"),
  ("Swim 20 min easy + run 15 min strides","run"),("Travel / register / rack bike","rest"),
  ("Short swim + spin, legs loose","swim"),("Rest \u2014 prep transition bags, early night","rest"),
  ("RACE DAY \u2014 IRONMAN 70.3 La Quinta","brick")]

# Phase-appropriate average paces (beginner -> trained). Used to convert
# bike/run time into realistic distance. Run = min/km, Bike = km/h.
RUN_PACE = {"Foundation":8.0,"Base":7.25,"Build & Integrate":6.75,"Peak":6.5,"Taper & Race":6.5}
BIKE_SPD = {"Foundation":20,"Base":23,"Build & Integrate":26,"Peak":28,"Taper & Race":28}
KM_PER_MI = 1.60934
def half(x): return round(x*2)/2

weeks = []
for w in range(1, N_WEEKS+1):
    ph = phase_of(w)
    monday = START + timedelta(weeks=w-1)
    th = total_hours(w)
    sf,bf,rf,stf,brf = FRACT[ph]
    hours = {"swim":q(th*sf),"bike":q(th*bf),"run":q(th*rf),"strength":q(th*stf),"brick":q(th*brf)}
    found_days = None
    found_dist = None
    deload_flag = is_deload(w)
    if ph == "Foundation":
        # Fixed 7-day weekly format (2 runs, 2 swims, 2 bikes, 3 strength blocks).
        # Weekly distance targets are an explicit linear progression across the
        # 16-week phase: bike 40 -> 50 mi, run 9 -> 12 mi. Session durations are
        # derived from those targets at the Foundation pace assumptions so the
        # daily breakdown always sums to the weekly target.
        deload_flag = False              # steady progression, no recovery dip
        p = (w - 1) / 15.0
        run_mi  = 9.0 + 3.0 * p
        bike_mi = 40.0 + 10.0 * p
        run_km  = run_mi * KM_PER_MI
        bike_km = bike_mi * KM_PER_MI
        run_total  = run_km * RUN_PACE[ph]            # minutes (8 min/km)
        bike_total = bike_km / BIKE_SPD[ph] * 60.0    # minutes (20 km/h)
        def r5(x): return int(round(x/5.0)*5)
        short_run = r5(40 + 20 * p)                   # Mon, ramps 40 -> 60 min
        long_run  = r5(run_total - short_run)         # Sat, remainder
        bk1       = 60                                # Wed, fixed Zone 2 hour
        long_bike = r5(bike_total - bk1)              # Sun, remainder
        sw1, sw2  = 30, 60                            # Tue 30, Thu 60
        st        = 40                                # strength block (x3)
        run_h = (short_run + long_run) / 60.0
        bike_h = (bk1 + long_bike) / 60.0
        swim_h = (sw1 + sw2) / 60.0
        strength_h = (st * 3) / 60.0
        hours = {"swim":q(swim_h),"bike":q(bike_h),"run":q(run_h),"strength":q(strength_h),"brick":0.0}
        found_dist = {
            "run_km": round(run_mi * KM_PER_MI, 1),  "run_mi": round(run_mi, 1),
            "bike_km": round(bike_mi * KM_PER_MI),   "bike_mi": round(bike_mi, 1),
        }
        found_days = [
            [("Zone 2 short run %d min" % short_run, "run")],
            [("Mixed strength %d min" % st, "strength"), ("Swim %d min technique" % sw1, "swim")],
            [("Upper-body strength %d min" % st, "strength"), ("Bike %d min Zone 2" % bk1, "bike")],
            [("Leg strength %d min" % st, "strength"), ("Swim %d min" % sw2, "swim")],
            [("Rest day", "rest")],
            [("Zone 2 long run %d min" % long_run, "run")],
            [("Long bike %d min" % long_bike, "bike")],
        ]
    elif ph == "Base":
        # 7-day Base format: Mon rest, Tue upper-body + swim + brick,
        # Wed lower-body + brick, Thu swim + brick, Fri rest, Sat long ride,
        # Sun long run. Weekly distance targets progress linearly across the
        # 20-week phase (bike 50 -> 70 mi, run 12 -> 16 mi). The long weekend
        # sessions take the lion's share; three midweek bricks split the rest
        # and grow with the weekly target (progressive bricks).
        deload_flag = False
        p = (w - 17) / 19.0
        bike_mi = 50.0 + 20.0 * p
        run_mi  = 12.0 + 4.0 * p
        bike_km = bike_mi * KM_PER_MI
        run_km  = run_mi * KM_PER_MI
        bike_total = bike_km / BIKE_SPD[ph] * 60.0    # minutes (26 km/h)
        run_total  = run_km * RUN_PACE[ph]            # minutes (6.75 min/km)
        def r5(x): return int(round(x/5.0)*5)
        long_ride  = r5(bike_total * 0.55)            # Sat
        brick_bike = r5((bike_total - long_ride) / 3.0)
        long_run   = r5(run_total * 0.60)             # Sun
        brick_run  = r5((run_total - long_run) / 3.0)
        sw1, sw2 = 45, 45                             # Tue, Thu endurance swims
        st = 45                                       # upper / lower body blocks
        bike_h = (3 * brick_bike + long_ride) / 60.0
        run_h  = (3 * brick_run + long_run) / 60.0
        swim_h = (sw1 + sw2) / 60.0
        strength_h = (st * 2) / 60.0
        # Brick time is already counted inside bike_h + run_h, so keep brick=0
        # to avoid double-counting the weekly total.
        hours = {"swim":q(swim_h),"bike":q(bike_h),"run":q(run_h),"strength":q(strength_h),"brick":0.0}
        found_dist = {
            "run_km": round(run_mi * KM_PER_MI, 1),  "run_mi": round(run_mi, 1),
            "bike_km": round(bike_mi * KM_PER_MI),   "bike_mi": round(bike_mi, 1),
        }
        brick_lbl = "Brick: bike %d min \u2192 run %d min" % (brick_bike, brick_run)
        found_days = [
            [("Rest day", "rest")],
            [("Upper-body strength %d min" % st, "strength"), ("Swim %d min" % sw1, "swim"), (brick_lbl, "brick")],
            [("Lower-body strength %d min" % st, "strength"), (brick_lbl, "brick")],
            [("Swim %d min" % sw2, "swim"), (brick_lbl, "brick")],
            [("Rest day", "rest")],
            [("Long ride %d min" % long_ride, "bike")],
            [("Long run %d min" % long_run, "run")],
        ]
    elif ph == "Build & Integrate":
        # Original time-based Build schedule, but with dedicated strength split:
        # upper body on Tue, lower body on Thu (each a separate, checkable item).
        # Strength is removed from Friday since it now lives on Tue/Thu.
        found_days = [
            [("Mobility / rest", "rest")],
            [("Bike intervals 60\u201375 min + short swim", "bike"), ("Upper-body strength 40 min", "strength")],
            [("Swim 60 min + easy run 40 min", "swim")],
            [("Run tempo 50\u201360 min", "run"), ("Lower-body strength 40 min", "strength")],
            [("Swim 60 min (open water)", "swim")],
            [("BRICK: long bike 2\u20133 h \u2192 run 15\u201330 min", "brick")],
            [("Long run 75\u201390 min easy", "run")],
        ]
    elif ph == "Peak":
        # Original time-based Peak schedule with dedicated strength split:
        # upper body on Tue, lower body on Thu (Friday becomes rest globally).
        found_days = [
            [("Mobility / rest", "rest")],
            [("Bike race-pace intervals 75\u201390 min + short swim", "bike"), ("Upper-body strength 40 min", "strength")],
            [("Swim 60\u201375 min + easy run 40 min", "swim")],
            [("Run threshold 60 min", "run"), ("Lower-body strength 40 min", "strength")],
            [("Open-water swim 60\u201375 min + light spin", "swim")],
            [("RACE BRICK: bike 3\u20133.5 h \u2192 run 30\u201345 min", "brick")],
            [("Long run 90\u2013120 min (fuel practice)", "run")],
        ]
    elif ph == "Taper & Race" and w != N_WEEKS:
        # Taper weeks keep the strength split but LIGHT/short to stay fresh.
        found_days = [
            [("Mobility / rest", "rest")],
            [("Bike 45\u201360 min + race-pace bursts", "bike"), ("Upper-body strength (light) 25 min", "strength")],
            [("Swim 40 min + run 30 min strides", "swim")],
            [("Bike 40 min easy / swim 30 min", "bike"), ("Lower-body strength (light) 25 min", "strength")],
            [("Run 20\u201330 min easy openers", "run")],
            [("Short swim + spin / pre-race", "swim")],
            [("Long session if >2 wks out, else rest", "run")],
        ]
    if w == N_WEEKS:
        hours = {"swim":1.0,"bike":1.5,"run":1.0,"strength":0.0,"brick":0.5}
    hours["total"] = round(sum(hours.values()),2)
    if found_dist is not None:
        dist = found_dist
    else:
        # Distances (bike & run) derived from the hours above
        run_km  = half(hours["run"] * 60.0 / RUN_PACE[ph])
        bike_km = round(hours["bike"] * BIKE_SPD[ph])
        dist = {
            "run_km": run_km,   "run_mi": round(run_km/KM_PER_MI,1),
            "bike_km": bike_km, "bike_mi": round(bike_km/KM_PER_MI,1),
        }
    block = "Recovery" if deload_flag else ("Race Week" if w==N_WEEKS else ("Taper" if ph=="Taper & Race" else "Build"))
    # Build the 7-day model. Foundation uses combined-item days; every other
    # phase / race week maps one session per day (single-item bundles).
    if found_days is not None:
        days = [[{"label":l,"sport":s} for (l,s) in day] for day in found_days]
    elif w == N_WEEKS:
        days = [[{"label":l,"sport":s}] for (l,s) in RACE_WEEK]
    else:
        days = [[{"label":l,"sport":s}] for (l,s) in TEMPLATES[ph]]
    # Global rule: every Friday (canonical day index 4) is a rest day.
    if len(days) > 4:
        days[4] = [{"label":"Rest day","sport":"rest"}]
    weeks.append({
        "n": w, "weekOf": monday.isoformat(), "phase": ph, "block": block,
        "hours": hours, "dist": dist, "focus": focus_note(w), "key": key_session(w),
        "milestone": (w in MILES) or (w==N_WEEKS),
        "deload": deload_flag,
        "days": days,
    })

paces = {p: {"run_min_km": RUN_PACE[p], "bike_kmh": BIKE_SPD[p]} for p in RUN_PACE}
WEEKDAYS = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
PHASES = ["Foundation","Base","Build & Integrate","Peak","Taper & Race"]
data = {"start": START.isoformat(), "race": RACE.isoformat(), "nWeeks": N_WEEKS,
        "weekdays": WEEKDAYS, "phases": PHASES,
        "paces": paces, "weeks": weeks}
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "plan_data.json"),"w") as f:
    json.dump(data, f, ensure_ascii=False, separators=(",",":"))
print("weeks:", len(weeks), "total planned hours:", round(sum(x["hours"]["total"] for x in weeks),1))
