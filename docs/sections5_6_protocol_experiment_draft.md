# Sections V-VI Draft for an IEEE GLOBECOM IoV Security Paper

## How to Use This Draft

This file is written in a GLOBECOM-friendly style: concise, systems-oriented,
and centered on deployment impact. If the final paper keeps a standalone
"Security Analysis" section before the experiments, renumber Section VI below
to Section VII and move the short security bridge paragraph accordingly.

# V. Edge-Assisted Accountable Dual-Revocation Access Control Protocol

## A. Design Rationale

We consider privacy-preserving dissemination of IoV business data, such as
incident reports, diagnostic traces, roadside sensing summaries, and
task-oriented coordination records. Unlike high-frequency safety beacons, these
messages are not uniformly public. They require sender authentication, receiver
authorization, revocation support, and post-incident accountability. Existing
vehicular authentication schemes and ABE-based access-control schemes solve
these requirements only partially and often in isolation. To bridge this gap,
we design an edge-assisted protocol that couples accountable anonymous
authentication with dual-revocation CP-ABE.

The protocol is guided by three principles. First, public verifiers should be
able to validate message legitimacy without learning the sender's real identity.
Second, encrypted business data should be accessible only to receivers whose
attributes satisfy the sender's policy under current revocation status. Third,
the OBU should avoid expensive pairing-heavy operations whenever they can be
offloaded to trusted roadside or edge infrastructure.

## B. System Entities and Notation

The system contains a trusted authority (TA), a tracing authority (TrA), an
attribute authority and revocation manager (AA/RM), roadside units acting as
edge proxies (RSUs), a cloud or service platform (CSP), vehicle OBUs with
tamper-protected devices (TPDs), and authorized data consumers. The TA and TrA
jointly support conditional privacy and verifiable tracing; the AA/RM issues
attribute keys and revocation updates; the RSU performs batch verification and
outsourced decryption.

| Symbol | Meaning |
| --- | --- |
| `ID_i` | Real identity of vehicle `V_i` |
| `PID_i^tau` | Slot-bound pseudonymous authentication handle for time slot `tau` |
| `A_i` | Attribute set of vehicle or requester `i` |
| `T` | Access tree or equivalent LSSS policy |
| `e_u` | User-revocation epoch |
| `ver(a)` | Current version of attribute `a` |
| `KU_t` | Epoch update material for non-revoked users at time `t` |
| `AU_{a,t}` | Attribute-version update token for attribute `a` at time `t` |
| `TK_i` | Transformation key used by the RSU for outsourced decryption |
| `sigma` | Anonymous accountable authentication tag / signature |
| `ctx` | Authentication transcript hash bound to the ciphertext |

## C. Setup and Enrollment

During system setup, the TA initializes the anonymous authentication subsystem
and distributes opening material between the TA and TrA. The AA/RM initializes
the CP-ABE public parameters, the user-revocation tree, and the attribute
version table. Each vehicle is enrolled once and obtains:

1. a long-term identity record bound to its TPD,
2. anonymous authentication credentials supporting `Sign`, `Verify`, `Open`,
   and `Judge`,
3. an attribute secret key for its initial attribute set,
4. a path-dependent revocation secret associated with the binary revocation
   tree, and
5. a transformation key derivation handle for RSU-assisted decryption.

The TA and AA/RM are logically separated to avoid a single authority that can
both trace users and decrypt protected data.

## D. Anonymous Authentication and Transcript Binding

When vehicle `V_s` sends a business-data message to an RSU or service platform,
it first authenticates the message anonymously. Let `m_hdr` denote the public
header, including the service type, coarse region tag, and current time slot
`tau`. The sender generates

`sigma <- Sign(cred_s, m_hdr, tau)`.

Any verifier can run `Verify(pp_auth, m_hdr, tau, sigma)` to confirm that the
message comes from a legitimate but hidden sender. To bind authentication and
authorization, the sender computes

`ctx = H(m_hdr || tau || sigma || sid || e_u)`,

where `sid` is a dissemination session identifier. The value `ctx` is then
embedded into the ABE ciphertext as an immutable binding tag. This design
prevents attackers from reusing an old anonymous authentication transcript to
wrap a new protected payload under a different policy.

If a dispute occurs, the TA and TrA jointly execute `Open` to recover the
responsible long-term identity and issue a signed tracing statement. A public
`Judge` procedure validates that the recovered identity is consistent with
`(m_hdr, tau, sigma)` and that the tracing authority did not forge the result.
This realizes anonymous but accountable dissemination.

