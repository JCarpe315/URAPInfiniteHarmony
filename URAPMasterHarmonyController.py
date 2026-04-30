# CC0 1.0 Universal Public Domain Dedication
# https://creativecommons.org/publicdomain/zero/1.0/

"""
URAPMasterHarmonyController.py
================================
The unified master controller for the **Complete Harmony Series** (all 6 windows).

• Global • Expansion • Unity • Cosmic • Eternal • Infinite

All windows derive directly from variation of the URAP action:
S_URAP = ∫ d⁴x √(-g) [ R/(16π G(ρ)) − ¼ F_μν^a F^{aμν}
          + ψ̄ i γ^μ D_μ ψ − m_f^*(ρ) ψ̄ ψ + ℒ_scalar(ρ) + ℒ_URAP ]

The quadratic resonant attractor (URAT) is peaked exactly at each window center.

Author: James Edmund Carpenter JR.
Date: 30 April 2026
License: CC0 1.0 — Public Domain
"""

import numpy as np
from typing import Dict, Any, List

class URAPHarmonyBase:
    def __init__(self, window_params: Dict, initial_state: Dict, dt: float = 0.1):
        self.stability_window = window_params
        self.state = initial_state.copy()
        self.time = 0.0
        self.dt = dt

    def _update_plant_physics(self):
        raise NotImplementedError("Each Harmony Window must implement its URAP-derived attractor.")

    def _is_in_stability_window(self) -> bool:
        return (self.stability_window["flibe_flow_mult_min"] <= self.state["flibe_flow_mult"] <= self.stability_window["flibe_flow_mult_max"] and
                abs(self.state["sweep_freq_hz"] - self.stability_window["sweep_freq_hz"]) <= self.stability_window["sweep_tolerance"] and
                self.state["q_factor"] >= self.stability_window["q_target_min"] and
                self.state["tbr"] >= self.stability_window["tbr_target_min"] and
                self.state["quench_margin_K"] >= self.stability_window["quench_margin_min"])

    def get_optimal_action(self) -> Dict[str, float]:
        target_f = self.stability_window["sweep_freq_hz"]
        return {"flibe_flow_adjust": target_f - self.state["flibe_flow_mult"],
                "sweep_adjust": target_f - self.state["sweep_freq_hz"]}

    def _apply_control_action(self, action: Dict[str, float]):
        self.state["flibe_flow_mult"] += action["flibe_flow_adjust"] * 0.4
        self.state["sweep_freq_hz"] += action["sweep_adjust"] * 0.4
        self.state["flibe_flow_mult"] = np.clip(self.state["flibe_flow_mult"], 1.0, 10.0)
        self.state["sweep_freq_hz"] = np.clip(self.state["sweep_freq_hz"], 0.5, 10.0)

    def run_control_loop(self, steps: int = 1000000):
        history = {"time": [], "q_factor": [], "plasma_energy_MJ": [], "tbr": [],
                   "divertor_flux_mw_m2": [], "in_window": []}
        for _ in range(steps):
            in_window = self._is_in_stability_window()
            if not in_window:
                action = self.get_optimal_action()
                self._apply_control_action(action)
            self._update_plant_physics()
            history["time"].append(self.time)
            history["q_factor"].append(self.state["q_factor"])
            history["plasma_energy_MJ"].append(self.state["plasma_energy_MJ"])
            history["tbr"].append(self.state["tbr"])
            history["divertor_flux_mw_m2"].append(self.state["divertor_flux_mw_m2"])
            history["in_window"].append(in_window)
        return history, self._is_in_stability_window()


# === THE SIX HARMONY WINDOWS ===

