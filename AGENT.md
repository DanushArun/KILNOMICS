# KILNOMICS — Build Prompt & Context Specification

**A multi-plant clinker-to-cement profitability, quality & energy optimization platform**

**Purpose of this document.** This is the founding context and build brief for an external engineering/ML team. It defines what the system must understand about cement manufacturing, the data it will ingest, the analysis and correlation layer it must compute, and the dashboard it must present. It contains no client data — every number the system works on arrives at runtime via the ingestion template. All domain values below are ranges, rules of thumb, and physical relationships, not client figures.

---

## 0. One-sentence brief

Build a grey-box decision-support platform that ingests per-plant cement manufacturing data (raw materials, fuel, clinker, cement, energy, process, cost), learns the correlations between process/quality parameters from historical data, and on current data returns actionable, cost-quantified recommendations to optimize the clinker-to-cement value chain — benchmarked across multiple structurally-different plants.

The system has two parts:

* **Backend** — an ML + chemistry-informed analytical engine that ingests Excel workbooks, fits/validates the parameter relationships, and computes recommendations and their rupee impact.
* **Frontend** — a dashboard that visualizes profitability, quality, energy, cross-plant benchmarks, correlations, and a what-if / recommendation engine.

---

## 1. Domain context the model MUST encode

This is a cement operation. The system reasons over the full chain. Every plant is structurally different — different number of kiln lines, different rated capacities, different preheater stages, cooler generation, mill types, WHRS configuration, mine geology, and fuel basket. No two machines are identical. The single most important design principle follows from this:

### 1.1 Scale vs. intensive — the cardinal rule

Every parameter must be classified as either:

* **Scale (absolute)** — tied to plant/kiln/line size (e.g. total kWh, clinker MT, running hours, TG generation MW, kiln feed TPH). Never benchmarked across plants directly.
* **Intensive (normalized)** — per-tonne, %, ratio, temperature, or moduli (e.g. kWh/t clinker, SHC kcal/kg, TSR %, LSF, clinker factor, ₹/t). These are the only cross-plant-comparable quantities.

The dashboard must visibly tag every metric as scale or intensive, and cross-plant comparisons must only ever use intensive metrics (or scale metrics normalized to rated capacity, e.g. utilization %).

### 1.2 The four pillars (one system, not four)

* **Raw materials & raw mix** $\rightarrow$ limestone + correctives set clinker chemistry (LSF, SM, AM).
* **Fuel & AFR** $\rightarrow$ set heat (SHC), flame, and the sulfur/chlorine/alkali cycles that bound how much AFR is feasible.
* **Clinker & pyroprocessing** $\rightarrow$ chemistry + burnability + kiln performance produce clinker of a given grade at a given energy cost.
* **Cement & SKUs** $\rightarrow$ clinker grade determines how much SCM (fly ash/slag/limestone) can dilute it while holding strength/colour/BIS — which sets clinker factor, the biggest cost lever.

### 1.3 Core physical/chemistry relationships to embed (grey-box, not black-box)

* Bogue equations for $\text{C}_3\text{S}/\text{C}_2\text{S}/\text{C}_3\text{A}/\text{C}_4\text{AF}$ from oxides.
* Moduli:
  $$\text{LSF} = \frac{\text{CaO}}{2.8 \cdot \text{SiO}_2 + 1.18 \cdot \text{Al}_2\text{O}_3 + 0.65 \cdot \text{Fe}_2\text{O}_3}$$
  $$\text{SM} = \frac{\text{SiO}_2}{\text{Al}_2\text{O}_3 + \text{Fe}_2\text{O}_3}$$
  $$\text{AM} = \frac{\text{Al}_2\text{O}_3}{\text{Fe}_2\text{O}_3}$$
* **Burnability:** free-lime and burning-zone energy as functions of LSF, SM, and fineness — higher LSF/$\text{C}_3\text{S}$ costs more heat and risks higher free lime.
* **TSR ceiling:** maximum feasible thermal substitution bounded by fuel sulfur + chlorine + circulating (alkali-sulfur) balance and preheater build-up risk — not a free variable.
* **Strength $\leftrightarrow$ clinker factor $\leftrightarrow$ Blaine:** 28-day strength as a function of clinker $\text{C}_3\text{S}$, SCM %, and fineness — the relationship that governs how far the clinker factor can be pushed down.
* **Two-level profitability:**
  * **Clinker level** = cost leadership $\times$ throughput (₹/t clinker: fuel + power + limestone + additives + stores).
  * **Cement level** = contribution margin per tonne cement = realization $-$ (clinker cost $\times$ clinker factor + SCM cost + grinding + gypsum + freight). This is the real KPI.

### 1.4 Themes to optimize (the "so-what" the dashboard must produce)

Fuel-mix / AFR increase $\cdot$ SHC / heat-loss reduction $\cdot$ false-air reduction $\cdot$ WHRS recovery $\cdot$ limestone consumption $\cdot$ clinker-factor reduction (max SCM at constant strength) $\cdot$ power (kWh/t) reduction $\cdot$ SKU-mix margin optimization $\cdot$ downtime/reliability (lost-tonnes value).

