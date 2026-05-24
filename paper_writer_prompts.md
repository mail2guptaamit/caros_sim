# IEEE Paper Writing Prompts (CarOS-A2X PoC)

Use these prompts with ChatGPT/Codex to avoid writing everything manually. Replace placeholders in `{...}`.

## 1) Abstract (Structured, Conservative Claims)

```text
You are helping draft an IEEE-style abstract.

Task:
Write a 150-220 word abstract using the inputs below. Keep claims conservative and evidence-based. Do not claim real-world safety proof. Use neutral technical tone.

Inputs:
- Problem: {problem_statement}
- Method: {method_summary}
- Dataset/Scale: {episodes_runs_configs}
- Key Results: {top_3_numeric_results}
- Limitation: {main_limitation}
- Contribution: {main_contribution}

Rules:
- 1 paragraph only.
- Include at least 3 numeric results.
- Include one explicit limitation sentence.
- End with one sentence on future validation.
```

## 2) Introduction

```text
Draft an IEEE-style Introduction section (450-700 words).

Context:
- Domain: Autonomous driving software architecture
- Proposed system: CarOS-A2X
- Motivation: Reduce interventions while improving mission completion under OOD/hazard conditions

Include:
1. Problem background and gap in current stacks.
2. Why confidence-aware policy + hybrid fallback + agentic mission layer is relevant.
3. What this paper evaluates (PoC simulation scope).
4. Main contributions as 3-5 bullet points at the end.

Constraints:
- Avoid marketing language.
- Distinguish clearly between simulation evidence and real-world validation.
```

## 3) Methods

```text
Write a Methods section (700-1100 words) from the details below.

Details:
- Simulator type: Monte Carlo episodic simulation
- Configurations compared: {config_list}
- Scenario set: {scenario_list}
- Metrics: interventions_per_1k, critical_rate_pct, mission_success_pct, left_turn_success_pct
- Reproducibility: deterministic seeds, multi-run aggregation
- Commands used: {commands_used}

Requirements:
- Include subsection headers: Study Objective, Experimental Design, Scenario Model, Metrics, Reproducibility.
- Add one paragraph explaining why this is hypothesis-checking, not certification-grade validation.
- Keep language precise and auditable.
```

## 4) Results

```text
Write a Results section (500-900 words) using the numeric inputs.

Inputs:
- Primary comparison table values: {baseline_vs_caros_values}
- Ablation summary values: {ablation_values}
- Variability: {std_or_ci_values}

Instructions:
- Report numbers first, then interpretation.
- Include absolute and relative differences.
- Do not overstate causality.
- Add one short "Key Takeaways" bullet list (3 bullets).
```

## 5) Threats to Validity

```text
Write a Threats to Validity section with these subsections:
- Internal Validity
- Construct Validity
- External Validity
- Statistical Conclusion Validity

Use this context:
{threats_context}

Requirements:
- 2-4 concrete threats per subsection.
- Each subsection must include at least one mitigation.
- Tone: candid and technically rigorous.
```

## 6) Conclusion

```text
Write a Conclusion section (180-280 words).

Include:
- What was demonstrated in this PoC.
- What was not demonstrated.
- Immediate next experiments (CARLA/nuPlan/real logs).
- One-sentence practical implication for architecture design.

Do not introduce new metrics.
```

## 7) Caption Generator (Figures/Tables)

```text
Generate IEEE-style captions.

Inputs:
- Figure/Table type: {figure_or_table}
- Content summary: {what_it_shows}
- Key metric trend: {trend}

Output:
- 3 caption options.
- Each caption max 28 words.
- Neutral tone, no hype.
```

## 8) Reviewer-Style Self-Critique

```text
Act as an IEEE reviewer and critique this draft section:

{paste_section_here}

Return:
1. Major concerns (max 5)
2. Minor concerns (max 8)
3. Missing experiments
4. Specific rewrite suggestions

Be strict, concrete, and technical.
```

## 9) Fast Editing Prompts (Auto-Suggest Workflow)

```text
Shorten this paragraph by 30% without losing technical meaning:
{paragraph}
```

```text
Rewrite this paragraph in formal IEEE tone, remove promotional wording, and keep all numbers unchanged:
{paragraph}
```

```text
Turn these rough bullets into a polished subsection with clear logic and transitions:
{bullets}
```

```text
Check this paragraph for overclaiming and rewrite with appropriately bounded claims:
{paragraph}
```

## 10) Fill-From-CSV Prompt

Use this after generating `results/episode_level_dataset.csv`.

```text
I have a CSV with columns:
configuration, run_id, seed, episode_idx, intervention, critical, mission_success, left_turn_present, left_turn_success

From this CSV, compute:
1. interventions_per_1k by configuration
2. critical_rate_pct by configuration
3. mission_success_pct by configuration
4. left_turn_success_pct by configuration (where left_turn_present=1)
5. 95% confidence intervals by configuration

Then draft a concise IEEE-style Results subsection (250-350 words) with the computed values.
```

---

## Practical Workflow (Minimal Typing)

1. Generate data:
```bash
python3 generate_episode_dataset.py --episodes 10000 --runs 12 --seed 500 --out results/episode_level_dataset.csv
```

2. Start with rough bullets only (not full prose).
3. Use prompts #1-#6 to generate full sections.
4. Use prompt #8 to stress-test your own draft.
5. Use prompt #9 to tighten wording and remove overclaims.
6. Final pass: verify all numbers match CSV/stat outputs.
