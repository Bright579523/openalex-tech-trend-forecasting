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
├── openalex_feasibility_audit\              # โฟลเดอร์ผลการตรวจสอบความเป็นไปได้ (Audit Deliverables)
│   ├── OPENALEX_FEASIBILITY_REPORT.md       # รายงาน Audit ฉบับสมบูรณ์ (CONDITIONAL PASS)
│   ├── AUDIT_CORRECTIONS.md                 # รายละเอียดการตอบข้อซักถามทางเทคนิค
│   ├── openalex_feasibility_audit.py        # โค้ดสำหรับรัน Audit 3 ขั้นตอน
│   ├── data_audit_summary.json              # สรุปผลทางสถิติในรูปแบบ JSON
│   ├── run_log.md                           # บันทึก API call และประวัติการรัน
│   ├── candidate_topics.csv                 # รายชื่อ 1,025 Topics ใน 5 สาขาเทคโนโลยี
│   ├── all_tech_topics_taxonomy.csv         # เมตาดาต้าอนุกรมวิธาน OpenAlex Topics
│   ├── national_annual_totals_all_science.csv # ยอดตีพิมพ์รวมระดับชาติรายปี (Global, DE, CN, JP)
│   ├── full_1025_topics_historical_volumes.csv # ตารางปริมาณผลงานย้อนหลังของ 1,025 Topics ใน 4 Origins
│   ├── full_universe_origin_eligibility.csv # สถิติสัดส่วน Topics ที่ผ่านเกณฑ์ >= 50 works (96-97%)
│   ├── sample_topic_country_counts.csv      # ตัวอย่างข้อมูล 45 แถว
│   ├── enriched_panel_with_both_rcas.csv    # Pilot Panel 50 Topics x 15 ปี พร้อม RCA ทั้งสองแบบ
│   └── model_pilot_results_allsci_consistent.csv # ผลประเมินโมเดล M0-M3 ของช่วงนำร่อง
│
└── proposal_audit_csvs\                     # โฟลเดอร์สำหรับตรวจไฟล์ CSV เพื่อเขียน Proposal
    ├── audit_csv.py                         # สคริปต์ Python ตรวจโครงสร้างและค่าสถิติในเครื่อง
    ├── full_1025_topics_historical_volumes.csv
    ├── full_universe_origin_eligibility.csv
    └── model_pilot_results_allsci_consistent.csv
```

---

## 🔬 สรุปข้อสรุปทางระเบียบวิธีวิจัยที่ผ่านการรับรองแล้ว (Methodological Consensus)

1. **Taxonomy & Scope:**
   - 1,025 Topics ใน 5 สาขาเทคโนโลยี (Engineering: 560, Computer Science: 302, Materials Science: 123, Energy: 27, Chemical Engineering: 13) ภายใต้ OpenAlex Topics Taxonomy
   - คัดกรองด้วย **Origin-Specific Historical Eligibility** ($\ge 50$ works ในอดีต 3 ปี $[t-2, t]$) ครอบคลุม 96.1% ถึง 97.2% โดยไม่มีปัญหา Lookahead Bias และตัด Topics ที่ไม่มีผลงาน (21 topics) ออกโดยอัตโนมัติ
2. **Attribution & Counting:**
   - ใช้ **Whole Counting** ผ่าน Server-side aggregation (`group_by=authorships.institutions.country_code`) เพื่อความคุ้มค่าและเป็นไปได้จริง
   - ยอมรับข้อจำกัดการนับซ้ำจาก International Co-authorship (~1.054 ประเทศต่อบทความ) ในบทข้อจำกัดของวิทยานิพนธ์
3. **Specialization Metric:**
   - ใช้ **All-Science RCA ($RCA_{\text{AllSci}}$)** เป็นฟีเจอร์หลักในการวัดความเชี่ยวชาญระดับชาติเมื่อเทียบกับงบวิจัยและศักยภาพวิทยาศาสตร์รวมของประเทศ
4. **Target & Baseline:**
   - Target: การเติบโต 3 ปีข้างหน้า $G(i, t) = \ln(1 + P_{[t+1, t+3]}) - \ln(1 + P_{[t-2, t]})$
   - Baseline $M0$: Momentum ช่วงเวลา 3 ปีที่สอดคล้องกัน $M_{\text{window}}(i, t) = \ln(1 + P_{[t-2, t]}) - \ln(1 + P_{[t-5, t-3]})$
5. **Temporal Train/Test Split:**
   - Cutoff ป้องกันการรั่วไหล: $t_{\text{train}} \le \text{test\_origin} - 3$
   - สาเหตุที่ $N_{\text{train}} = 50$ (ที่ origin 2018) และ $200$ (ที่ origin 2021) ใน Pilot เกิดจากการขยายช่วงรายปี (Annual Rolling) โดยที่ origin 2018 มีปีย้อนหลังถึงปี 2015 ได้ 1 ปี ($1 \times 50 = 50$) ส่วน origin 2021 มีปี 2015..2018 ได้ 4 ปี ($4 \times 50 = 200$)

---

## 🚀 แผนงานขั้นต่อไป (Next Steps)
1. นำข้อมูลจาก `proposal_audit_csvs` และคำอธิบายใน `README.md` / `AGENTS.md` ไปเขียนเล่ม Proposal
2. เมื่อพร้อมรันการสกัดข้อมูลจริงขนาดเต็ม (Master Panel 1,025 Topics $\times$ 4 ประเทศ $\times$ 15 ปี = 4,100 API calls) สามารถใส่ OpenAlex Free API Key แล้วรันได้ทันที (ใช้เวลาประมาณ 3–5 นาที โดยไม่มีค่าใช้จ่ายจริง)