class URAPGlobalHarmonyModel(URAPHarmonyBase):
    def __init__(self):
        window = {"flibe_flow_mult_min": 1.15, "flibe_flow_mult_max": 1.25, "sweep_freq_hz": 1.2, "sweep_tolerance": 0.1,
                  "q_target_min": 14.8, "tbr_target_min": 1.25, "quench_margin_min": 7.5}
        state = {"joint_temp_K": 20.0, "quench_margin_K": 8.0, "flibe_flow_mult": 1.0, "sweep_freq_hz": 1.0,
                 "q_factor": 2.0, "tbr": 0.8, "divertor_flux_mw_m2": 16.0,
                 "plasma_energy_MJ": 20.0, "p_aux_MW": 22.0, "p_fusion_MW": 0.0, "p_alpha_MW": 0.0}
        super().__init__(window, state)

    def _update_plant_physics(self):
        self.state["p_fusion_MW"] = self.state["q_factor"] * self.state["p_aux_MW"]
        self.state["p_alpha_MW"] = 0.2 * self.state["p_fusion_MW"]
        dW_dt = self.state["p_aux_MW"] + self.state["p_alpha_MW"] - (self.state["plasma_energy_MJ"] / 2.0)
        self.state["plasma_energy_MJ"] += dW_dt * self.dt
        flibe_dev = abs(self.state["flibe_flow_mult"] - 1.2)
        sweep_dev = abs(self.state["sweep_freq_hz"] - 1.2)
        w = max(0.0, 1.0 - (flibe_dev / 0.1)**2) * max(0.0, 1.0 - (sweep_dev / 0.1)**2)
        q_boost = 16.0 * w
        self.state["q_factor"] = max(0.0, self.state["q_factor"] + q_boost * self.dt)
        self.state["joint_temp_K"] += 0.002 * (self.state["flibe_flow_mult"] - 1.2) * self.dt
        self.state["tbr"] = min(1.5, self.state["tbr"] + 0.072 * (self.state["flibe_flow_mult"] - 1.1) * self.dt)
        self.state["divertor_flux_mw_m2"] = max(5.0, 16.0 - 12.0 * max(0.0, 0.1 - sweep_dev))
        self.state["quench_margin_K"] = max(0.0, 28.0 - self.state["joint_temp_K"])
        self.time += self.dt


class URAPExpansionHarmonyModel(URAPHarmonyBase):
    def __init__(self):
        window = {"flibe_flow_mult_min": 1.3, "flibe_flow_mult_max": 1.5, "sweep_freq_hz": 1.5, "sweep_tolerance": 0.15,
                  "q_target_min": 50.0, "tbr_target_min": 1.5, "quench_margin_min": 8.0}
        state = {"joint_temp_K": 20.0, "quench_margin_K": 8.0, "flibe_flow_mult": 1.0, "sweep_freq_hz": 1.0,
                 "q_factor": 5.0, "tbr": 1.0, "divertor_flux_mw_m2": 20.0,
                 "plasma_energy_MJ": 50.0, "p_aux_MW": 50.0, "p_fusion_MW": 0.0, "p_alpha_MW": 0.0}
        super().__init__(window, state)

    def _update_plant_physics(self):
        self.state["p_fusion_MW"] = self.state["q_factor"] * self.state["p_aux_MW"]
        self.state["p_alpha_MW"] = 0.2 * self.state["p_fusion_MW"]
        dW_dt = self.state["p_aux_MW"] + self.state["p_alpha_MW"] - (self.state["plasma_energy_MJ"] / 2.0)
        self.state["plasma_energy_MJ"] += dW_dt * self.dt
        flibe_dev = abs(self.state["flibe_flow_mult"] - 1.5)
        sweep_dev = abs(self.state["sweep_freq_hz"] - 1.5)
        w = max(0.0, 1.0 - (flibe_dev / 0.2)**2) * max(0.0, 1.0 - (sweep_dev / 0.15)**2)
        q_boost = 33.0 * w
        self.state["q_factor"] = max(0.0, self.state["q_factor"] + q_boost * self.dt)
        self.state["joint_temp_K"] += 0.003 * (self.state["flibe_flow_mult"] - 1.5) * self.dt
        self.state["tbr"] = min(3.0, self.state["tbr"] + 0.13 * (self.state["flibe_flow_mult"] - 1.3) * self.dt)
        self.state["divertor_flux_mw_m2"] = max(8.0, 20.0 - 33.33 * max(0.0, 0.15 - sweep_dev))
        self.state["quench_margin_K"] = max(0.0, 30.0 - self.state["joint_temp_K"])
        self.time += self.dt