## E. Policy-Protected Data Dissemination

After generating the authenticated header, the sender samples a symmetric
session key `K` and encrypts the payload `M` with an authenticated symmetric
primitive:

`C_dem = AEAD.Enc(K, M, aad = m_hdr || tau || sigma)`.

The sender then defines a partially hidden access policy. The visible part may
expose only coarse service semantics, while sensitive policy leaves remain
opaque. A representative policy is

`T = ((Role AND Region AND Task) OR Emergency) AND Freshness`.

The sender uses CP-ABE to encrypt `(K, ctx, meta)` under policy `T`, where
`meta` includes the current user-revocation epoch `e_u` and the current
attribute versions `ver(a)` for the attributes appearing in the policy. The
final dissemination object is

`C = {m_hdr, tau, sigma, C_dem, CT_abe}`.

Thus, public verification is lightweight, while access to the protected content
is granted only to requesters whose current attributes satisfy the policy.

## F. Edge-Assisted Outsourced Decryption

To reduce OBU delay, each authorized receiver derives a lightweight
transformation key `TK_i` and submits only the minimum verification material to
the serving RSU. Upon receiving `C`, the RSU first verifies `sigma` locally or
in batch form. If the message is valid, the RSU executes

`CT'_i <- Transform(TK_i, CT_abe)`.

The transformed ciphertext leaks no useful plaintext information to the RSU but
removes most pairing-heavy work from the OBU. The receiver then performs a
small final step:

`(K, ctx') <- FinalDec(sk_i, CT'_i)`.

The OBU accepts the output only if `ctx' = H(m_hdr || tau || sigma || sid || e_u)`.
This final consistency check is essential. Even if a malicious relay replays
old ciphertext components or mixes a valid authentication transcript with a new
ABE wrapper, the transcript-binding check causes final decryption to fail.

## G. Dual Revocation Mechanism

### 1) User Revocation

User revocation is managed by epochs over a binary tree. Each enrolled user is
assigned a leaf and stores secret material associated with the nodes on the
root-to-leaf path. At epoch `t`, the AA/RM publishes `KU_t` for the cover set
of all non-revoked users. A legitimate receiver combines its path secret with
`KU_t` to derive the current decryption capability. A revoked user cannot
reconstruct the required epoch key even if it retains old attribute material.

This mechanism gives efficient user revocation because the update size grows
with the cover set rather than linearly with the total number of users. It also
provides a clean metric for evaluation: update size and update application time
under varying revocation densities.

### 2) Attribute Revocation

Each attribute `a` maintains a version number `ver(a)`. When `a` is revoked
from a user or reissued under new conditions, the AA/RM increments `ver(a)` and
generates fresh update tokens `AU_{a,t}` for all non-revoked holders of that
attribute. The sender always encrypts against the current version metadata.
Existing ciphertexts can be refreshed lazily by the CSP or RSU using proxy
update material, which avoids immediate full reencryption by the original
sender.

This design separates coarse identity invalidation from fine-grained privilege
removal. A vehicle may remain a valid network participant while losing a single
role attribute such as `Maintenance`, `Law-Enforcement`, or `Fleet-Coordinator`.
That distinction is important in IoV deployments where service privileges change
more frequently than enrollment status.

## H. Accountable Tracing Procedure

The accountable tracing workflow is executed only on demand. After receiving a
complaint or identifying a malicious dissemination event, the TA and TrA
jointly run `Open(m_hdr, tau, sigma)` and recover `ID_s`. They then issue a
trace record

`TR = {m_hdr, tau, sigma, ID_s, pi_open, sig_TA, sig_TrA}`.

Here, `pi_open` is a verification object showing that the opening operation is
consistent with the anonymous authentication system, while `sig_TA` and
`sig_TrA` attest that tracing required joint authorization. Any auditor can run
`Judge(TR)` to confirm that the tracing result is valid and non-forged. This
prevents abuse of tracing power and turns conditional privacy into verifiable
accountability rather than opaque authority trust.

## I. Security Bridge Paragraph

