# Data Preparation Draft (Stage 1 & Stage 2) — Version 3 (Certified Handover)

> **Document:** `DATA_PREPARATION_DRAFT_v3.md`  
> **Repository Location:** `D:\Thesis\openalex_feasibility_audit\DATA_PREPARATION_DRAFT_v3.md`  
> **Status:** **DEFINITIVE DATA PREPARATION DRAFT (REPLACES ALL PREVIOUS VERSIONS)**  
> **Date:** 05 November 2026  
> **Target Thesis Chapter:** Chapter 3 (Data Preparation: Sections 3.1–3.4; Forecast Windows, Eligibility, Target & Baseline allocated to Methodology)

---

## English Version

### 3.1 Data Source and Research Scope

We use OpenAlex, an open bibliographic database, accessed through its REST API. The study covers Germany (DE), China (CN) and Japan (JP), with the global total as a reference. The observation period is 2010–2024, which gives 15 annual observation intervals.

Technology topics come from the OpenAlex Topics taxonomy, which groups works by citation-based clustering. We keep every topic in five Physical Sciences fields:

| Field | Topics |
|---|---|
| Engineering | 560 |
| Computer Science | 302 |
| Materials Science | 123 |
| Energy | 27 |
| Chemical Engineering | 13 |
| **Total** | **1,025** |

### 3.2 Work Selection and Country Attribution

**Work types.** The primary modelling panel includes only works of type `article`, `conference-paper` and `review`. We call these *selected scholarly work types*. This is a structural classification assigned by OpenAlex, and we do not claim that every record has undergone formal peer review. A secondary panel covering all document types is preserved as a frozen baseline for sensitivity analysis only.

**Topic assignment.** Each work in OpenAlex has one *primary topic*. We select works strictly with the filter `primary_topic.id`, not `topics.id`. A work therefore belongs to exactly one topic, ensuring zero cross-topic double counting.

**Country attribution.** A work is linked to a country through the institutions listed in its authorships. We count the distinct affiliated countries on each work. We use two counting rules:

- **Whole counting:** a country receives a count of 1 for every work with at least one affiliated institution in that country.
- **Fractional counting (primary rule):** a work with $k$ distinct countries assigns each of them $1/k$ credit:

$$FC_{w,c} = \frac{1}{k_w}$$

where $k_w$ is the number of distinct countries affiliated with work $w$. The fractional publication count of country $c$ in topic $i$ and year $t$ is:

$$P^{\text{Frac}}_{c,i,t} = \sum_{k \ge 1} \frac{N_{c,i,t,k}}{k}$$

where $N_{c,i,t,k}$ is the number of works in topic $i$ and year $t$ affiliated with country $c$ having exactly $k$ distinct countries. The counts are obtained directly from OpenAlex by server-side 2D aggregation on publication year and distinct-country count, returning exact census aggregates. Following post-proposal supervisor guidance (*"Please use fractional counting for publications involving multiple countries"*), fractional counting was adopted as the primary rule because it avoids over-crediting internationally co-authored papers, while whole counts are retained in the panel as an auxiliary reference column.

### 3.3 Dataset Construction and RCA

The final primary panel has one row per topic and year: 1,025 topics × 15 years = 15,375 rows, with 26 columns. Each row stores the global count, whole and fractional counts for DE, CN and JP, the matching national all-science denominators, and the RCA values.

National scientific specialisation is measured by Revealed Comparative Advantage (RCA):

$$RCA_{c,i,t} = \frac{P_{c,i,t} \,/\, P_{c,\text{All},t}}{P_{\text{Global},i,t} \,/\, P_{\text{Global},\text{All},t}}$$