---

## 2. Backend — the analytical / ML engine

### 2.1 Ingestion

Accept one workbook per plant in the fixed 15-sheet schema (Section 4). Validate schema, units, and ranges on load; reject/flag out-of-range values. Support 6+ months of daily data per plant. The system holds no data of its own — everything is user-fed at runtime.

### 2.2 Two computational layers

* **Chemistry core (deterministic, grey-box):** Bogue, moduli, burnability, TSR ceiling, least-cost raw-mix and fuel-mix solver (start with a coarse grid; upgrade to a proper LP/simplex under stated linear constraints), and BIS-bound differentiated SCM fill per SKU. These are known physics — hard-code them, do not "learn" them.
* **Correlation / soft-sensor layer (learned):** from historical daily data, fit and back-test the empirical relationships that physics doesn't pin down exactly — e.g. strength vs ($\text{C}_3\text{S}$, SCM %, Blaine); free-lime vs (LSF, SM, burning-zone temp); SHC vs (false air, PH exit temp, feed variability); fan power vs production (false-air proxy). Report Pearson/parametric fits with sample size and confidence, and never present a small-$n$ correlation as causation.

### 2.3 Correlation requirements

* Compute a full correlation matrix across process, quality, energy, and cost parameters.
* Distinguish within-plant correlations (for that plant's soft-sensors) from cross-plant benchmarking (intensive metrics only).
* Flag confounders explicitly (e.g. a production dip that is really downtime, not quality; a limestone-consumption gap that is really ore grade, not inefficiency).
* Every correlation surfaced to the user must carry: $n$, direction, strength band, and a plain-language "reading" + a caution if it's small-sample or confounded.

### 2.4 Recommendation engine — "solve, then diff"

For current fed data, compute the optimal (least-cost-at-constraint) raw mix, fuel/AFR blend, and cement blend, then present before $\rightarrow$ after with:

* the changed variables,
* the constraint checks (BIS min/max, TSR ceiling, free-lime bound, $\text{SO}_3$, chlorine, colour),
* burnability/energy feedback (does the new mix cost more heat?),
* and the net ₹/tonne and annualized ₹ impact. Recommendations must be actionable and costed, ranked by impact, and labelled by confidence (firm vs. investigate) exactly as a consulting recommendation would be.

### 2.5 Cross-plant benchmarking module

For each intensive metric, identify the best-performing plant/line and compute the gap value for the others (the internal good-practice-transfer logic). Attach the specific initiative required to close each gap and its rupee value. Keep "structural difference" (e.g. a line lacking solid-AFR infrastructure, a different WHRS boiler config, poorer mine grade) separate from "performance gap" — never credit a structural difference as a capturable saving.

### 2.6 Honesty / maturity guardrails (must be built in, not bolted on)

* Clearly mark which relationships are trained on real data vs parametric stand-ins awaiting training/back-test.
* Show data-status (have / partial / missing) per parameter per plant.
* Every rupee figure carries its basis and a confidence tier.
* Not-yet-modelled items must be listed, not silently omitted (see roadmap).

---

## 3. Frontend — the dashboard

**Views (mirroring and extending the reference tool):**

* **Home / Executive** — portfolio KPIs across plants: contribution margin ₹/t, clinker cost ₹/t, SHC, kWh/t, TSR %, clinker factor. Scale vs intensive clearly separated.
* **Profitability** — two-level view (clinker cost leadership; cement contribution margin), per-product margin map.
* **Compare Plants** — intensive-only benchmarking with best-in-class highlighted and gap-to-best quantified.
* **Raw / Fuel / Clinker / Energy / Cement detail views** — parameter trends, targets, BAT reference bands.
* **Correlation Explorer** — interactive matrix + scatter, with $n$ and confidence shown.
* **What-if Optimizer** — user pulls levers (LSF, TSR, SCM %, Blaine…); constraints check live; net ₹ impact updates.
* **Recommendation Engine** — computed before$\rightarrow$after with costed, ranked, confidence-tagged actions.
* **Data Status / Maturity** — have/partial/missing per plant, and which relationships are trained vs stand-in.

**Design:** clean, analyst/partner-facing (not flashy). Every comparison view enforces the scale/intensive rule. Every number traceable to an input.

---

## 4. Ingestion schema (15 sheets — one workbook per plant, 6 months daily)

### Library / static sheets:

* **PlantMaster** — `plant_id`, `plant_name`, `kiln_line_id`, `rated_clinker_tpd`, `preheater_stages`, `calciner_type`, `cooler_generation`, `raw_mill_type`, `coal_mill_type`, `cement_mill_type`, `WHR_capacity_MW`, `altitude_m`.
* **MaterialSources** — `plant_id`, `id`, `name`, `category`, `CaO`, `SiO2`, `Al2O3`, `Fe2O3`, `MgO`, `K2O`, `Na2O`, `SO3` (+ `cost`, `moisture`).
* **FuelLibrary** — `plant_id`, `id`, `name`, `category`, `ncvKcalPerKg`, `moisturePct`, `ashPct`, `volatileMatterPct`, `sulfurPct`, `chlorinePct`, `HGI`, `biogenicFraction` (+ `cost`).
* **CementConstituents** — `plant_id`, `id`, `name`, `type`, `costPerTon`, `availabilityTpm`, `BIS_min_pct`, `BIS_max_pct`, `strength_activity_index`, `moisture_pct`, `blaine_m2kg`.
* **KilnConfig** — `plant_id`, `clinkerTPD`, `dustLoss`, `freeLime`, `bypassAvailable`, `tsrMaxPct`, `mainBurnerMinPct`.
* **Targets** — `plant_id`, `parameter`, `min`, `max`, `hard(bool)`, `comment`.
* **ProductRecipe** — `plant_id`, `product`, `BIS_type`, `target_grade_MPa`, `clinker_factor`, `scm_id`, `scm_pct`, `gypsum_pct`, `target_blaine_m2kg`, `NSR_per_ton`, `monthly_volume_t`, `lead_distance_km`.

### Time-series sheets (daily, feed the correlation/soft-sensor layer):

* **KilnFeedDaily** — `date`, `shift`, `feed_rate_tph`, `LSF`, `SM`, `AM`, `CaO`, `SiO2`, `Al2O3`, `Fe2O3`, `MgO`.
* **FuelDaily** — `date`, `shift`, `fuel_id`, `qty_tonnes`, `as_fired_NCV_kcalkg`, `TSR_pct`.
* **ClinkerDaily** — `date`, `shift`, `C3S`, `C2S`, `C3A`, `C4AF`, `fCaO_mean`, `fCaO_SD`, `litre_weight_gL`, `LSF`, `SM`.
* **CementDaily** — `date`, `product`, `clinker_factor`, `blaine_m2kg`, `residue_45um_pct`, `str_1d/3d/7d/28d_MPa`, `setting_init/final_min`.
* **EnergyDaily** — `date`, `clinker_tonnes`, `cement_tonnes`, `SHC_kcalkg`, `kWh_crushing`, `kWh_rawgrind`, `kWh_kilnfans`, `kWh_coalmill`, `kWh_cementgrind`, `kWh_utilities`, `WHR_generation_kWh`.
* **ProcessDaily** — `date`, `shift`, `burning_zone_temp_C`, `PH_exit_temp_C`, `PH_exit_O2_pct`, `PH_exit_CO_pct`, `secondary_air_temp_C`, `false_air_pct`, `kiln_torque_pct`, `downtime_min`, `downtime_cause`.
* **CircLoad** — `date`, `hotmeal_SO3_pct`, `hotmeal_Cl_pct`, `hotmeal_alkali_Na2Oeq_pct`, `bypass_dust_tonnes`, `alkali_sulfur_ratio`.

### Cost layer (attach to every parameter):

Clinker variable cost split (fuel/power/limestone/additives/stores) ₹/t; power ₹/kWh by source (grid/captive/WHRS); fuel ₹/1000 kcal by grade; SCM & gypsum ₹/t; freight ₹/t·km; product realization (NSR) ₹/t.

---

## 5. The final synthesis the platform must deliver

Per plant, a production-function statement of the form:

> "xx limestone (at xx grade) + xx additive/SCM mix, at xx heat (SHC) and xx power (kWh/t), yields xx-grade clinker ($\text{C}_3\text{S}$/free lime), which supports xx% SCM in the SKU blend to produce cement at xx contribution margin ₹/t."

Cross-plant, this becomes: which plant's recipe (not scale) delivers the lowest cost per tonne of cement at equivalent quality — and which specific coefficients (LSF, TSR, clinker factor, kWh/t, SHC) each plant should adopt from whichever sister plant does it best, with each transfer costed and confidence-tagged.

---

## 6. Explicitly out of scope for v1 (state, don't silently omit)

Liquid-phase / coating-risk model $\cdot$ $\text{SO}_3$ optimum $\cdot$ grinding energy vs SCM/Blaine trade-off $\cdot$ durability spec (beyond strength) $\cdot$ multi-objective Pareto front. These are roadmap items; the architecture should leave hooks for them but not fake them.

---

## 7. Build guardrails (non-negotiable)

1. No client data is embedded — the platform is empty until a plant workbook is loaded.
2. Grey-box, not black-box — known chemistry is coded; only genuinely empirical relationships are learned, and those are back-tested and confidence-scored.
3. Scale vs intensive is enforced everywhere — no cross-plant comparison on absolute numbers.
4. Every recommendation is costed, ranked, and confidence-tagged (firm vs investigate).
5. Structural differences are never sold as capturable savings.
6. Data status and model maturity are always visible — the user must always know what is measured, what is assumed, and what is still a stand-in.
7. Input schema can be changed use synthetic realistic parameter correlations don’t leave blank like prompt said.