The security goals of the protocol follow directly from its composition:
unforgeability of anonymous authentication, sender anonymity against public
observers, accountability under joint opening, confidentiality of business data
under policy-compliant access, resistance to collusion among users with stale
or partially revoked keys, and correctness of outsourced decryption. In the
paper, these claims can be formalized by combining the security of the
accountable anonymous authentication layer with the IND-CPA or IND-sAtt-CPA
style guarantees of the partially hidden CP-ABE layer under transcript binding.

# VI. Experimental Methodology and Evaluation Plan

## A. Evaluation Goal

The evaluation should answer one systems question rather than several unrelated
cryptographic questions: does the proposed composition reduce OBU-side
processing while preserving accountable privacy and low end-to-end dissemination
latency for protected IoV business data? To answer this clearly within the
GLOBECOM page budget, the experiments should combine micro-benchmarks with
network-level simulation.

## B. Prototype Stack

We recommend a two-layer prototype.

1. **Cryptographic prototype.**
   Implement the protocol primitives in a unified framework. `Charm` or
   `OpenABE` can be used to validate policy handling and functional correctness.
   `JPBC` or `PBC/C` should then be used for final timing measurements because
   the evaluation needs explicit pairing and exponentiation costs.

2. **Network simulation.**
   Use `Veins + OMNeT++ + SUMO` to model the dissemination network. The
   cryptographic delays measured in the prototype are injected as application
   processing delays for sender OBUs, receiving OBUs, and RSUs.

This split keeps the paper reproducible and avoids the common mistake of
claiming end-to-end network performance without measuring the underlying
cryptographic cost.

## C. Baselines

The baselines should mirror the related-work matrix and each one should answer
a specific comparison question.

| Baseline | Role in Evaluation | Reused Metrics |
| --- | --- | --- |
| BCPPA [1] | Authentication-only privacy baseline | Sign/verify delay, communication overhead |
| SE-CPPA [2] | Lightweight anonymous authentication baseline | Batch verification gain, authentication latency |
| Dynamic FGAC [3] | Access-control and user-revocation baseline | Authorization delay, update cost |
| Lightweight direct-AR CP-ABE [4] | Attribute-revocation and RSU-offload baseline | OBU final decryption delay, RSU transform cost |
| Flexible Revocation ABE [5] | Foundational user-revocation mechanism baseline | Update size, epoch rekey delay |
| TRE-DSP [6] | Closest IoV data-sharing baseline | Trace latency, ciphertext cost, revocation-aware dissemination |

All baselines should be reimplemented or normalized under a unified security
level. Published values may be reported only as secondary references, not as
the main fairness basis.

## D. Metrics

The core metrics should be limited to the following set.

| Category | Metric | Meaning |
| --- | --- | --- |
| OBU cost | Signing delay | Time to produce the anonymous authentication tag |
| OBU cost | Final decryption delay | Residual client-side decryption after RSU transform |
| RSU cost | Transform cost | Edge-side outsourced decryption overhead |
| Accountability | Trace latency | Time from trace request to validated `Judge` result |
| Revocation | User update size | Size of `KU_t` under varying revoked-user counts |
| Revocation | Attribute update cost | Size and application delay of `AU_{a,t}` |
| Network | End-to-end delivery delay | Delay from sender generation to authorized receiver recovery |
| Network | PDR / throughput | Delivery effectiveness under traffic load |
| Network | Communication overhead | Bytes added by authentication and ABE metadata |

These metrics directly support the paper's thesis: low OBU burden, revocation
efficiency, and deployable privacy-preserving dissemination.

## E. Parameter Settings

The experiments should scan the following parameter ranges.

| Parameter | Values |
| --- | --- |
| Number of attributes in user key | 5, 10, 20, 30, 50 |
| Number of policy rows / leaves | 5, 10, 20, 40 |
| Revoked users per epoch | 1, 10, 50, 100 |
| Revoked attributes per update | 1, 5, 10 |
| Number of vehicles | 50, 100, 200, 500 |
| Number of RSUs | 4, 8, 16 |
| Business-data payload size | 200, 500, 1000 bytes |

All schemes should first be normalized to roughly 128-bit security. If an older
baseline relies on outdated pairing parameters, one additional "original
parameter" reproduction curve may be shown to explain discrepancies with the
normalized results.

## F. Micro-Benchmark Procedure

For each configuration, measure:

1. sender-side signing time,
2. sender-side ABE encryption time,
3. RSU-side verification and transform time,
4. receiver-side final decryption time,
5. user-revocation update generation and application time,
6. attribute-revocation update generation and lazy-refresh time, and
7. opening and judging time under dispute.