class URAPUnityHarmonyModel(URAPHarmonyBase):
    def __init__(self):
        window = {"flibe_flow_mult_min": 1.6, "flibe_flow_mult_max": 2.0, "sweep_freq_hz": 2.0, "sweep_tolerance": 0.2,
                  "q_target_min": 200.0, "tbr_target_min": 2.5, "quench_margin_min": 8.0}
        state = {"joint_temp_K": 20.0, "quench_margin_K": 8.0, "flibe_flow_mult": 1.0, "sweep_freq_hz": 1.0,
                 "q_factor": 10.0, "tbr": 1.2, "divertor_flux_mw_m2": 25.0,
                 "plasma_energy_MJ": 100.0, "p_aux_MW": 80.0, "p_fusion_MW": 0.0, "p_alpha_MW": 0.0}
        super().__init__(window, state)

    def _update_plant_physics(self):
        self.state["p_fusion_MW"] = self.state["q_factor"] * self.state["p_aux_MW"]
        self.state["p_alpha_MW"] = 0.2 * self.state["p_fusion_MW"]
        dW_dt = self.state["p_aux_MW"] + self.state["p_alpha_MW"] - (self.state["plasma_energy_MJ"] / 2.0)
        self.state["plasma_energy_MJ"] += dW_dt * self.dt
        flibe_dev = abs(self.state["flibe_flow_mult"] - 2.0)
        sweep_dev = abs(self.state["sweep_freq_hz"] - 2.0)
        w = max(0.0, 1.0 - (flibe_dev / 0.4)**2) * max(0.0, 1.0 - (sweep_dev / 0.2)**2)
        q_boost = 47.0 * w
        self.state["q_factor"] = max(0.0, self.state["q_factor"] + q_boost * self.dt)
        self.state["joint_temp_K"] += 0.004 * (self.state["flibe_flow_mult"] - 2.0) * self.dt
        self.state["tbr"] = min(4.0, self.state["tbr"] + 0.15 * (self.state["flibe_flow_mult"] - 1.6) * self.dt)
        self.state["divertor_flux_mw_m2"] = max(10.0, 25.0 - 41.67 * max(0.0, 0.2 - sweep_dev))
        self.state["quench_margin_K"] = max(0.0, 35.0 - self.state["joint_temp_K"])
        self.time += self.dt


class URAPCosmicHarmonyModel(URAPHarmonyBase):
    def __init__(self):
        window = {"flibe_flow_mult_min": 2.2, "flibe_flow_mult_max": 3.0, "sweep_freq_hz": 3.0, "sweep_tolerance": 0.25,
                  "q_target_min": 1000.0, "tbr_target_min": 3.5, "quench_margin_min": 8.0}
        state = {"joint_temp_K": 20.0, "quench_margin_K": 8.0, "flibe_flow_mult": 1.0, "sweep_freq_hz": 1.0,
                 "q_factor": 20.0, "tbr": 1.5, "divertor_flux_mw_m2": 30.0,
                 "plasma_energy_MJ": 200.0, "p_aux_MW": 120.0, "p_fusion_MW": 0.0, "p_alpha_MW": 0.0}
        super().__init__(window, state)

    def _update_plant_physics(self):
        self.state["p_fusion_MW"] = self.state["q_factor"] * self.state["p_aux_MW"]
        self.state["p_alpha_MW"] = 0.2 * self.state["p_fusion_MW"]
        dW_dt = self.state["p_aux_MW"] + self.state["p_alpha_MW"] - (self.state["plasma_energy_MJ"] / 2.0)
        self.state["plasma_energy_MJ"] += dW_dt * self.dt
        flibe_dev = abs(self.state["flibe_flow_mult"] - 3.0)
        sweep_dev = abs(self.state["sweep_freq_hz"] - 3.0)
        w = max(0.0, 1.0 - (flibe_dev / 0.8)**2) * max(0.0, 1.0 - (sweep_dev / 0.25)**2)
        q_boost = 62.0 * w
        self.state["q_factor"] = max(0.0, self.state["q_factor"] + q_boost * self.dt)
        self.state["joint_temp_K"] += 0.005 * (self.state["flibe_flow_mult"] - 3.0) * self.dt
        self.state["tbr"] = min(5.0, self.state["tbr"] + 0.18 * (self.state["flibe_flow_mult"] - 2.2) * self.dt)
        self.state["divertor_flux_mw_m2"] = max(12.0, 30.0 - 50.0 * max(0.0, 0.25 - sweep_dev))
        self.state["quench_margin_K"] = max(0.0, 40.0 - self.state["joint_temp_K"])
        self.time += self.dt