Here $P_{c,\text{All},t}$ is the total publication output of country $c$ across all fields of science in year $t$, and $P_{\text{Global},\text{All},t}$ is the global all-science output. Both denominators strictly use the identical selected scholarly work types scope (`type:article|conference-paper|review`). In the fractional version ($RCA_{\text{AllSci}}^{\text{Frac}}$), both the numerator topic count $P_{c,i,t}$ and the national all-science denominator $P_{c,\text{All},t}$ employ the identical $1/k$ fractional counting rule, ensuring mathematical consistency. An RCA value above 1.0 indicates that the country publishes more in that topic than its overall share of global scientific output would predict.

### 3.4 Data Quality Control and Limitations

**Synchronization of denominators.** On 4 November 2026, OpenAlex executed a database-wide deduplication merge (>17.3 million duplicate works). The topic counts in our modeling panel were retrieved after this update (`23:08–23:52 UTC+1`), whereas the initial denominator table had been retrieved 21 hours earlier (`01:09 UTC+0`), resulting in an intraday global scale shift of $-1.4\%$ to $-5.2\%$. We re-extracted national all-science denominators following the deduplication update (`23:54 UTC+0`) and deterministically synchronized the panel. The original files were preserved unchanged. The fractional RCA values of the synchronized panel correlate almost perfectly with the original panel across all 15,375 topic-year observations per country:
- **Germany (DE):** Pearson $r = 0.99983$
- **China (CN):** Pearson $r = 0.99986$
- **Japan (JP):** Pearson $r = 0.99987$

This demonstrates that the deduplication update shifted denominator scale while preserving topic specialisation rankings.

**Validation.** An automated independent verification script (`independent_audit_v2.py`) executing 29 programmatic checks was enforced on the final panel. The complete check manifest is documented in the Appendix.

| Validation Dimension | Result | Status |
|---|---|:---:|
| Total observations | 15,375 topic-years | **PASS** |
| Unique topics | 1,025 technology topics | **PASS** |
| Observation years | 15 annual intervals (2010–2024) | **PASS** |
| Duplicate topic-year records | 0 duplicate records | **PASS** |
| Missing / null values | 0 across all 399,750 matrix cells | **PASS** |
| Denominator mismatches | 0 mismatched rows across all 15 years | **PASS** |
| Fractional-count bound violations ($0 \le P_{\text{Frac}} \le P_{\text{Whole}}$) | 0 violations | **PASS** |
| RCA recalculation maximum discrepancy | $\le 0.00000500$ across all 92,250 RCA cells | **PASS** |
| Independent audit gate | 29 / 29 checks passed (`exit 0`) | **PASS** |

**Limitations.**
1. OpenAlex does not provide an atomic snapshot identifier. We state that both topic counts and synchronized denominators were retrieved after the 4 November deduplication update and were synchronized using matching denominator records.
2. Topic labels are generated by OpenAlex's October 2026 classifier (fine-tuned Qwen3-8B) and applied retrospectively to earlier publications based on modern metadata rather than classification at publication time. Labels for early years may therefore reflect hindsight, and the topic list was built from citation links that include later papers.
3. Country-level equal fractional counting ($1/k$) approximates national scientific effort by dividing credit equally among affiliated countries, without author-level weighting.

---

### Methodological Formulation (Allocated to Methodology Chapter)

**Forecast Windows.** Evaluation is strictly conducted across two approved forecast origins matching the approved Thesis Proposal:

| Forecast Origin ($t$) | Past Window $[t-2, t]$ | Momentum Base $[t-5, t-3]$ | Future Evaluation Window $[t+1, t+3]$ |
|---|---|---|---|
| **2018** | 2016–2018 | 2013–2015 | 2019–2021 |
| **2021** | 2019–2021 | 2016–2018 | 2022–2024 |

*Rationale for Origin Selection:* Origin 2015 is retained as a training origin for the 2018 test because its three-year outcome window (2016–2018) is fully observed by the 2018 forecast origin. It is not evaluated as a test origin because no earlier eligible training origin is available: a training origin of 2012 or earlier would require a momentum reference window in 2007–2009, which lies outside the 2010–2024 dataset. Under the leakage-free cutoff ($t_{\text{train}} \le t_{\text{test}} - 3$), formal model evaluation is therefore conducted on Origins 2018 and 2021 only.

