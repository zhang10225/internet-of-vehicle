# Feasibility Assessment and Optimization Suggestions

## 1. Executive Summary

**The overall research plan is feasible and well-positioned for the GLOBECOM CISS track.**

The core objective is to couple accountable anonymous authentication with
dual-revocation CP-ABE, leveraging RSU/edge offloading to reduce OBU burden,
targeting IoV business-data dissemination for an IEEE GLOBECOM submission.

This objective is feasible across four dimensions — theoretical, implementation,
timeline, and experimental — though each dimension carries specific risks and
optimization opportunities documented below.

---

## 2. Feasibility Assessment

### 2.1 Theoretical Feasibility: Viable — The Composition Itself Is a Contribution

The proposal does not introduce a new cryptographic primitive. Instead, it
composes existing building blocks into a communication-oriented framework. This
is fully accepted at GLOBECOM CISS, which encourages systems-level security
design over pure cryptographic contributions.

**Building Block Maturity:**

| Building Block | Source | Maturity | Risk |
| --- | --- | --- | --- |
| Conditional privacy authentication (Sign/Verify/Open/Judge) | SE-CPPA style, group signature or pseudonym schemes | High | Interface is clear; verify that the chosen primitive has no known vulnerabilities |
| CP-ABE attribute revocation | Entropy 2023, versioned attributes + proxy update | Medium-High | Confirm compatibility with the chosen CP-ABE scheme |
| User revocation (binary tree + epoch update) | Flexible Revocation / BGW/CS style | High | Update size scales with cover set; verify scale boundary experimentally |
| Transcript binding | Original design, ctx = H(...) | New composition | Field selection adequacy requires security argument |
| RSU outsourced decryption | Entropy 2023 + Green-style outsourced decryption | Medium-High | Must prove RSU cannot recover plaintext |
| Partially hidden policy | TRE-DSP and recent partially hidden CP-ABE literature | Medium | Adds ciphertext expansion and decryption overhead |

**Key Theoretical Risks:**