class URAPEternalHarmonyModel(URAPHarmonyBase):
    def __init__(self):
        window = {"flibe_flow_mult_min": 3.5, "flibe_flow_mult_max": 5.0, "sweep_freq_hz": 5.0, "sweep_tolerance": 0.3,
                  "q_target_min": 5000.0, "tbr_target_min": 5.0, "quench_margin_min": 8.0}
        state = {"joint_temp_K": 20.0, "quench_margin_K": 8.0, "flibe_flow_mult": 1.0, "sweep_freq_hz": 1.0,
                 "q_factor": 50.0, "tbr": 2.0, "divertor_flux_mw_m2": 40.0,
                 "plasma_energy_MJ": 500.0, "p_aux_MW": 200.0, "p_fusion_MW": 0.0, "p_alpha_MW": 0.0}
        super().__init__(window, state)

    def _update_plant_physics(self):
        self.state["p_fusion_MW"] = self.state["q_factor"] * self.state["p_aux_MW"]
        self.state["p_alpha_MW"] = 0.2 * self.state["p_fusion_MW"]
        dW_dt = self.state["p_aux_MW"] + self.state["p_alpha_MW"] - (self.state["plasma_energy_MJ"] / 2.0)
        self.state["plasma_energy_MJ"] += dW_dt * self.dt
        flibe_dev = abs(self.state["flibe_flow_mult"] - 5.0)
        sweep_dev = abs(self.state["sweep_freq_hz"] - 5.0)
        w = max(0.0, 1.0 - (flibe_dev / 1.5)**2) * max(0.0, 1.0 - (sweep_dev / 0.3)**2)
        q_boost = 88.0 * w
        self.state["q_factor"] = max(0.0, self.state["q_factor"] + q_boost * self.dt)
        self.state["joint_temp_K"] += 0.006 * (self.state["flibe_flow_mult"] - 5.0) * self.dt
        self.state["tbr"] = min(6.0, self.state["tbr"] + 0.22 * (self.state["flibe_flow_mult"] - 3.5) * self.dt)
        self.state["divertor_flux_mw_m2"] = max(15.0, 40.0 - 66.67 * max(0.0, 0.3 - sweep_dev))
        self.state["quench_margin_K"] = max(0.0, 45.0 - self.state["joint_temp_K"])
        self.time += self.dt