**Historical Origin-Specific Eligibility.** A topic enters evaluation at origin $t$ if and only if it has accumulated at least 50 global publications in the recent 3-year window:
$$P_{[t-2, t]}^{(i)} \ge 50 \text{ works}$$
Under the primary Selected Scholarly Work Types panel, **992 topics (96.78%)** qualify at Origin 2018, and **995 topics (97.07%)** qualify at Origin 2021. Because eligibility is evaluated strictly using historical data available up to origin $t$, lookahead bias is eliminated.

**Target Variable ($G_{\text{adj}}$).** Future 3-year log growth rate adjusted for global all-science growth:
$$G_{\text{adj}}(i, t) = \left[\ln\left(1 + P_{[t+1, t+3]}^{(i)}\right) - \ln\left(1 + P_{[t-2, t]}^{(i)}\right)\right] - \left[\ln\left(1 + W_{[t+1, t+3]}\right) - \ln\left(1 + W_{[t-2, t]}\right)\right]$$
where $P^{(i)}$ is the global volume in topic $i$, and $W$ is the total global All-Science publication count under the identical Selected Scholarly Work Types scope.

**Momentum Baseline ($M0_{\text{adj}}$).** Consistent window-to-window past log growth adjusted for global all-science growth:
$$M0_{\text{adj}}(i, t) = \left[\ln\left(1 + P_{[t-2, t]}^{(i)}\right) - \ln\left(1 + P_{[t-5, t-3]}^{(i)}\right)\right] - \left[\ln\left(1 + W_{[t-2, t]}\right) - \ln\left(1 + W_{[t-5, t-3]}\right)\right]$$
Because $M0_{\text{adj}}$ applies the identical 3-year span, log transformation, and global expansion adjustment over $[t-2, t]$ and $[t-5, t-3]$, it predicts the exact same conceptual growth quantity as $G_{\text{adj}}$ without learned parameters: $G_{\text{adj}}(i, t) = M0_{\text{adj}}(i, t+3)$.

---

## ฉบับภาษาไทย

### 3.1 แหล่งข้อมูลและขอบเขตงานวิจัย

งานวิจัยนี้ใช้ OpenAlex ซึ่งเป็นฐานข้อมูลบรรณานุกรมทางวิชาการแบบเปิด ผ่าน REST API โดยครอบคลุม 3 ประเทศเป้าหมาย ได้แก่ เยอรมนี (DE) จีน (CN) และญี่ปุ่น (JP) โดยมียอดรวมระดับโลก (Global) เป็นข้อมูลอ้างอิง ช่วงเวลาการสังเกตครอบคลุมปี 2010–2024 รวมทั้งสิ้น 15 ช่วงเวลาสังเกตการณ์รายปี

หัวข้อเทคโนโลยีมาจากอนุกรมวิธาน OpenAlex Topics ซึ่งจัดกลุ่มผลงานวิจัยด้วยการทำ Citation-based Clustering โดยคัดเลือกทุกหัวข้อใน 5 สาขาเทคโนโลยีภายใต้กลุ่ม Physical Sciences ดังนี้:

| สาขาเทคโนโลยี (Field) | จำนวนหัวข้อ (Topics) |
|---|:---:|
| Engineering | 560 |
| Computer Science | 302 |
| Materials Science | 123 |
| Energy | 27 |
| Chemical Engineering | 13 |
| **รวมทั้งสิ้น** | **1,025** |

### 3.2 การคัดเลือกผลงานและการระบุประเทศ

