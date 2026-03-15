# GLOBECOM-Style Related Work Matrix for Privacy-Preserving IoV Data Dissemination

## Purpose

This note is a drafting aid for an IEEE GLOBECOM submission targeting the
Communications and Information Systems Security (CISS) symposium. The matrix is
not an exhaustive survey. Instead, it selects papers that help us build a
focused story around three core contributions:

1. accountable anonymous authentication for IoV message dissemination,
2. dual revocation for fine-grained data access control, and
3. RSU/edge-assisted lightweight processing for on-board units (OBUs).

Two citation corrections from the earlier planning stage are reflected here:

- The verified DOI for `TRE-DSP` is `10.1016/j.vehcom.2024.100746`.
- DOI `10.1016/j.procs.2023.09.020` corresponds to a general ABE revocation
  paper rather than an IoV-specific scheme. It is still useful as a revocation
  mechanism reference, but it should not be presented as an IoV baseline.

## Venue Fit Notes

- The GLOBECOM CISS symposium explicitly covers authentication, access control,
  privacy, and lightweight cryptography, so the paper should be framed as a
  communications-security systems paper rather than a pure cryptography paper
  [G1].
- The draft should stay compact and figure-driven. Recent GLOBECOM calls and
  author pages favor a concise conference presentation style, so the related
  work section should do gap positioning rather than a long taxonomy [G2], [G3].

## Selected Related Work Matrix

| ID | Paper | Main Focus | Anonymous Auth. | Traceability / Accountability | User Revocation | Attribute Revocation | Policy Hiding | Edge / Proxy Offload | Experimental Style | How We Use It | Key Limitation vs. Our Target |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [1] | BCPPA | Blockchain-assisted conditional privacy-preserving VANET authentication | Yes | Conditional privacy with opening authority | No | No | No | Limited | Crypto cost + network-level discussion | Authentication-line baseline | No fine-grained data access control; no dual revocation |
| [2] | SE-CPPA | Lightweight conditional privacy-preserving authentication in VANETs | Yes | Yes, through authority-assisted identity recovery | No | No | No | Batch verification support | Detailed signing / verification measurements | Main lightweight authentication baseline | Stops at authentication; does not protect business data with ABE |
| [3] | Dynamic fine-grained access control scheme for VANETs | Access control and dynamic authorization | No | Weak / indirect | Yes | Not explicit | No | Service-assisted | Access-control latency and communication overhead | User-revocation access-control baseline | Lacks anonymous authentication and accountable opening |
| [4] | A Lightweight CP-ABE Scheme with Direct Attribute Revocation for Vehicular Ad Hoc Network | CP-ABE for VANET with direct attribute revocation | No | No | Indirect / limited | Yes | No | Yes, RSU-assisted two-stage decryption | Pairing-cost evaluation with OBU/RSU split | Attribute-revocation baseline | No accountable anonymous authentication; no explicit user revocation |
| [5] | Attribute-based Encryption with Flexible Revocation | General ABE revocation mechanism | No | No | Yes | Mechanism-level support via updates | No | Possible with extension | Cryptographic micro-benchmarks | Foundational revocation primitive reference | Not IoV-specific; does not solve vehicular authentication or traceability |
| [6] | TRE-DSP | Traceable and revocable CP-ABE data sharing for IoV with partially hidden policy | No | Traceability at data-sharing layer | Yes | Limited / not full dual revocation | Partially | Yes | Cryptographic cost + data-sharing workflow | Closest data-sharing baseline | Does not close the gap between anonymous network authentication and ABE-protected dissemination |

## Ready-to-Use Synthesis for the Related Work Section

### A. Conditional Privacy-Preserving Authentication

Conditional privacy-preserving authentication remains the dominant design
pattern for VANET and IoV trust establishment. Representative schemes such as
BCPPA [1] and SE-CPPA [2] allow vehicles to authenticate safety-related
messages while hiding long-term identities from the public. These designs are
well aligned with the networking constraints of vehicular systems because they
optimize signing, verification, and sometimes batch verification. However, they
mainly solve link-layer or application-message authentication. They do not
provide fine-grained authorization for sensitive business data, nor do they
offer user-level or attribute-level revocation for encrypted content.

### B. Fine-Grained Access Control and Revocation

A second line of work introduces ABE into vehicular or edge-assisted data
sharing. Dynamic access-control frameworks for VANETs, such as [3], show that
attribute-based authorization is a natural way to regulate who can access
vehicular data under changing service conditions. Subsequent works strengthen
this direction by addressing revocation and lightweight processing. The scheme
in [4] integrates direct attribute revocation with RSU-assisted decryption to
reduce OBU burden. The flexible-revocation mechanism in [5] offers a useful
cryptographic foundation for user revocation through update material and time
evolution. More recently, TRE-DSP [6] combines traceability, revocation, and
partially hidden policies for IoV data sharing. Nevertheless, this line still
treats access control and vehicular authentication largely as separate layers.

### C. Gap Positioning

The central gap for a GLOBECOM-oriented paper is therefore not the absence of
either anonymous authentication or revocable ABE in isolation. The real gap is
the lack of a tightly integrated dissemination framework that:

1. authenticates IoV senders anonymously but preserves verifiable
   accountability,
2. enforces fine-grained access over business data rather than only over public
   safety beacons,
3. supports both user revocation and attribute revocation in one workflow, and
4. keeps OBU-side delay low by shifting heavy computation to RSU/edge nodes.

This is the positioning that should be emphasized in the paper. The novelty is
not a brand-new primitive, but a communication-oriented composition that closes
the operational gap between privacy-preserving authentication and deployable
data-plane access control.

## Baseline Mapping for Our Evaluation

| Evaluation Axis | Recommended Baseline(s) | Why |
| --- | --- | --- |
| OBU signing / verification delay | [1], [2] | Best-known authentication-focused baselines |
| Batch verification gain | [2] | Practical conditional-privacy authentication baseline |
| Access-control latency | [3], [4] | Directly relevant to vehicular data authorization |
| Attribute revocation cost | [4] | Closest vehicular attribute-revocation reference |
| User revocation update size / delay | [3], [5] | One vehicular access-control baseline plus one foundational revocation mechanism |
| Trace latency | [1], [2], [6] | Covers accountability in authentication and data sharing |
| Edge offloading gain | [4], [6] | Closest RSU/proxy-assisted designs |

## Writing Guidance for the Final Paper

- Put [1] and [2] in one short paragraph under "authentication-oriented
  privacy-preserving vehicular security".
- Put [3], [4], and [5] in one short paragraph under "ABE-based data access
  control and revocation".
- Use [6] alone to motivate why the closest existing IoV data-sharing solution
  still does not fully integrate accountable anonymous authentication with dual
  revocation.
- End the section with a one-sentence contribution contrast:
  "Unlike prior works that optimize either anonymous authentication or
  revocable access control, our design binds accountable anonymous
  authentication transcripts to edge-assisted dual-revocation CP-ABE
  ciphertexts for low-latency IoV business-data dissemination."

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

[G1] IEEE GLOBECOM 2025 CISS Symposium Page:
https://globecom2025.ieee-globecom.org/program/symposia/communications-and-information-systems-security-symposium

[G2] IEEE GLOBECOM 2025 Call for Symposium Papers:
https://globecom2025.ieee-globecom.org/call-symposium-papers

[G3] IEEE GLOBECOM 2026 CFP (IEEE China page):
https://cn.ieee.org/2026/01/27/call-for-paper-ieee-globecom-2026%E8%AE%BA%E6%96%87%E5%BE%81%E9%9B%86%E4%B8%AD/
