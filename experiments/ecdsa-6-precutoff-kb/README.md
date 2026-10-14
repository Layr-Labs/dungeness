# Six-paper pre-cutoff knowledge-organization experiment

## Question

Does organizing knowledge that predates the model cutoff improve research
performance beyond model prior knowledge or access to the same raw papers?

Document-level inclusion in training cannot be observed directly. The
experiment therefore separates two empirical questions:

1. Does the model show closed-book familiarity with source-specific details?
2. Holding model, checkpoint, task, and budget fixed, does structured access
   outperform raw access?

## Arms

| Arm | Knowledge access | Budget |
|---|---|---:|
| baseline | existing `ecdsa-astra-high-no-kb-12usd` | 12 USD |
| raw | six unchanged pre-cutoff PDFs | 12 USD |
| structured | same six PDFs plus mechanism contracts, recipes, cards, and page-level evidence | 12 USD |

The six sources are Litinski, Luongo et al., Gidney, Kornerup et al., Khattar
et al., and Häner et al. Later sources and prior run discoveries are excluded.

## Primary outcomes

- best valid score;
- time and model cost to first valid candidate;
- best score after equal normalized spend;
- number of accepted improvements;
- number and diversity of mechanism families attempted;
- whether a paper-specific mechanism survives in the final implementation;
- premature stopping behavior.

## Training-familiarity probe

Use the same model with no tools or KB. Ask source-specific questions whose
answers are unlikely to follow from titles alone:

- Litinski correction identity and reported counts;
- Luongo MBU preconditions and expected costs;
- Gidney carry identity and workspace points;
- Spooky line-tradeoff relation and ghosting preconditions;
- Khattar explicit/implicit transition distinction and direct division;
- Häner Kaliski normalization, pseudo-inverse correction, and workspace reuse.

Score each paper:

```text
0 = no familiarity or fabricated answer
1 = correct broad topic only
2 = one source-specific mechanism correct
3 = several independent source-specific details correct
4 = correct mechanism, quantitative detail, and limitation
```

A high score is evidence of model familiarity, not proof that the PDF itself
was in training. Knowledge may come from citations, derivative text, or related
sources.

## Interpretation

- structured > raw > baseline: access and organization both help;
- structured > raw approximately baseline: organization retrieves latent
  knowledge better than document reading;
- raw approximately structured > baseline: external content helps, but this
  organization adds little;
- all approximately equal: either model prior dominates or the six-paper
  corpus does not attack the limiting research direction;
- structured explores more mechanisms but scores similarly: organization
  improves research breadth without yet improving objective value.

At least two repetitions per treatment are needed before making a strong
stochastic claim. The first pair is a pilot datapoint.