**ประเภทผลงาน (Work Types):** ชุดข้อมูลหลักสำหรับสร้างโมเดล (Modeling Panel v2) จำกัดเฉพาะประเภทผลงานทางวิชาการ 3 ประเภท ได้แก่ `article`, `conference-paper` และ `review` เราเรียกกลุ่มนี้ว่า "ประเภทงานวิชาการที่คัดเลือก" (*Selected Scholarly Work Types*) ซึ่งเป็นโครงสร้างการจำแนกประเภทของ OpenAlex โดยไม่อ้างว่าทุกบทความในกลุ่มนี้ผ่านการทบทวนโดยผู้ทรงคุณวุฒิอย่างเป็นทางการ (Peer Review) ทั้งหมด ส่วนชุดข้อมูลที่รวมเอกสารทุกประเภท (Master Panel v1) ถูกเก็บรักษาไว้เป็น Frozen Baseline สำหรับการวิเคราะห์ความอ่อนไหว (Sensitivity Analysis) เท่านั้น

**การกำหนดหัวข้อ (Topic Assignment):** ผลงานแต่ละชิ้นใน OpenAlex จะมี Primary Topic เพียงหัวข้อเดียว เราคัดกรองผลงานอย่างเคร่งครัดด้วยตัวกรอง `primary_topic.id` (ไม่ใช้ `topics.id`) ทำให้ผลงานแต่ละชิ้นถูกจัดอยู่ในหัวข้อเดียวอย่างเด็ดขาด และไม่เกิดการนับซ้ำข้ามหัวข้อ

**การระบุประเทศ (Country Attribution):** ผลงานเชื่อมโยงกับประเทศผ่านสถาบันต้นสังกัดของผู้เขียน (Affiliated Institutions) ใน Authorships โดยนับจำนวนประเทศที่ไม่ซ้ำกันในแต่ละบทความ และใช้กฎการนับ 2 รูปแบบ:

- **Whole Counting:** ประเทศจะได้รับเครดิตเต็ม 1 คะแนน สำหรับทุกบทความที่มีสถาบันในประเทศนั้นปรากฏอย่างน้อย 1 สถาบัน
- **Fractional Counting (กฎหลัก):** ผลงานที่มีจำนวนประเทศไม่ซ้ำกัน $k$ ประเทศ จะแบ่งเครดิตให้แต่ละประเทศเท่ากันที่ $1/k$:

$$FC_{w,c} = \frac{1}{k_w}$$

โดย $k_w$ คือจำนวนประเทศที่ไม่ซ้ำกันในบทความ $w$ ยอดจำนวนผลงานแบบ Fractional ของประเทศ $c$ ในหัวข้อ $i$ และปี $t$ คือ:

$$P^{\text{Frac}}_{c,i,t} = \sum_{k \ge 1} \frac{N_{c,i,t,k}}{k}$$

โดย $N_{c,i,t,k}$ คือจำนวนผลงานในหัวข้อ $i$ ปี $t$ ของประเทศ $c$ ที่มีจำนวนประเทศร่วมเขียนเท่ากับ $k$ ประเทศพอดี ข้อมูลนี้ได้จากการจัดกลุ่มแบบ 2 มิติระดับเซิร์ฟเวอร์ (`group_by=publication_year,countries_distinct_count`) ทำให้ได้ค่ายอดรวมที่แม่นยำ 100% ตามคำแนะนำเพิ่มเติมของอาจารย์ที่ปรึกษาหลังอนุมัติโครงร่างวิจัย (*"Please use fractional counting for publications involving multiple countries"*) เราจึงใช้ Fractional Counting เป็นกฎหลักเพื่อป้องกันการให้เครดิตเกินจริงในบทความที่เขียนร่วมกันหลายประเทศ โดยยังคงเก็บค่า Whole Counting ไว้ในชุดข้อมูลเป็นคอลัมน์อ้างอิงเสริม

### 3.3 การสร้างชุดข้อมูลและ RCA

ชุดข้อมูลหลักมีโครงสร้างแบบ Balanced Panel ขนาด 1,025 หัวข้อ × 15 ปี = 15,375 แถว รวม 26 คอลัมน์ โดยแต่ละแถวประกอบด้วยยอดผลงานระดับโลก ยอด Whole และ Fractional ของ DE, CN, JP ตัวหาร All-Science ระดับประเทศ และค่า RCA

