

import json
import os

try:
    from google import genai
except ImportError:
    genai = None

with open("narrator/findings.json", "r") as file:
    findings = json.load(file)
# ==========================================
# Task 2 & 3: Gemini SCR Narrative Generator
# - Generate Situation, Complication, Resolution
# - Use only verified findings
# - Use deterministic settings and error handling
# ==========================================

def generate_scr_narrative(findings: dict) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return {
            "status": "error",
            "narrative": None,
            "message": "GEMINI_API_KEY not found."
        }
    system_instruction = """
    You are a senior data analyst writing for Mamaearth's regional ops and finance heads.

    Write the business narrative using exactly three labeled sections:
    Situation
    Complication
    Resolution

    Every number in the output must come from the supplied findings and must appear
    with the same value. Do not invent, estimate, or modify any statistics.
      """
    user_prompt = f"""
      Using only the verified findings below, write an SCR business narrative.

      Verified findings:
      {json.dumps(findings, indent=2)}
      """
    try:
        client = genai.Client(
            api_key=api_key,
            http_options={"timeout": 10000}
        )

        response = client.models.generate_content(
              model="gemini-3.8-flash",
              contents=user_prompt,
              config={
                  "system_instruction": system_instruction,
                  "temperature": 0.0,  # Deterministic factual business report, not creative writing
                  "max_output_tokens": 500
              }
          )

        return {
              "status": "success",
              "narrative": response.text,
              "tokens": response.usage_metadata.total_token_count
          }

    except Exception as err:
      return {
                "status": "error",
                "narrative": None,
                "message": str(err)
            }
# ==========================================
# Task 4: Deterministic Offline Fallback
# - Runs without an API key or network call
# - Uses only verified findings
# - Produces the same SCR structure
# ==========================================
def generate_scr_narrative_offline(findings: dict) -> dict:
    situation = f"""
Situation:
The raw revenue was ₹{findings['raw_total_revenue_inr']:,.2f}.
After removing duplicate records, the cleaned revenue was ₹{findings['cleaned_total_revenue_inr']:,.2f}.
The duplicate-driven reconciliation difference was ₹{findings['duplicate_reconciliation_delta_inr']:,.2f}.
"""
    complication = f"""
Complication:
Returns are concentrated in COD orders, which have a {findings['return_rate_by_payment']['COD']:.1f}% return rate.
COD orders from Tier {findings['highest_risk_segment']['city_tier']} cities show the highest-risk segment return rate at {findings['highest_risk_segment']['return_rate_pct']:.1f}%.
"""
    resolution = f"""
Resolution:
January appeared to generate ₹{findings['outlier_inflated_month']['apparent_revenue_inr']:,.2f}, but after accounting for the flagged bulk-order outliers, its corrected revenue was ₹{findings['outlier_inflated_month']['corrected_revenue_inr']:,.2f}.
The true peak revenue month was March 2026 at ₹{findings['true_peak_month']['revenue_inr']:,.2f}.
Management should therefore use the cleaned and outlier-aware revenue picture when interpreting business performance.
"""
    narrative = situation + complication + resolution

    return {
        "status": "success",
        "narrative": narrative,
        "tokens": 0
    }
# ==========================================
# Task 5: Narrative Verification Checker
# - Normalizes commas before validation
# - Verifies all five mandatory figures
# - Prints PASS/FAIL for each requirement
# ==========================================
def check_narrative(narrative: str):
    normalized = narrative.replace(",", "")

    # 1. Cleaned total revenue
    if "97358.30" in normalized or "97358.3" in normalized:
        print("PASS - Cleaned revenue")
    else:
        print("FAIL - Cleaned revenue")

    # 2. COD return rate
    if "44.4" in normalized:
        print("PASS - COD return rate")
    else:
        print("FAIL - COD return rate")

    # 3. COD + Tier 2 highest-risk return rate
    if "54.5" in normalized:
        print("PASS - COD + Tier 2 highest-risk return rate")
    else:
        print("FAIL - COD + Tier 2 highest-risk return rate")

    # 4. Duplicate-driven reconciliation delta
    if "2501.90" in normalized or "2501.9" in normalized:
        print("PASS - Duplicate reconciliation delta")
    else:
        print("FAIL - Duplicate reconciliation delta")

    # 5. True peak month and revenue
    if "March" in normalized and (
        "20318.90" in normalized or "20318.9" in normalized
    ):
        print("PASS - True peak month and revenue")
    else:
        print("FAIL - True peak month and revenue")
# ==========================================
# Run Narrator with Automatic Fallback
# ==========================================
result = generate_scr_narrative(findings)

if result["status"] == "error":
    print("Gemini API unavailable or not configured. Using offline fallback.")
    result = generate_scr_narrative_offline(findings)

with open("narrator/sample_output.txt", "w", encoding="utf-8") as file:
    file.write(result["narrative"])

print(result["narrative"])
check_narrative(result["narrative"])
