import sys
import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Inject core path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.middleware import EpistemicFirewallMiddleware
from fas_phase2_core import JurisprudenceState
from fas_digital_twin import DigitalTwinJurisprudentialEngine

app = FastAPI(
    title="CORTEX-FAS Regulatory Dynamics Engine",
    description="Interpretative Risk Simulator for Legal Systems Under Stress. STRICTLY COUNTERFACTUAL.",
    version="6.0.0"
)

# Apply Epistemic Firewall
app.add_middleware(EpistemicFirewallMiddleware)

# Integrate Stripe Webhook Router
from api.webhook_handler import router as stripe_router
app.include_router(stripe_router)

class OutputContract(BaseModel):
    mode: str
    epistemic_status: str
    regime: str
    metrics: dict
    interpretation: str

@app.get("/health")
def health_check():
    return {"status": "operational", "epistemic_status": "counterfactual_only"}

@app.post("/stress_test", response_model=OutputContract)
def run_stress_test():
    """
    Executes a baseline synthetic stress test using the JEF and Lyapunov engines.
    """
    state = JurisprudenceState()
    # Baseline constraints
    state.drift_vector["art13_lgt_strength"] = 0.50
    state.drift_vector["donation_skepticism"] = 0.50
    
    twin = DigitalTwinJurisprudentialEngine(state)
    try:
        analysis = twin.analyze_full()
        return OutputContract(
            mode="adversarial_stress_simulation",
            epistemic_status="counterfactual_only",
            regime=analysis["regime"],
            metrics={
                "energy": analysis["energy"]["E_total"],
                "lyapunov": analysis["lyapunov"]["lambda"],
                "flip_probability": analysis["lyapunov"]["flip_probability"]
            },
            interpretation="sensitivity to assumption perturbation calculated"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analyze")
def analyze_state():
    return run_stress_test()

@app.get("/regime")
def get_regime():
    res = run_stress_test()
    return {"regime": res.regime, "epistemic_status": res.epistemic_status}

@app.get("/lyapunov")
def get_lyapunov():
    res = run_stress_test()
    return {"lyapunov": res.metrics["lyapunov"], "epistemic_status": res.epistemic_status}