ความเชี่ยวชาญพิเศษทางวิทยาศาสตร์ระดับประเทศวัดด้วย Revealed Comparative Advantage (RCA):

$$RCA_{c,i,t} = \frac{P_{c,i,t} \,/\, P_{c,\text{All},t}}{P_{\text{Global},i,t} \,/\, P_{\text{Global},\text{All},t}}$$

โดย $P_{c,\text{All},t}$ คือผลงานของประเทศ $c$ ในทุกสาขาวิทยาศาสตร์ในปี $t$ และ $P_{\text{Global},\text{All},t}$ คือผลงานรวมทุกสาขาวิทยาศาสตร์ระดับโลก ทั้งตัวเศษและตัวหารใช้ขอบเขตประเภทผลงานที่คัดเลือก (`type:article|conference-paper|review`) เดียวกันอย่างเคร่งครัด ในเวอร์ชัน Fractional ($RCA_{\text{AllSci}}^{\text{Frac}}$) ทั้งตัวเศษและตัวหารใช้กฎการนับแบบ $1/k$ เดียวกัน ทำให้มีความสอดคล้องทางคณิตศาสตร์ 100% ค่า RCA ที่มากกว่า 1.0 บ่งชี้ว่าประเทศมีความเชี่ยวชาญพิเศษในหัวข้อนั้นสูงกว่าค่าเฉลี่ยสัดส่วนผลงานวิทยาศาสตร์โดยรวมของประเทศ

### 3.4 การควบคุมคุณภาพข้อมูลและข้อจำกัด

**การซิงก์ตัวหาร (Denominator Synchronization):** วันที่ 4 พฤศจิกายน 2026 OpenAlex ได้อัปเดตระบบ Deduplication รวมบทความซ้ำกว่า 17.3 ล้านรายการ ยอดผลงานระดับหัวข้อใน Panel ของเราดึงข้อมูลหลังการอัปเดต (`23:08–23:52 UTC+1`) แต่ตัวหาร All-Science ชุดแรกถูกดึงก่อนการอัปเดต 21 ชั่วโมง ส่งผลให้ตัวหารเดิมคลาดเคลื่อน $-1.4\%$ ถึง $-5.2\%$ เราจึงสกัดตัวหารหลังการ Deduplication ใหม่ (`23:54 UTC+0`) และซิงก์เข้าสู่ Panel ใหม่อย่างเป็นระบบ โดยเก็บรักษาไฟล์เดิมไว้โดยไม่มีการแก้ไข ค่า Fractional RCA หลังการซิงก์สัมพันธ์กับเวอร์ชันก่อนหน้าในระดับเกือบสมบูรณ์ (คำนวณจาก 15,375 Topic-year ต่อประเทศ):
- **เยอรมนี (DE):** Pearson $r = 0.99983$
- **จีน (CN):** Pearson $r = 0.99986$
- **ญี่ปุ่น (JP):** Pearson $r = 0.99987$

แสดงให้เห็นว่าการอัปเดตเปลี่ยนเพียงขนาดสเกลของตัวหาร แต่ไม่ส่งผลกระทบต่อลำดับความเชี่ยวชาญของหัวข้อ

**การตรวจสอบคุณภาพข้อมูล (Validation):** ชุดข้อมูลสุดท้ายผ่านการตรวจสอบอัตโนมัติด้วยสคริปต์อิสระ (`independent_audit_v2.py`) ครอบคลุม 29 รายการทดสอบแบบ Programmatic:

