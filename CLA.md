# Contributor License Agreement (CLA)

**Project:** Edges of Light  
**Copyright Holder:** Or Gal

By submitting any content (“Contribution”) to this repository, you agree to the following terms.

---

## 1) Definitions
- **Work**: The contents of this repository and any future collected or published editions based on it.  
- **Contribution / Contributor**: Original text or other content you submit and that is merged into the main branch.  
- **Words Changed**: For a given Contributor, the total number of words **added plus deleted** in merged commits to `main`, measured using the Git history.  
  - Words Changed are **counted forever** — once credited, they remain in the tally for all future revenue-sharing, even if later altered or removed.  
  - Edits that delete or modify another person’s text still count toward the editor’s Words Changed.  
  - Unmerged pull requests do not count.

---

## 2) Grant of Rights
You grant the Copyright Holder an **exclusive, irrevocable, perpetual, worldwide, royalty-free license** to use, modify, reproduce, distribute, display, and create derivative works from your Contribution in any form or medium, including for commercial purposes, subject to the revenue-sharing terms in Section 6.

---

## 3) Ownership & Warranties
You represent and warrant that you own or control all rights in your Contribution and that it does not infringe any third-party rights. This Agreement does not transfer ownership of your underlying authorship, but it grants the exclusive license described above.

---

## 4) Moral Rights
To the fullest extent permitted by law, you waive any moral rights you may have in your Contribution.

---

## 5) No Obligation to Use
The Copyright Holder is under no obligation to use, merge, publish, or distribute any Contribution.

---

## 6) Revenue Sharing
If the Copyright Holder commercially publishes or otherwise monetizes the Work (e.g., printed book, e-book, audiobook, licenses, adaptations, or similar), the Copyright Holder will allocate **30% of Net Revenue** as a **Contributor Pool** to be shared among all Contributors.

**Net Revenue** means gross receipts actually received by the Copyright Holder from monetization of the Work **minus** direct, third-party costs for that monetization (e.g., printing, distribution/platform fees, payment processor fees, sales/VAT/GST, reasonable shipping/fulfillment for physical editions). General overhead and unrelated income are excluded.

---

### 6.1 Allocation Formula — Text Contributions
**Variables:**  
- **Wc_text** = Lifetime Words Changed (added + deleted) for text.  
- **WEU_assets** = Lifetime Word-Equivalent Units from non-text assets (see Section 6.2).  
- **W_translated** = Lifetime number of words translated into another language.  
- **τ** = Translation factor (default **0.60**).  
- **R** = Net Revenue for the accounting period.  
- **P** = Contributor Pool percentage (**30%**).

**Contributor’s Lifetime Total:**  

Wc_total = Wc_text + WEU_assets + (τ × W_translated)

**Payout Formula:**  

Contributor’s Payout = (Wc_total ÷ ΣWc_total_all_contributors) × (P × R)

---

### 6.2 Non-Text Assets & Translations — Word-Equivalent Units (WEU)
To keep allocation fair across different types of contributions, all non-text work is converted to **Word-Equivalent Units (WEU)** and added to the contributor’s lifetime tally.  
WEU accumulate **forever** — once credited, they remain in the tally for all future revenue-sharing.

| Contribution Type                          | WEU Credit                                 | Notes |
|-------------------------------------------|---------------------------------------------|-------|
| **Original illustration / image**         | **500 WEU** per accepted asset              | For substantial, story-relevant images (hand-drawn or AI-assisted). |
| **Map / complex diagram**                 | **1,000 WEU** per accepted asset            | Significant design effort with narrative or gameplay relevance. |
| **Cover / hero artwork**                  | **1,200 WEU** per accepted asset            | Includes design, composition, and refinement. |
| **Icon set / small graphic bundle**       | **300 WEU** per cohesive bundle             | Group of related small assets used together. |
| **Audio narration (finished minutes)**    | **100 WEU / min**                           | For final mastered minutes released publicly. |
| **Original music (finished minutes)**     | **150 WEU / min**                           | Original composition created for the project. |
| **Sound design / audio edit (finished min)** | **75 WEU / min**                           | Cutting, mixing, SFX, mastering. |
| **Video trailer / motion edit (finished min)** | **250 WEU / min**                         | Final exported runtime. |
| **Subtitles / captions (per source min)** | **30 WEU / min**                            | Creating readable timed text. |
| **Translation (target-language words)**   | **τ × words** (default τ = **0.60**)        | Credit for the translator; the original author’s text is not double-counted. |

---

### 6.3 Examples
1) **Illustrator + Writer**  
- 2 accepted illustrations = 2 × 500 = **1,000 WEU**  
- 3,200 Words Changed (text) = **3,200**  
- **Wc_total = 1,000 + 3,200 = 4,200**

2) **Translator (EN → ES)**  
- 18,000 Spanish target-language words  
- τ = 0.60 → **10,800 WEU**  
- **Wc_total = 10,800**

3) **Video Editor**  
- 90-second trailer (1.5 min) → 1.5 × 250 = **375 WEU**

4) **Audio Team**  
- 5-minute narrated chapter: Narrator 5 × 100 = **500 WEU**;  
  Mixer/Sound Design 5 × 75 = **375 WEU**.

---

## 7) Reporting
At each payout, the Copyright Holder will provide a brief summary of:
- Net Revenue for the period,  
- Total Wc_total counted, and  
- Each Contributor’s Wc_total used in the allocation.

---

## 8) Governing Law
This Agreement is governed by the laws of the **United States of America**, without regard to its conflicts of law principles.

---

## 9) Miscellaneous
This is the entire agreement regarding Contributions, superseding any prior understandings.  
If any provision is held unenforceable, the remainder remains in effect.  
This Agreement may be updated prospectively by posting a revised version in the repository; submitting Contributions after such posting constitutes acceptance of the updated terms.

---

**By submitting a pull request, you confirm that you have read and agree to this Contributor License Agreement.**