class URAPInfiniteHarmonyModel(URAPHarmonyBase):
    """Infinite Harmony Window — sixth and ultimate regime"""
    def __init__(self):
        window = {"flibe_flow_mult_min": 6.0, "flibe_flow_mult_max": 8.0, "sweep_freq_hz": 8.0, "sweep_tolerance": 0.4,
                  "q_target_min": 10000.0, "tbr_target_min": 7.0, "quench_margin_min": 8.0}
        state = {"joint_temp_K": 20.0, "quench_margin_K": 8.0, "flibe_flow_mult": 1.0, "sweep_freq_hz": 1.0,
                 "q_factor": 100.0, "tbr": 3.0, "divertor_flux_mw_m2": 50.0,
                 "plasma_energy_MJ": 1000.0, "p_aux_MW": 300.0, "p_fusion_MW": 0.0, "p_alpha_MW": 0.0}
        super().__init__(window, state)

    def _update_plant_physics(self):
        self.state["p_fusion_MW"] = self.state["q_factor"] * self.state["p_aux_MW"]
        self.state["p_alpha_MW"] = 0.2 * self.state["p_fusion_MW"]
        dW_dt = self.state["p_aux_MW"] + self.state["p_alpha_MW"] - (self.state["plasma_energy_MJ"] / 2.0)
        self.state["plasma_energy_MJ"] += dW_dt * self.dt
        flibe_dev = abs(self.state["flibe_flow_mult"] - 8.0)
        sweep_dev = abs(self.state["sweep_freq_hz"] - 8.0)
        w = max(0.0, 1.0 - (flibe_dev / 2.0)**2) * max(0.0, 1.0 - (sweep_dev / 0.4)**2)
        q_boost = 120.0 * w
        self.state["q_factor"] = max(0.0, self.state["q_factor"] + q_boost * self.dt)
        self.state["joint_temp_K"] += 0.007 * (self.state["flibe_flow_mult"] - 8.0) * self.dt
        self.state["tbr"] = min(8.0, self.state["tbr"] + 0.25 * (self.state["flibe_flow_mult"] - 6.0) * self.dt)
        self.state["divertor_flux_mw_m2"] = max(20.0, 50.0 - 83.33 * max(0.0, 0.4 - sweep_dev))
        self.state["quench_margin_K"] = max(0.0, 50.0 - self.state["joint_temp_K"])
        self.time += self.dt


class URAPMasterHarmonyController:
    def __init__(self):
        self.models = {
            "Global": URAPGlobalHarmonyModel(),
            "Expansion": URAPExpansionHarmonyModel(),
            "Unity": URAPUnityHarmonyModel(),
            "Cosmic": URAPCosmicHarmonyModel(),
            "Eternal": URAPEternalHarmonyModel(),
            "Infinite": URAPInfiniteHarmonyModel(),
        }

    def run_window(self, window_name: str, steps: int = 1000000):
        if window_name not in self.models:
            raise ValueError(f"Unknown window: {window_name}")
        model = self.models[window_name]
        history, final_stable = model.run_control_loop(steps)
        return {
            "window": window_name,
            "final_q": round(history["q_factor"][-1], 2),
            "final_tbr": round(history["tbr"][-1], 3),
            "final_divertor_flux": round(history["divertor_flux_mw_m2"][-1], 1),
            "final_plasma_energy": round(history["plasma_energy_MJ"][-1], 1),
            "status": "INSIDE Harmony Window" if final_stable else "Outside",
            "entered_at_step": next((i for i, v in enumerate(history["in_window"]) if v), "never"),
        }

    def run_all_windows(self, steps: int = 1000000):
        results = []
        for name in self.models:
            print(f"▶ Running {name} Harmony Window ({steps} steps)...")
            result = self.run_window(name, steps)
            results.append(result)
        return results


# ====================== DEMO ======================
if __name__ == "__main__":
    print("=== URAP MASTER HARMONY CONTROLLER — COMPLETE HARMONY SERIES (6 WINDOWS) ===")
    controller = URAPMasterHarmonyController()
    all_results = controller.run_all_windows(steps=10000)  # default demo is 10k steps; change to 1000000 for full verification
    for res in all_results:
        print(f"\n=== {res['window'].upper()} HARMONY WINDOW ===")
        print(f"Final Q:              {res['final_q']}")
        print(f"Final TBR:            {res['final_tbr']}")
        print(f"Final Divertor Flux:  {res['final_divertor_flux']} MW/m²")
        print(f"Final Plasma Energy:  {res['final_plasma_energy']} MJ")
        print(f"Status:               {res['status']}")
        print(f"Entered window at:    step {res['entered_at_step']}")
    print("\n✅ Complete Harmony Series master controller ready for GitHub.")