- The transcript binding security argument needs a formal definition. The
  current design `ctx = H(m_hdr || tau || sigma || sid || e_u)` is reasonable,
  but the paper must clearly state what attacks it prevents (mix-and-match
  replay, transcript substitution) and what it does not prevent (credential
  theft, which is the authentication layer's responsibility).
- The combined security of dual revocation cannot simply be stated as "each
  revocation mechanism is individually secure, therefore their combination is
  secure." The paper must address whether interactive attack surfaces exist
  between the two mechanisms (e.g., a user-revoked but attribute-unrevoked node
  exploiting residual attribute material).

### 2.2 Implementation Feasibility: Viable — But Tool-Chain Decisions Must Be Made Early

**Cryptographic Prototype Layer:**

- Charm-Crypto works on Ubuntu 22.04 but its maintenance activity has declined.
  If compilation fails, PBC + hand-written Python bindings or direct C
  implementation is a viable fallback.
- OpenABE is more stable but less flexible for custom revocation logic.
  Recommendation: **use Charm for functional validation, PBC/C or JPBC for
  final timing measurements.**
- The three-layer environment split (cryptographic / network simulation /
  legacy compatibility) is sound, but the legacy layer (BCPPA) should be
  deprioritized further as it contributes minimally to the paper.

**Network Simulation Layer:**

- OMNeT++ 6 + SUMO + Veins 5.2/5.3 is feasible on Ubuntu 22.04 with adequate
  community support.
- Injecting cryptographic delays into the application layer is standard
  practice, but the injected delays should include serialization/deserialization
  overhead, not just raw computation time.

### 2.3 Timeline Feasibility: Depends on Target Venue

| Target | Approximate Deadline | Current Distance | Risk Assessment |
| --- | --- | --- | --- |
| GLOBECOM 2025 | Already passed or imminent | Very tight | Not recommended unless significant code already exists |
| GLOBECOM 2026 | Approximately April–May 2026 | ~1–2 months | Tight but feasible if coding starts immediately |
| Other IEEE venues/journals | Per specific CFP | Flexible | ICC or TVT/TIFS are alternatives if GLOBECOM 2026 is missed |

**Critical Path:** The project is currently in the document-planning phase with
no code written. For GLOBECOM 2026, the core cryptographic micro-benchmarks
(encrypt/decrypt/revoke) must be completed within 4–6 weeks, or downstream
writing and simulation time will be critically compressed.

### 2.4 Experimental Feasibility: Viable — But Needs Scope Reduction

The experimental plan (Sections V–VI draft) is comprehensive: micro-benchmarks +
network simulation + ablation + three main figures. This is a "full
configuration" plan.

**Points Requiring Attention:**

- Six baselines are too many for a 6-page conference paper. Recommend keeping
  3–4 in the main text and mentioning the rest in related work only.
- Five ablation variants are also excessive. Recommend keeping the 3 most
  discriminating ones in the main text.
- The 500-vehicle + 16-RSU simulation scale is reasonable but time-consuming to
  set up. If time is tight, start with 50–200 vehicles and prioritize
  interpretable results.

---

## 3. Optimization Suggestions

### 3.1 Protocol Design

#### Suggestion 1: Define Transcript Binding Security Goals Explicitly

Add a "Transcript Binding Security Goal" paragraph that states:

- **Attacks prevented:** An attacker with a valid sigma cannot pair it with an
  unrelated ABE ciphertext (mix-and-match attack).
- **Attacks not prevented:** Full credential compromise falls to the
  authentication layer's security.
- **Interaction with revocation:** Embedding `e_u` in ctx means cross-epoch
  replay is detectable, but same-epoch transcript reuse semantics should be
  documented.

#### Suggestion 2: Consider Deferring Partially Hidden Policy to Future Work

Combining dual revocation + anonymous authentication + outsourced decryption +
policy hiding risks spreading the contribution too thin for a 6-page paper.
If time is tight, present partially hidden policy as future work to let the
three core contributions stand out more clearly.

#### Suggestion 3: Strengthen the TA/TrA Separation Justification

Reviewers may ask why TA, TrA, and AA/RM are separate entities. Add one
sentence: "TA cannot unilaterally decrypt data, TrA cannot unilaterally trace
users, and AA/RM cannot participate in the accountability process." Back this
up in the security analysis with a concrete attack scenario (e.g., insider
abuse).

### 3.2 Experimental Design

#### Suggestion 4: Build a Unified Benchmark Harness First

Before writing the first line of protocol code, establish a benchmark harness:

- Unified timing (median of 30 runs + 95% CI);
- Unified parameter configuration file;
- Unified output format (CSV or JSON) for direct plot generation.

This harness survives library changes (e.g., switching from Charm to PBC/C).

#### Suggestion 5: Reduce Main-Text Baselines to Four

| Retained Baseline | Role | Reason |
| --- | --- | --- |
| SE-CPPA [2] | Authentication baseline | Directly comparable on anonymous auth |
| Entropy 2023 [4] | Attribute revocation + outsourced decryption baseline | Directly comparable on ABE submodule |
| TRE-DSP [6] | Closest comprehensive baseline | Only one covering tracing + revocation + data sharing |
| Flexible Revocation [5] | User revocation baseline | Compares the user-revocation half of dual revocation |

BCPPA [1] and Dynamic FGAC [3] can be cited in related work without
experimental comparison in the main text.

#### Suggestion 6: Specify the SUMO Scenario Early

Decide now whether to use a standard SUMO scenario (e.g., TAPASCologne or a
custom grid) and document the traffic-flow model (random trips vs. OD matrix)
and business-data generation rate (messages per vehicle per second).

#### Suggestion 7: Reduce Ablation Variants to Three

Retain the three most discriminating ablations in the main text:

| Variant | Removed Capability | Selection Reason |
| --- | --- | --- |
| No outsourced decryption | Full OBU-side decryption | Directly shows RSU offloading value |
| No user revocation | Remove epoch updates | Shows necessity of user-level revocation in dual scheme |
| No transcript binding | Remove ctx check | Shows security benefit of auth-authorization coupling |

"No attribute revocation" and "no accountability" can be summarized in one
sentence each without dedicated figures.

### 3.3 Environment and Tool-Chain

#### Suggestion 8: Containerize the Cryptographic Prototype Environment

Add a Dockerfile (or docker-compose.yml) for the cryptographic prototype
environment. Benefits:

- Anyone can `docker compose up` for a reproducible environment;
- Switching machines requires no reconfiguration;
- The paper can claim containerized reproducibility.

#### Suggestion 9: Prepare a Charm-Crypto Fallback Path

If `pip install charm-crypto-framework` fails on Ubuntu 22.04 (OpenSSL
version sensitivity is common), do not spend more than one day debugging. Switch
to `pypbc` (Python PBC bindings) or write core primitives in C with PBC and
use Python only as a driver.

### 3.4 Paper Writing

#### Suggestion 10: Verify the TRE-DSP Citation

The literature guide notes that TRE-DSP did not pass stable verification. If
the full text cannot be confirmed, either verify it before submission or replace
it with another confirmed 2023–2024 IoV data-sharing paper. Citing a paper
without having read its full text carries reviewer risk.

#### Suggestion 11: Include a Minimal Formal Security Model

The current security bridge paragraph (Section V-I) lists security goals but
lacks a formal threat model. For a 6-page paper, a full proof is unnecessary,
but the paper should at least:

- Define which entities are honest, honest-but-curious, or malicious;
- Give a one-sentence proof sketch for each goal;
- Explicitly state collusion scenarios (e.g., a user-revoked OBU colluding
  with a policy-unsatisfied OBU).

#### Suggestion 12: Frame the Title and Abstract Around "Composition Framework"

The contribution is compositional, not primitive-level. The title and abstract
should emphasize:

- "edge-assisted" (venue fit);
- "accountable anonymous authentication + dual-revocation access control"
  (core contribution);
- "IoV business-data dissemination" (application scenario).

Avoid cryptographic jargon (IND-CPA, LSSS) in the title, as GLOBECOM
reviewers lean more systems than pure crypto.

### 3.5 Research Roadmap

#### Suggestion 13: Shift from "Paper-by-Paper Reproduction" to "Framework-First"

Instead of reproducing papers sequentially, build your own framework
incrementally:

1. **Week 1:** Benchmark harness + Entropy 2023 minimal loop
   (Setup/KeyGen/Encrypt/Decrypt);
2. **Week 2:** Add AttrRevoke and RSUTransform; implement SE-CPPA
   Sign/Verify in the same framework;
3. **Week 3:** Add user revocation module (from Flexible Revocation
   mechanism); form "dual revocation" prototype;
4. **Week 4:** Complete all micro-benchmarks, generate plots;
5. **Weeks 5–6:** Network simulation + paper writing.

#### Suggestion 14: Do Not Attempt to Run the BCPPA Repository

Read the BCPPA repository for structural insights only. Do not invest time in
building its legacy environment. If BCPPA performance data is needed for the
paper, cite the original paper's reported values and note the source.

---

## 4. Risks and Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Charm-Crypto fails to compile on Ubuntu 22.04 | Blocks prototype development | Prepare PBC/C fallback or use Ubuntu 20.04 Docker image |
| Dual-revocation security argument is insufficient | Reviewer rejection on security | Write collusion-scenario analysis early; provide at least intuitive arguments |
| Veins/SUMO simulation debugging takes too long | Insufficient time for network experiments | Prioritize complete micro-benchmarks; replace network simulation with analytical model if needed |
| Paper exceeds 6 pages | Format non-compliance | Keep only 3 figures + 1 table in main text; move extras to arXiv version |
| TRE-DSP citation cannot be confirmed | Inaccurate related work | Either fully verify or replace with another confirmed paper |

---

## 5. Specific Document Corrections

### 5.1 Environment Manual

- Section 5: The Charm PyPI package name `charm-crypto-framework` should be
  verified — the official name has changed historically and may need to be
  `charm-crypto` or source-installed.
- Section 9: The `opp_env install omnetpp-6.3.0` version should be noted as
  "current stable at time of writing" to prevent the document from becoming
  stale.

### 5.2 Related Work Matrix

- Add a "本文方案 / Our Scheme" row as the last row in the matrix so readers
  can instantly see the comparison against all baselines.
- Consider adding an "IoV-Specific" column to quickly distinguish IoV-native
  schemes from general ABE mechanisms.

### 5.3 Protocol Draft (Sections V–VI)

- Section V-B notation table: Add `C_dem` (symmetric ciphertext) and `C`
  (final dissemination object), which are used in the text but not defined in
  the table.
- Section V-E: Explain why `aad` does not include `sid` and `e_u` (they are
  already bound through `ctx` and do not need to be redundantly bound at the
  AEAD layer).
- Section VI-E: The upper bounds of 50 attributes and 40 policy rows may cause
  excessively long per-run times. If runs above 30 attributes become
  impractical, reduce the upper bound.

### 5.4 First-Round Task Sheet

- Section 5.2 describes a three-layer implementation framework
  (auth / access-control / integration). Consider creating the corresponding
  directory structure in the repository (e.g., `src/auth/`, `src/abe/`,
  `src/integration/`) with placeholder files to formalize the code
  organization.

---

## 6. Summary

| Dimension | Verdict | Confidence |
| --- | --- | --- |
| Theoretical feasibility | ✅ Viable — mature building blocks, sound composition | High |
| Implementation feasibility | ✅ Viable — toolchain available but needs fallback plan | Medium-High |
| Timeline feasibility | ⚠️ Depends on target deadline; must begin coding immediately | Medium |
| Experimental feasibility | ✅ Viable — but reduce scope on baselines and ablations | Medium-High |
| Venue positioning | ✅ Strong GLOBECOM CISS fit; clear compositional contribution | High |

**One-sentence summary:** The plan is feasible and well-directed. The most
important next step is not further document refinement but immediate entry into
the coding phase — build the unified benchmark harness first, then close the
Entropy 2023 minimal loop.