| มิติการตรวจสอบ | ผลการตรวจสอบ | สถานะ |
|---|---|:---:|
| จำนวนแถวทั้งหมด | 15,375 แถว | **PASS** |
| จำนวนหัวข้อไม่ซ้ำ | 1,025 หัวข้อ | **PASS** |
| จำนวนปีที่สังเกต | 15 ปี (2010–2024) ครบถ้วน | **PASS** |
| ข้อมูลซ้ำซ้อน (Topic-Year) | 0 รายการ | **PASS** |
| ค่าสูญหาย (Missing / Null) | 0 ค่า จากทั้งหมด 399,750 เซลล์ | **PASS** |
| ความไม่สอดคล้องของตัวหาร | 0 แถว ตลอด 15 ปี | **PASS** |
| การละเมิดขอบเขตของค่านับแบบเศษส่วน ($0 \le P_{\text{Frac}} \le P_{\text{Whole}}$) | 0 รายการ | **PASS** |
| ความคลาดเคลื่อนในการคำนวณ RCA ซ้ำ | $\le 0.00000500$ จาก 92,250 เซลล์ RCA ทั้งหมด | **PASS** |
| การตรวจสอบอิสระ (Independent Audit Gate) | ผ่านครบ 29 / 29 รายการ (`exit 0`) | **PASS** |

**ข้อจำกัดของข้อมูล (Limitations):**
1. OpenAlex ไม่มีระบบ Snapshot Identifier เราจึงบันทึกตามข้อเท็จจริงว่าชุดข้อมูลทั้งสองดึงข้อมูลหลังการอัปเดต Deduplication วันที่ 4 พฤศจิกายน และซิงก์ด้วยระเบียนตัวหารที่สอดคล้องกัน
2. การจัดกลุ่มหัวข้อใช้ Topic Classifier รุ่นเดือนตุลาคม 2026 (Fine-tuned Qwen3-8B) ซึ่งเป็นการจัดกลุ่มย้อนหลังตามเมตาดาต้าปัจจุบัน ไม่ใช่ป้ายกำกับ ณ วันที่ตีพิมพ์จริง ป้ายของปีแรก ๆ จึงอาจสะท้อน hindsight และรายการหัวข้อสร้างจากการอ้างอิงที่รวมงานตีพิมพ์ภายหลัง
3. การนับแบบ Fractional ระดับประเทศ ($1/k$) แบ่งเครดิตเท่ากันตามจำนวนประเทศที่ร่วมตีพิมพ์โดยไม่ได้ถ่วงน้ำหนักตามจำนวนผู้เขียนรายบุคคล

---

### รายละเอียดส่วนวิธีวิจัย (แยกไปอยู่บท Methodology)

**ช่วงเวลาพยากรณ์ (Forecast Windows):** ประเมินผลเฉพาะ 2 จุดพยากรณ์หลักตามโครงร่างวิจัยที่ได้รับอนุมัติ:

| จุดพยากรณ์ ($t$) | ช่วงอดีต $[t-2, t]$ | ช่วงฐาน Momentum $[t-5, t-3]$ | ช่วงประเมินอนาคต $[t+1, t+3]$ |
|---|---|---|---|
| **2018** | 2016–2018 | 2013–2015 | 2019–2021 |
| **2021** | 2019–2021 | 2016–2018 | 2022–2024 |

*เหตุผลในการเลือกจุดพยากรณ์:* ปี 2015 ใช้เป็นจุดฝึก (Training Origin) ของ Test 2018 ได้ เพราะช่วงผลลัพธ์ 3 ปีของมัน (2016–2018) ทราบครบแล้วก่อนถึงจุดพยากรณ์ 2018 แต่ไม่ใช้ 2015 เป็นจุดทดสอบ เพราะไม่มีจุดฝึกก่อนหน้าที่ใช้ได้ จุดฝึกปี 2012 หรือก่อนนั้นต้องใช้ช่วงอ้างอิง Momentum ปี 2007–2009 ซึ่งอยู่นอกชุดข้อมูลปี 2010–2024 ภายใต้เกณฑ์ปลอด Lookahead Bias ($t_{\text{train}} \le t_{\text{test}} - 3$) การประเมินโมเดลจึงทำเฉพาะจุด 2018 และ 2021

