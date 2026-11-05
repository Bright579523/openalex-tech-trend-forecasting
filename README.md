# Master's Thesis: Forecasting Emerging Technology Research Trends
### A Comparative Study of Germany, China, and Japan Using OpenAlex Data

* **Degree:** Master of Science in Data Science
* **Thesis Target Submission:** 12 February 2027
* **Primary Repository:** `d:\Thesis`

---

## 📌 เผื่อเปิดแชทใหม่แล้วบทสนทนาหายไป: วิธีทำงานต่อทันที

หากเปิดหน้าต่างแชทใหม่ใน Antigravity หรือ ChatGPT แล้วประวัติการสนทนาเดิมหายไป **ไม่ต้องกังวลครับ** ข้อมูลและข้อสรุปทางวิชาการทั้งหมดถูกตรึงไว้ที่ไฟล์ [AGENTS.md](file:///d:/Thesis/AGENTS.md) และเอกสารในโฟลเดอร์นี้เรียบร้อยแล้ว

### ข้อความสำหรับ Copy ไปวางในแชทใหม่ (Prompt to Resume):
```text
สวัสดีครับ ผมกำลังทำวิทยานิพนธ์ปริญญาโทเรื่อง "Forecasting Emerging Technology Research Trends: A Comparative Study of Germany, China, and Japan Using OpenAlex Data" 
โค้ดและข้อมูลทั้งหมดอยู่ที่ d:\Thesis 
กรุณาอ่านไฟล์ d:\Thesis\AGENTS.md และ d:\Thesis\openalex_feasibility_audit\OPENALEX_FEASIBILITY_REPORT.md เป็นหลัก 
เพื่อรับทราบข้อตกลงทางระเบียบวิธีวิจัย สถานะข้อมูลล่าสุด และงานที่ต้องทำต่อ จากนั้นสรุปความพร้อมให้ผมฟังได้เลยครับ
```

---

## 🛡️ ระบบสำรองข้อมูล (Backup Strategy)

ความเสี่ยงที่ใหญ่ที่สุดของงานวิจัยคือไฟล์สูญหายหรือถูกเขียนทับ เราจึงวางระบบสำรองข้อมูล 3 ชั้นไว้ให้พร้อมใช้งานทันที:

### ระดับที่ 1: สคริปต์สำรองข้อมูลแบบ One-Click (`backup_thesis.py`)
เมื่อคุณต้องการเซฟงานในแต่ละวัน เพียงรันคำสั่ง:
```bash
python backup_thesis.py
```
* **การทำงาน:** สคริปต์จะบีบอัดไฟล์งานทั้งหมดใน `d:\Thesis` เป็นไฟล์ `.zip` พร้อมประทับเวลา (Timestamp) เช่น `Thesis_Backup_20261026_014514.zip`
* **ตำแหน่งจัดเก็บ:** บันทึกไปยัง `d:\Thesis_Backups\` และจะ **คัดลอกสำเนาไปยัง Microsoft OneDrive อัตโนมัติ** (`C:\Users\Bright\OneDrive\Thesis_Backups\`) ทำให้ข้อมูลขึ้น Cloud ตลอดเวลา

### ระดับที่ 2: Git Local Version Control (บันทึกประวัติการแก้ไข)
โฟลเดอร์นี้ถูกตั้งค่า Git Repository เรียบร้อยแล้ว เมื่อมีการแก้ไขโค้ดหรือเขียนรายงานเสร็จ สามารถบันทึกจุด checkpoint ได้ด้วยคำสั่ง:
```bash
git add .
git commit -m "Update thesis progress: [ใส่ข้อความอธิบายสั้นๆ]"
```

### ระดับที่ 3: เชื่อมต่อ GitHub / GitLab (Private Cloud Repository)
หากต้องการเก็บโค้ดไว้บน Cloud ส่วนตัวแบบปลอดภัย (แนะนำให้ทำเป็น Private Repository):
1. สร้าง Private Repository บน [GitHub.com](https://github.com) ชื่อ `thesis-openalex`
2. รันคำสั่งเชื่อมต่อในโฟลเดอร์ `d:\Thesis`:
   ```bash
   git remote add origin https://github.com/<YOUR_USERNAME>/thesis-openalex.git
   git branch -M main
   git push -u origin main
   ```

---

## 📂 โครงสร้างโฟลเดอร์และไฟล์สำคัญ (Repository Structure)

```
d:\Thesis\
│
├── AGENTS.md                                # เอกสารหลักสำหรับ AI Agent (Single Source of Truth)
├── README.md                                # คู่มือภาพรวมและวิธีสำรองข้อมูล (เอกสารนี้)
├── backup_thesis.py                         # สคริปต์ One-Click สำรองข้อมูลและ Sync ขึ้น OneDrive
├── .gitignore                               # กำหนดรายการไฟล์ที่ไม่ต้อง Commit ใน Git
├── lens-export.csv                          # ข้อมูลสิทธิบัตร/สิ่งพิมพ์อ้างอิง
├── Lecture 01 Master Colliquim Reseach Topic.pdf  # เอกสารประกอบการเรียน/ข้อกำหนด
├── Lecture 02 Master Good Thesis.pdf        # เอกสารเกณฑ์วิทยานิพนธ์ที่ดี
│
├── openalex_feasibility_audit\              # โฟลเดอร์ชุดข้อมูลหลักและรายงานการตรวจสอบ (Stage 1 & Stage 2 Deliverables)
│   ├── OPENALEX_FEASIBILITY_REPORT.md       # รายงาน Audit ความเป็นไปได้ฉบับสมบูรณ์ (Stage 1)
│   ├── FINAL_FREEZE_REPORT.md               # รายงานรับรองความถูกต้อง Master Panel v1
│   ├── DOCUMENT_TYPE_AND_METADATA_AUDIT.md  # รายงานตรวจสอบขอบเขตประเภทเอกสารและเมตาดาต้า
│   ├── STAGE2_DATASET_AUDIT_REPORT.md       # รายงานสรุปผลการสกัดและตรวจสอบ Dataset Stage 2
│   ├── STAGE2_FINAL_CORRECTION_REPORT.md    # รายงานการกระทบยอดตัวหารและการแก้ไข Stage 2
│   ├── FINAL_DENOMINATOR_AND_RCA_VERIFICATION.md # รายงานยืนยันความถูกต้องของ Synchronized Panel v2 และ RCA
│   ├── CHATGPT_REVIEW_BUNDLE.md             # เอกสารรวมศูนย์สำหรับ Independent Review
│   ├── openalex_master_panel_1025topics.csv # FROZEN Master Panel v1 (All Types Baseline, 15,375 แถว)
│   ├── openalex_modeling_panel_1025topics_v2_selected_types.csv # PRESERVED Original Modeling Panel v2 (15,375 แถว)
│   ├── openalex_modeling_panel_1025topics_v2_synchronized.csv # PRIMARY Synchronized Modeling Panel v2 (15,375 แถว)
│   ├── all_science_national_denominators_fractional.csv # ตัวหาร All-Science Fractional ครบ 15 ปี (v1)
│   ├── all_science_national_denominators_fractional_v2_selected_types.csv # ตัวหาร All-Science Selected Types เดิม (เก็บอนุรักษ์)
│   ├── all_science_national_denominators_fractional_v2_live_recheck_20261105.csv # ตัวหาร All-Science Selected Types ที่ซิงก์ตรงเวลา
│   ├── annual_work_types_and_topic_coverage.csv # ตารางสัดส่วนประเภทเอกสารและความครอบคลุม 15 ปี
│   ├── synchronize_modeling_panel_v2.py     # สคริปต์สร้าง Synchronized Panel v2 แบบทำซ้ำได้ 100% โดยไม่ต้องยิง API
│   ├── extract_denominators_v2.py           # สคริปต์สกัดตัวหารระดับประเทศสำหรับ Selected Scholarly Work Types
│   ├── independent_audit_v2.py              # สคริปต์ตรวจสอบความถูกต้องอัตโนมัติ 28 รายการ
│   ├── candidate_topics.csv                 # รายชื่อ 1,025 Topics ใน 5 สาขาเทคโนโลยี
│   └── all_tech_topics_taxonomy.csv         # เมตาดาต้าอนุกรมวิธาน OpenAlex Topics
│
├── extract_master_panel_1025topics.py       # สคริปต์สกัดข้อมูล Master Panel v1
└── extract_modeling_panel_v2_selected_types.py # สคริปต์สกัดข้อมูล Modeling Panel v2 (Selected Types)
```

---

## 🔬 สรุปข้อสรุปทางระเบียบวิธีวิจัยที่ผ่านการรับรองแล้ว (Methodological Consensus)

1. **Taxonomy & Scope:**
   - 1,025 Topics ใน 5 สาขาเทคโนโลยี (Engineering: 560, Computer Science: 302, Materials Science: 123, Energy: 27, Chemical Engineering: 13) ภายใต้ OpenAlex Topics Taxonomy
   - คัดกรองด้วย **Origin-Specific Historical Eligibility** ($\ge 50$ works ในอดีต 3 ปี $[t-2, t]$) ครอบคลุม 96.1% ถึง 97.2% โดยไม่มีปัญหา Lookahead Bias และตัด Topics ที่ไม่มีผลงาน (21 topics) ออกโดยอัตโนมัติ
2. **Attribution & Counting (Country-Level Equal Fractional Counting):**
   - ใช้ **Option C: Country-Level Equal Fractional Counting ($1/k$)** ผ่านเซิร์ฟเวอร์ 2D GroupBy (`publication_year,countries_distinct_count`) เพื่อให้ตรงตามข้อกำหนด Fractional Counting ของ Supervisor
   - สูตร: $P_{\text{Frac}}(c, i, t) = \sum_{k \ge 1} \frac{N(c, i, t, k)}{k}$ (โดย $k$ คือจำนวนประเทศไม่ซ้ำในบทความ)
   - เก็บค่า Whole Counting ควบคู่ไว้ใน Master Panel เป็นคอลัมน์อ้างอิงสำหรับการวิเคราะห์ความอ่อนไหว (Sensitivity Analysis)
3. **Specialization Metric (Fractional All-Science RCA):**
   - ใช้ **Fractional All-Science RCA ($RCA_{\text{AllSci}}^{\text{Frac}}$)** เป็นฟีเจอร์หลัก โดยทั้งตัวเศษ (ยอดผลงาน Topic) และตัวหาร (ยอดรวมวิทยาศาสตร์ทั้งประเทศ) ใช้การนับแบบ Fractional เดียวกันอย่างสอดคล้อง 100%
4. **Target & Baseline:**
   - Target: การเติบโต 3 ปีข้างหน้าปรับด้วยการเติบโตของวิทยาศาสตร์โลก (Global All-Science Adjusted Growth):
     $$G_{\text{adj}}(i, t) = [\ln(1 + P_{[t+1, t+3]}^{(i)}) - \ln(1 + P_{[t-2, t]}^{(i)})] - [\ln(1 + W_{[t+1, t+3]}) - \ln(1 + W_{[t-2, t]})]$$
   - Baseline $M0_{\text{adj}}$: Adjusted Momentum ช่วงเวลา 3 ปีที่หักลบการเติบโตของวิทยาศาสตร์โลกในงวด $[t-2, t]$ เทียบกับ $[t-5, t-3]$ เพื่อให้สอดคล้องกับนิยามเดียวกับ $G_{\text{adj}}$:
     $$M0_{\text{adj}}(i, t) = [\ln(1 + P_{[t-2, t]}^{(i)}) - \ln(1 + P_{[t-5, t-3]}^{(i)})] - [\ln(1 + W_{[t-2, t]}) - \ln(1 + W_{[t-5, t-3]})]$$
5. **Forecast Origins Scope:**
   - ใช้เฉพาะ 2 Origins ตามข้อเสนอวิจัยที่ได้รับอนุมัติ: **Origin 2018** (ประเมินช่วง 2019–2021) และ **Origin 2021** (ประเมินช่วง 2022–2024)
   - ไม่ใช้ Origin 2012 เนื่องจาก Feature Momentum $[t-5, t-3]$ จะต้องใช้ข้อมูลปี 2007–2009 ซึ่งอยู่นอกช่วงข้อมูลปี 2010–2024 ของเรา

---

## 🚀 แผนงานขั้นต่อไป (Next Steps)
1. **Stage 2:** สกัดและตรวจสอบชุดข้อมูลสมบูรณ์แล้วทั้ง 2 ชุด (Master Panel v1: All Types และ Modeling Panel v2: Selected Types)
2. **Stage 3:** เข้าสู่กระบวนการสร้าง Feature ($M0-M3$) และ Target Variable $G(i, t)$ สำหรับการเทรน Ridge Regression เมื่อได้รับการอนุมัติจากผู้ใช้
