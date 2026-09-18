# D6 Final Cost Summary — LIANG LUWEN

- Selected baseline: `openai/gpt-5.6-luna` v2
- Measured trial success: 35/59 = 59.32%
- Layer 1 variable cost: US$0.003481/task
- Layer 2 expected fallback: US$3.091525/task
- Cost-to-serve: US$3.095006/task
- Layer 3: US$0.00/month (prototype-scope assumption)
- Monthly cost at 8,000 claims: US$24,760.05
- Sensitivity (-10pp / measured / +10pp): US$3.8550 / US$3.0950 / US$2.3350
- Gemini v2 break-even success rate vs Luna: 59.30%; measured Gemini v2 = 28.81%
- Deployment caps: 8 steps/run; US$0.05/run; 200 runs/user/month (implied US$10.00/user/month ceiling)

## Cost-lever evidence

| lever            | status                         |      before |      after | unit                                     | measured_effect                                                                                       | evidence_type                                  |
|:-----------------|:-------------------------------|------------:|-----------:|:-----------------------------------------|:------------------------------------------------------------------------------------------------------|:-----------------------------------------------|
| tool_block_size  | READY_WITH_RECONSTRUCTION_NOTE | 1049        | 841        | cl100k_base proxy tokens                 | -208 tokens (19.8% reduction)                                                                         | analytical D2(a) baseline → actual final block |
| turn_count       | READY_WITH_SCOPE_NOTE          |    6.34146  |   4.09756  | average turns/case                       | proxy input tokens 12240.7 → 7744.4; code pass rate 87.8% → 100.0%; strict-sequential step-cap hits 5 | controlled scripted D2(c) replay               |
| observation_size | READY_WITH_COMMIT_NOTE         |  442.034    | 475.746    | avg cl100k_base observation tokens/trial | total tokens 26080 → 28069                                                                            | retained Gemini live v1/v2 traces              |
| success_rate     | READY_WITH_COMMIT_NOTE         |    0.169492 |   0.288136 | trial pass rate                          | +11.86 percentage points                                                                              | retained Gemini live v1/v2 results             |

## Disclosed limitations

1. D2(a) has no historical pre-consolidation implementation; its before value is an analytical baseline constructed from the documented design responsibilities.
2. D2(c) turn-count evidence is a controlled scripted replay, not a second live-model battery.
3. The retained Gemini v1 control uses commit `57a21e6` while final v2 uses `74072ad`.