**เกณฑ์การมีสิทธิ์ของหัวข้อ (Historical Origin-Specific Eligibility):** หัวข้อจะมีสิทธิ์เข้าสู่การทดสอบที่จุด $t$ เมื่อมีผลงานสะสมระดับโลกในรอบ 3 ปีที่ผ่านมาไม่ต่ำกว่า 50 ผลงาน:
$$P_{[t-2, t]}^{(i)} \ge 50 \text{ ผลงาน}$$
บน Panel หลัก (Selected Types) มีหัวข้อผ่านเกณฑ์ **992 หัวข้อ (96.78%)** ณ จุด 2018 และ **995 หัวข้อ (97.07%)** ณ จุด 2021 เนื่องจากเกณฑ์นี้ประเมินจากข้อมูลอดีต ณ จุด $t$ เท่านั้น จึงไม่มี Lookahead Bias

**ตัวแปรเป้าหมาย ($G_{\text{adj}}$):** อัตราการเติบโตแบบลอการิทึม 3 ปีข้างหน้าปรับด้วยการเติบโตของวิทยาศาสตร์โลก:
$$G_{\text{adj}}(i, t) = \left[\ln\left(1 + P_{[t+1, t+3]}^{(i)}\right) - \ln\left(1 + P_{[t-2, t]}^{(i)}\right)\right] - \left[\ln\left(1 + W_{[t+1, t+3]}\right) - \ln\left(1 + W_{[t-2, t]}\right)\right]$$
โดย $P^{(i)}$ คือจำนวนผลงานของหัวข้อ $i$ และ $W$ คือจำนวนผลงาน Global All-Science ในช่วงเวลาและประเภทผลงานเดียวกัน

**โมเมนตัมพื้นฐาน ($M0_{\text{adj}}$):** อัตราการเติบโตในอดีตปรับด้วยการเติบโตของวิทยาศาสตร์โลก:
$$M0_{\text{adj}}(i, t) = \left[\ln\left(1 + P_{[t-2, t]}^{(i)}\right) - \ln\left(1 + P_{[t-5, t-3]}^{(i)}\right)\right] - \left[\ln\left(1 + W_{[t-2, t]}\right) - \ln\left(1 + W_{[t-5, t-3]}\right)\right]$$
สูตร $M0_{\text{adj}}$ ใช้นิยามช่วงเวลา 3 ปี การแปลงค่า Log และการหักลบการเติบโตของวิทยาศาสตร์โลกแบบเดียวกับ $G_{\text{adj}}$ ทุกประการ ทำให้ทำนายตัวแปรเป้าหมายแนวคิดเดียวกันโดยไม่มีพารามิเตอร์ที่ต้องเทรน: $G_{\text{adj}}(i, t) = M0_{\text{adj}}(i, t+3)$


---

## References (OpenAlex official sources)

1. OpenAlex (4 November 2026). *17 million duplicate works merged: a new matcher for OpenAlex.* OpenAlex Blog. https://blog.openalex.org/17-million-duplicate-works-merged-a-new-matcher-for-openalex/ (reports 17,315,197 duplicate works merged)
2. OpenAlex (6 October 2026). *Same topics, better assignments: a new topic classifier for OpenAlex.* OpenAlex Blog. https://blog.openalex.org/same-topics-better-assignments/
3. OpenAlex Help Center. *Topics.* https://help.openalex.org/data/topics/
4. OpenAlex Help Center. *Work types.* https://help.openalex.org/data/work-types/

> Citation status: Items 3 and 4 were fetched successfully (HTTP 200); item 3 mentions Qwen. Items 1 and 2 returned HTTP 406 to an automated request, so their content (including the 17,315,197 figure) was not independently verified here. Open them in a browser and check the title, date and number before finalizing. Access dates must be added at submission.