Each data point should be averaged over at least 30 runs and reported with a
95% confidence interval. The same machine, curve family, compiler or JVM
configuration, and library version must be used across all schemes.

## G. Network-Level Simulation

The network-level study should focus on protected business-data dissemination
rather than periodic safety beacons. A practical setup is a mixed urban grid
scenario in SUMO with 50 to 500 vehicles and 4 to 16 RSUs. Vehicles generate
business-data packets at moderate rates, and only receivers satisfying the
current policy can recover the payload. The simulation injects the measured
cryptographic delays into the application layer and then reports:

- end-to-end delivery delay,
- packet delivery ratio,
- effective throughput for authorized receivers, and
- additional delay introduced by tracing or revocation refresh events.

This setup matches the intended contribution far better than applying CP-ABE to
10 Hz safety beacons, which would create an artificial real-time bottleneck and
invite unnecessary reviewer criticism.

## H. Ablation Studies

Five ablations are sufficient and directly aligned with the contribution claims.

| Variant | Removed Capability | Expected Outcome |
| --- | --- | --- |
| No user revocation | Remove epoch-based binary-tree update | Lower update cost but stale users remain decrypt-capable |
| No attribute revocation | Remove versioned attribute updates | Lower maintenance cost but no fine-grained privilege removal |
| No outsourced decryption | Force full OBU-side ABE decryption | Higher OBU delay and lower scalability |
| No accountability | Replace `Open/Judge` with opaque tracing | Slightly lower control overhead but weaker trust in tracing |
| No transcript binding | Remove `ctx` consistency check | Similar raw cost but weaker protection against mix-and-match replay |

These ablations help reviewers see that each component contributes a distinct
system-level benefit.

## I. Three Main Figures for a 6-Page Paper

To stay within the GLOBECOM format, keep only three main experimental figures.

1. **Figure 1:** OBU and RSU cryptographic delay versus number of attributes.
   Plot sender signing, RSU transform, and OBU final decryption together.
2. **Figure 2:** Revocation overhead versus number of revoked users or revoked
   attributes. One subfigure for `KU_t`, one for `AU_{a,t}`.
3. **Figure 3:** End-to-end delivery delay and PDR versus number of vehicles.
   This is the main networking result that justifies venue fit.

Any extra micro-benchmark tables can be moved to supplementary material or a
workshop extension.

## J. Result Claims to Make in the Paper

The final discussion should make only the following claims unless stronger data
is obtained:

1. the proposed design preserves anonymous authentication while adding
   verifiable accountability;
2. the dual-revocation mechanism removes both revoked users and revoked
   privileges from the authorized set;
3. RSU-assisted outsourced decryption shifts the dominant pairing cost away
   from resource-constrained OBUs; and
4. under realistic IoV business-data workloads, the resulting end-to-end delay
   remains suitable for low-latency protected dissemination.

This wording is strong enough for GLOBECOM while remaining defensible.

## Draft References

[1] M. A. Ferrag, O. Friha, L. Shu, and X. Yang, "BCPPA: A Blockchain-Based
Conditional Privacy-Preserving Authentication Protocol for Vehicular Ad Hoc
Networks," *IEEE Transactions on Intelligent Transportation Systems*, 2020.
DOI: https://doi.org/10.1109/TITS.2020.3002096

[2] "SE-CPPA: A Secure and Efficient Conditional Privacy-Preserving
Authentication Scheme in Vehicular Ad-Hoc Networks," *Sensors*, 2021.
URL: https://www.mdpi.com/1424-8220/21/24/8206

[3] "Dynamic fine-grained access control scheme for vehicular ad hoc networks,"
*Computer Networks*, 2021. DOI: https://doi.org/10.1016/j.comnet.2021.107872

[4] "A Lightweight CP-ABE Scheme with Direct Attribute Revocation for Vehicular
Ad Hoc Network," *Entropy*, 2023. DOI: https://doi.org/10.3390/e25070979

[5] "Attribute-based encryption with Flexible Revocation," *Procedia Computer
Science*, 2023. DOI: https://doi.org/10.1016/j.procs.2023.09.020

[6] "TRE-DSP: A traceable and revocable encryption and data sharing protocol
with partially hidden access policy for Internet of Vehicles,"
*Vehicular Communications*, 2024. DOI: https://doi.org/10.1016/j.vehcom.2024.100746
