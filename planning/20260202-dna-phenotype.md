# **Technical Blueprint for Genomic Phenotype Prediction: A Comprehensive Implementation Report for 23andMe Raw Data**

## **1\. Architectural Overview and System Design**

### **1.1 Project Scope and Objectives**

The objective of this technical report is to provide a complete, exhaustively detailed specification for the development of a bioinformatics analysis engine capable of predicting non-benign externally visible characteristics (EVCs) and metabolic traits from direct-to-consumer (DTC) microarray data, specifically the format provided by 23andMe. The target system is designed to be integrated into a coding agent or an automated pipeline that ingests raw text-based genotype files, processes specific genetic markers, applies validated statistical models, and outputs a human-readable report detailing phenotypes such as eye color, hair color, skin pigmentation, height, and weight predisposition.

This report serves as the "knowledge base" for the coding agent. It translates high-level academic findings from forensic genetics and Genome-Wide Association Studies (GWAS) into actionable logic, defining exactly *which* SNPs to query, *how* to weight them mathematically, and *how* to contextualize the results for a lay user. The analysis is grounded in the validated methodologies of the HIrisPlex-S system for pigmentation 1 and the GIANT consortium's meta-analyses for anthropometric traits.3

### **1.2 Data Ingestion: The 23andMe Specification**

The foundation of the entire pipeline is the robust ingestion of the user's genetic data. 23andMe provides raw data in a tab-delimited text format that has evolved over several array versions (v2, v3, v4, v5). The coding agent must implement a parser capable of handling these variations while ensuring data integrity.

#### **1.2.1 File Structure and Parsing Logic**

The raw data file typically follows a standard structure that the parser must recognize:

* **Header Section:** Marked by \# characters, containing file creation dates and reference genome build information (usually GRCh37/hg19). The agent must parse the header to confirm the build version, as SNP positions can shift between hg19 and GRCh38.  
* **Data Columns:**  
  1. rsid: The Reference SNP Cluster ID (e.g., rs12913832). This is the primary key for lookups.  
  2. chromosome: The chromosome identifier (1-22, X, Y, MT).  
  3. position: The base pair integer coordinate.  
  4. genotype: The called alleles (e.g., AA, GT, CC).

**Algorithmic Requirement:** The parser should read this file line-by-line or via a dataframe optimization (like pandas in Python) into a Hash Map (Dictionary) structure where Key=rsID and Value=Genotype. This ensures ![][image1] lookup time during the phenotype calculation phase, which is critical when querying thousands of height-associated markers.5

#### **1.2.2 Handling No-Calls and Errors**

A significant percentage of SNPs in any given array scan may result in a "no-call," represented in 23andMe data as \--.7

* **Imputation Strategy:** For critical pigmentation markers (like *HERC2*), a missing value is catastrophic to the model. The agent should be programmed to flag this as "Inconclusive" rather than attempting to guess, given the high weight of these specific variants.  
* **Polygenic Tolerance:** For height and BMI scores involving hundreds of markers, the agent can implement a "mean imputation" or "score scaling" logic, where the final score is adjusted based on the proportion of successfully called SNPs, assuming the missing data is missing at random (MAR).

#### **1.2.3 Strand Orientation and Allele Flipping**

A major technical pitfall in bioinformatics implementation is strand orientation. 23andMe typically reports genotypes on the positive (+) strand of the GRCh37 reference. However, many GWAS papers and forensic tables report effect alleles relative to the gene's transcription strand (which might be negative) or simply report the minor allele found in their specific study.

* **Validation Logic:** The agent must check the "Expected Alleles" against the "Observed Genotype."  
  * *Scenario:* The model expects an effect from allele T. The user's genotype is AA.  
  * *Resolution:* The agent must check if A is the complement of T. If the user's genotype corresponds to the complement of the expected variants (e.g., A/A vs T/T), the agent must flip the user's genotype to match the model's orientation before processing.

## ---

**2\. The Pigmentation Prediction Engine: HIrisPlex-S**

### **2.1 Theoretical Framework: Forensic DNA Phenotyping**

The prediction of pigmentation is the most mature discipline within Forensic DNA Phenotyping (FDP). Unlike complex traits like behavior or longevity, pigmentation is controlled by a relatively small number of highly conserved genes involved in melanogenesis—the production and transport of melanin. The standard system for this analysis is **HIrisPlex-S**, a hierarchical system combining **IrisPlex** (Eye), **HIrisPlex** (Hair), and an extended skin color panel.1

The coding agent should implement this as a deterministic prediction module using **Multinomial Logistic Regression (MLR)**. Unlike a simple "risk score," MLR outputs a precise probability for categorical outcomes (e.g., "Probability of Blue Eyes \= 94.2%").

### **2.2 Eye Color: The IrisPlex Module**

The eye color prediction module relies on a defined set of 6 Single Nucleotide Polymorphisms (SNPs). These markers interact epistatically and additively to regulate the ratio of eumelanin (brown/black) to pheomelanin (red/yellow) in the iris stroma.

#### **2.2.1 The 6-SNP Panel and Biological Function**

The agent requires a precise dictionary of these markers to query the user's genome.

**Table 1: The IrisPlex 6-SNP Panel**

| Gene | rsID | Effect Allele (Dark) | Biological Mechanism | Impact Strength |
| :---- | :---- | :---- | :---- | :---- |
| **HERC2** | rs12913832 | A (or T on \- strand) | **The Master Switch.** This SNP is located in an intron of *HERC2* but acts as an enhancer for the *OCA2* gene. The derived 'G' allele (often reported as C) destroys a transcription factor binding site, dramatically reducing *OCA2* expression and resulting in blue eyes. The 'A' allele maintains expression, leading to brown eyes. | Critical (Explains \~74% variance) 9 |
| **OCA2** | rs1800407 | G | Encodes the P-protein, a melanosomal transporter. The 'G' allele is the ancestral, functioning allele (Brown). The 'A' allele (Arg419Gln) reduces function, lightening the eye. | High 9 |
| **SLC24A4** | rs12896399 | T | A sodium/potassium/calcium exchanger (NCKX4) involved in ion homeostasis within melanosomes. | Moderate 11 |
| **SLC45A2** | rs16891982 | G | Transporter protein (MATP). The 'G' allele (L374F) is a major driver of dark pigmentation in Europeans. | Moderate 11 |
| **TYR** | rs1393350 | A | Tyrosinase is the rate-limiting enzyme in melanin synthesis. 'A' allele maintains high activity. | Moderate 12 |
| **IRF4** | rs12203592 | C | Interferon Regulatory Factor 4; interacts with the *MITF* transcription factor to regulate tyrosinase. | Low-Moderate 11 |

#### **2.2.2 Algorithmic Implementation: Multinomial Logistic Regression**

The agent must implement the MLR equations. The model calculates the natural logarithm of the odds (logit) of a specific eye color category (![][image2]) relative to a reference category (typically Brown).

**The Equation:**

**![][image3]**  
Where:

* ![][image4] is the probability of the target color (Blue or Intermediate).  
* ![][image5] is the intercept for that color.  
* ![][image6] is the regression coefficient (weight) for SNP ![][image7] for color ![][image2].  
* ![][image8] is the genotype dosage (0, 1, or 2\) of the **effect allele** (usually the minor/risk allele).

**Coefficients for Implementation:** Based on the research snippets 9, the agent should utilize the following approximate coefficients (note: these should be treated as representative values for the architecture; precise calibration requires the full supplemental datasets from Walsh et al. 2011/2013).

**Table 2: Estimated Regression Coefficients (Betas) for Eye Color**

| SNP | Allele Checked | Beta (Blue vs Brown) | Beta (Intermediate vs Brown) |
| :---- | :---- | :---- | :---- |
| **Intercept** | \- | **0.50** | **\-1.20** |
| rs12913832 | G (Blue allele) | \+4.52 | \+0.45 |
| rs1800407 | A (Light allele) | \+1.20 | \+1.50 |
| rs16891982 | C (Light allele) | \+0.85 | \+0.60 |
| rs1393350 | T (Light allele) | \+0.40 | \+0.35 |
| rs12896399 | T (Light allele) | \+0.25 | \+0.20 |
| rs12203592 | T (Light allele) | \+0.15 | \+0.10 |

*(Note: The agent must verify if the user's genotype matches the "Allele Checked" and assign a value of 0, 1, or 2\. For rs12913832, if the user is GG, dosage is 2\. If AG, dosage is 1.)*

**Probability Conversion:**

Once the logits (![][image9] and ![][image10]) are calculated, the agent must convert them to probabilities summing to 1:

![][image11]  
![][image12]  
![][image13]

#### **2.2.3 Output Logic and Presentation**

The agent should parse the resulting probabilities and generate a report.

* **Threshold:** If ![][image14], make a definitive call. If not, report "Indeterminate/Mixed".15  
* **Narrative Output:**"Based on the IrisPlex model, your genetic probability for Blue eye color is 94%. This is primarily driven by your genotype (GG) at the HERC2 locus, which strongly inhibits melanin deposition in the iris."

### ---

**2.3 Hair Color: The HIrisPlex Module**

Hair color prediction is topologically distinct from eye color because it introduces **epistasis** (gene-gene masking) and a new phenotype: **Red Hair**. The coding agent cannot simply run a linear regression; it must implement a hierarchical decision tree.

#### **2.3.1 The MC1R Epistasis Logic**

The *MC1R* gene is the key switch between producing eumelanin (brown/black) and pheomelanin (red/yellow). Variants in *MC1R* that cause "Loss of Function" (LoF) result in red hair, regardless of what the other genes (like *HERC2*) are doing. This is epistasis.

**Step 1: The Red Hair Check**

The agent must first query the "R-alleles" (strong effect) and "r-alleles" (weak effect) of *MC1R*.

* **Primary SNPs:** rs1805007, rs1805008, rs11547464.  
* **Logic:** Count the number of variant alleles.  
  * If Dosage ![][image15] (Homozygous or Compound Heterozygous): **Prediction \= RED**.  
  * *Probability:* ![][image16].  
  * *Action:* Stop further color processing or weight Red extremely high.

#### **2.3.2 The Light/Dark Spectrum (Blond/Brown/Black)**

If the user is NOT predicted to have Red hair (i.e., *MC1R* is functional), the agent proceeds to the second tier of the hierarchy: distinguishing light vs. dark hair.

* **Key Markers:**  
  * *HERC2* (rs12913832): Strongly separates Blond (Light) from Brown/Black.  
  * *KITLG* (rs12821256): The 'A' allele is associated with Blond hair. Ligand for the KIT receptor, crucial for melanocyte migration.2  
  * *SLC45A2* and *TYR*: Refine the intensity of the darkness (Brown vs Black).

**Implementation Logic:**

The HIrisPlex system uses an expanded panel of \~22 SNPs. The agent should sum the probability contributions.

* **Blond:** High probability if *HERC2* is GG AND *KITLG* is AA.  
* **Black:** High probability if *HERC2* is AA AND *SLC45A2* is GG AND *TYR* is GG.

### ---

**2.4 Skin Color: The HIrisPlex-S Extension**

Skin color prediction adds complexity due to the global diversity of pigmentation alleles. While *HERC2* and *SLC45A2* affect skin, specific markers are exclusive to skin tone regulation.

#### **2.4.1 The 5-Category Model**

The HIrisPlex-S model predicts five categories derived from the Fitzpatrick scale: **Very Pale, Pale, Intermediate, Dark, Dark-to-Black**.

#### **2.4.2 Critical Skin-Specific Markers**

The agent must include these specific loci in the skin module.1

**Table 3: Key Skin Pigmentation SNPs**

| Gene | rsID | Variant | Effect | Context |
| :---- | :---- | :---- | :---- | :---- |
| **SLC24A5** | rs1426654 | A / G | **The Golden Marker.** The 'G' allele (A111T) is virtually fixed in European populations and is a primary driver of light skin. The 'A' allele is ancestral and associated with darker pigmentation. Heterozygotes are often Intermediate. | 11 |
| **ASIP** | rs6119471 | G / A | Agouti Signaling Protein. The 'A' allele increases pheomelanin, leading to lighter skin. | 11 |
| **TYR** | rs1126809 | A / G | Associated with lighter skin tones. | 16 |
| **MC1R** | (Various) | \- | Variants here contribute to freckling and pale skin (Type I/II). | 2 |

#### **2.4.3 Algorithmic Integration**

The coding agent should utilize the 41-SNP panel defined in HIrisPlex-S.

1. **Input:** User genotypes for all 41 SNPs.  
2. **Processing:** Apply 5 separate logistic regression equations (one for each skin category).  
3. **Output:** A probability distribution across the 5 categories.  
   * *Example:* {Very Pale: 0.05, Pale: 0.15, Intermediate: 0.60, Dark: 0.15, Black: 0.05}.  
   * *Prediction:* "Intermediate."

## ---

**3\. The Anthropometric Engine: Height Prediction**

### **3.1 The Polygenic Paradigm**

Predicting height differs fundamentally from pigmentation. There is no single "tall gene." Height is a quantitative trait with a heritability of \~80%, governed by thousands of variants with minute effect sizes. The coding agent must shift from the "Deterministic" logic of HIrisPlex to the "Cumulative" logic of a **Polygenic Risk Score (PRS)** or **Weighted Allele Score (WAS)**.3

### **3.2 Data Source: The GIANT Consortium**

The Genetic Investigation of ANthropometric Traits (GIANT) consortium provides the "gold standard" summary statistics. Their meta-analyses (e.g., Wood et al. 2014\) identified 697 genome-wide significant variants.

The coding agent should rely on a **Reference Beta Table** derived from these studies. The snippets provide insight into the top contributors.17

### **3.3 Top Loci for the Coding Agent**

While a full PRS uses thousands of SNPs, the agent can generate a "High-Impact Score" using the top loci identified in the research.

**Table 4: High-Impact Height SNPs**

| Gene | rsID | Effect Allele | Effect Size (cm) | Mechanism |
| :---- | :---- | :---- | :---- | :---- |
| **HMGA2** | rs1042725 | C | \+0.41 | Chromatin remodeling; cell proliferation. Homozygotes (CC) are \~0.8cm taller than TT. 19 |
| **GDF5** | rs6060373 | A | \-0.37 (Short) | Growth Differentiation Factor 5; cartilage development in limb joints. |
| **ZBTB38** | rs6440003 | A | \+0.44 | Zinc finger transcriptional repressor; associated with skeletal growth. |
| **CDK6** | rs2282978 | C | \+0.31 | Cell cycle regulation; replication timing. |
| **HHIP** | rs64399 | A | \-0.30 | Hedgehog interacting protein; regulates bone formation. |
| **LCORL** | rs16896068 | A | \+0.28 | Ligand dependent nuclear receptor corepressor; skeletal length. |

### **3.4 Algorithm: Calculating the Polygenic Score**

The agent must implement the following summation logic:

![][image17]

1. **Iterate:** Loop through all ![][image18] height-associated SNPs found in the user's 23andMe file.  
2. **Weight:** Multiply the genotype dosage (0, 1, or 2 of the effect allele) by the beta coefficient (![][image19]).  
   * *Note on Betas:* Ensure betas are in the same unit (e.g., standard deviations or cm). GIANT betas are often in Standard Deviations (SD).  
3. **Normalize:** The raw sum is biologically meaningless without a reference.  
   * Calculate the **Z-Score**: ![][image20]  
   * *Reference Populations:* The agent should use parameters (![][image21]) derived from a control population (e.g., 1000 Genomes European).  
4. **Prediction:** Convert Z-Score to a percentile.  
   * ![][image22] 84th Percentile ("Above Average").  
   * ![][image23] 2nd Percentile ("Short Stature").

### **3.5 Presentation of Height Results**

The report must carefully manage user expectations.

* **Genetic Potential:** Phrase the output as "Genetic Height Potential."  
* **Environmental Caveat:** Explicitly state: "This score reflects your genetic potential. Final adult height is heavily influenced by nutrition, health, and environment during childhood."  
* **Sample Text:**"Your polygenic height score places you in the **85th percentile** of the reference population. This suggests a genetic predisposition towards being **taller than average**. Key contributors include the 'C' allele at *HMGA2* and variants in the *LCORL* locus."

## ---

**4\. The Metabolic Engine: Weight and BMI**

### **4.1 Genetic Architecture of Obesity**

Body Mass Index (BMI) is highly heritable (\~40-70%), but like height, it is polygenic. However, unlike height, there are distinct "risk loci" with significantly larger effect sizes that warrant individual reporting. The coding agent should implement a **Hybrid Model**: reporting specific high-risk genes (*FTO*, *MC4R*) alongside a general polygenic susceptibility score.

### **4.2 The FTO Gene: The "Fat Mass" Locus**

The *FTO* gene contains the strongest known common genetic risk factor for obesity.20

* **Target SNP:** rs9939609 (or high-LD proxies like rs1421085).  
* **Alleles:**  
  * T: Protective / Ancestral.  
  * A: Risk.  
* **Effect Size:**  
  * AT (Heterozygous): \~1.5 kg heavier than TT, 1.3x obesity risk.  
  * AA (Homozygous): \~3.0 kg heavier than TT, 1.7x obesity risk.  
* **Mechanism:** The risk variant disrupts a repressor binding site (ARID5B), leading to overexpression of *IRX3* and *IRX5* in the hypothalamus. This reduces satiety signals and increases preference for high-calorie foods.

**Agent Logic for FTO:**

1. Check rs9939609.  
2. If AA: Output "High Risk." Explanation: "Two copies of the FTO risk variant detected. Associated with reduced satiety and higher average body mass."  
3. **Interaction Insight:** The agent *must* integrate the GxE (Gene-by-Environment) finding: "Research indicates that physical activity can attenuate the effect of the FTO risk allele by up to 30%.".22 This transforms the report from a "diagnosis of doom" to an actionable insight.

### **4.3 The MC4R Gene: The "Appetite" Locus**

* **Target SNP:** rs17782313.  
* **Alleles:** C (Risk) / T (Protective).  
* **Effect:** The *MC4R* gene controls energy balance. LoF variants or associated risk SNPs lead to hyperphagia (insatiable hunger).  
* **Implementation:** Similar to *FTO*, report presence of risk alleles and contextualize with "appetite regulation" rather than just "metabolism.".23

### **4.4 Polygenic BMI Score**

Beyond *FTO* and *MC4R*, the agent should sum the effects of other validated BMI-associated SNPs found in the GIANT BMI meta-analysis.3

* **Top Loci to Include:** *TMEM18*, *GNPDA2*, *BDNF*, *NEGR1*, *SH2B1*.  
* **Calculation:** Sum weighted betas ![][image24] Z-Score ![][image24] Percentile.  
* **Output:** "Global Metabolic Score." A user might have "High FTO Risk" but a "Low Polygenic Score," balancing out their overall predisposition.

## ---

**5\. Technical Implementation Guide for the Coding Agent**

### **5.1 Python Environment and Libraries**

The agent should be constructed using the Python data science stack.

* pandas: For efficient loading and manipulation of the large genotype files (CSV/TSV parsing).  
* numpy: For vectorized calculation of PRS (dot products of genotype vectors and beta weight vectors).  
* scikit-learn (optional): If implementing the MLR models using pre-trained weights, though hard-coding the logistic equations is often more portable for this specific application.

### **5.2 Pseudocode for the Main Pipeline**

Python

class PhenotypePredictor:  
    def \_\_init\_\_(self, raw\_data\_path):  
        \# 1\. Ingestion  
        self.genotypes \= self.parse\_23andme(raw\_data\_path)  
        \# 2\. Load Knowledge Base (JSON or internal dicts)  
        self.irisplex\_model \= load\_model('irisplex\_betas.json')  
        self.height\_betas \= load\_model('giant\_height.json')  
      
    def parse\_23andme(self, path):  
        \# Implementation of parsing logic  
        \# Handle '\#' comments, map rsID \-\> Genotype  
        \# Handle '--' no-calls  
        pass

    def predict\_eye\_color(self):  
        \# Pigmentation Engine  
        \# Check specific 6 SNPs  
        logits \= {'blue': 0, 'inter': 0, 'brown': 0}  
          
        \# Base Intercepts  
        logits\['blue'\] \+= self.irisplex\_model\['intercept\_blue'\]  
          
        for snp in self.irisplex\_model\['snps'\]:  
            user\_geno \= self.genotypes.get(snp.rsid)  
            dosage \= self.calculate\_dosage(user\_geno, snp.effect\_allele)  
            logits\['blue'\] \+= dosage \* snp.beta\_blue  
            logits\['inter'\] \+= dosage \* snp.beta\_inter  
              
        \# Softmax conversion  
        probs \= self.softmax(logits)  
        return self.generate\_narrative("Eye Color", probs)

    def predict\_height(self):  
        \# Anthropometric Engine  
        score \= 0  
        snp\_count \= 0  
          
        for snp in self.height\_betas:  
            if snp.rsid in self.genotypes:  
                dosage \= self.calculate\_dosage(self.genotypes\[snp.rsid\], snp.effect\_allele)  
                score \+= dosage \* snp.beta\_value  
                snp\_count \+= 1  
          
        \# Imputation/Scaling if coverage is low  
        adjusted\_score \= scale\_score(score, snp\_count, total\_snps=180)  
        z\_score \= (adjusted\_score \- REF\_MEAN) / REF\_STD  
        percentile \= z\_score\_to\_percentile(z\_score)  
          
        return self.generate\_height\_report(percentile)

    def generate\_report(self):  
        \# Synthesize all module outputs into final Markdown  
        pass

### **5.3 Output Template Design**

The agent's output should be structured, professional, and readable.

**Section 1: Executive Summary**

* Brief overview of the most striking results (e.g., "High probability of Blue Eyes," "FTO Risk Detected").

**Section 2: Detailed Phenotype Analysis**

* **Subsection: Pigmentation**  
  * *Table:* Probability breakdown (Blue: 90%, Int: 5%, Brown: 5%).  
  * *Narrative:* Explanation of *HERC2* and *OCA2* status.  
* **Subsection: Anthropometrics**  
  * *Chart:* Visual bar showing percentile relative to population.  
  * *Narrative:* Discussion of *HMGA2* and polygenic potential.  
* **Subsection: Metabolism**  
  * *Alert:* FTO Status (Risk/Protective).  
  * *Advice:* Contextual note on lifestyle interaction.

**Section 3: Methodology and Limitations**

* Disclaimer on ancestry bias (models trained on Europeans).  
* Disclaimer on environmental factors.

## ---

**6\. Conclusion and Future Outlook**

This report provides the granular technical specifications required to build a functional genomic phenotype prediction agent. By strictly adhering to the **HIrisPlex-S** protocols for pigmentation and **GIANT-based PRS** for height and weight, the coding agent can deliver forensic-grade predictions that vastly exceed the utility of simple SNP-lookup tools.

The integration of these disparate biological models—deterministic regression for eye color versus cumulative scoring for height—reflects the complex reality of human genetics. Future iterations of this agent should look to incorporate **Machine Learning (ML)** models trained on larger, more diverse datasets (such as the UK Biobank) to refine the beta coefficients and improve accuracy for non-European ancestries, thereby addressing one of the primary ethical and technical limitations of current FDP technology.

By following this blueprint, the developer can ensure the resulting system is robust, scientifically accurate, and provides users with a nuanced understanding of their own biological blueprint.

#### **Works cited**

1. The HIrisPlex-S system for eye, hair and skin colour prediction from DNA \- IU Indianapolis ScholarWorks, accessed February 2, 2026, [https://scholarworks.indianapolis.iu.edu/bitstream/1805/15921/1/Chaitanya\_2018\_HIrisPlex.pdf](https://scholarworks.indianapolis.iu.edu/bitstream/1805/15921/1/Chaitanya_2018_HIrisPlex.pdf)  
2. The HIrisPlex-S system for eye, hair and skin colour prediction from DNA: Introduction and forensic developmental validation | National Institute of Justice, accessed February 2, 2026, [https://nij.ojp.gov/library/publications/hirisplex-s-systemffor-eye-hair-and-skin-color-prediction-dna-introduction-and](https://nij.ojp.gov/library/publications/hirisplex-s-systemffor-eye-hair-and-skin-color-prediction-dna-introduction-and)  
3. Meta-analysis of genome-wide association studies for height and body mass index in ∼700000 individuals of European ancestry \- PMC \- PubMed Central, accessed February 2, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC6488973/](https://pmc.ncbi.nlm.nih.gov/articles/PMC6488973/)  
4. Update on the predictability of tall stature from DNA markers in Europeans \- ResearchGate, accessed February 2, 2026, [https://www.researchgate.net/publication/333551262\_Update\_on\_the\_predictability\_of\_tall\_stature\_from\_DNA\_markers\_in\_Europeans](https://www.researchgate.net/publication/333551262_Update_on_the_predictability_of_tall_stature_from_DNA_markers_in_Europeans)  
5. cslarsen/arv: A fast 23andMe DNA parser and inferrer for Python \- GitHub, accessed February 2, 2026, [https://github.com/cslarsen/arv](https://github.com/cslarsen/arv)  
6. From Raw DNA to Deep Insights: Building a Personal Genomics RAG with LangChain and PubMed \- DEV Community, accessed February 2, 2026, [https://dev.to/beck\_moulton/from-raw-dna-to-deep-insights-building-a-personal-genomics-rag-with-langchain-and-pubmed-9nm](https://dev.to/beck_moulton/from-raw-dna-to-deep-insights-building-a-personal-genomics-rag-with-langchain-and-pubmed-9nm)  
7. How 23andMe Reports Genotypes, accessed February 2, 2026, [https://customercare.23andme.com/hc/en-us/articles/212883677-How-23andMe-Reports-Genotypes](https://customercare.23andme.com/hc/en-us/articles/212883677-How-23andMe-Reports-Genotypes)  
8. Raw Genotype Data Technical Details \- 23andMe Customer Care, accessed February 2, 2026, [https://eu.customercare.23andme.com/hc/en-us/articles/115002090907-Raw-Genotype-Data-Technical-Details](https://eu.customercare.23andme.com/hc/en-us/articles/115002090907-Raw-Genotype-Data-Technical-Details)  
9. HIrisPlex-S Eye, Hair and Skin Colour DNA Phenotyping Webtool, accessed February 2, 2026, [https://hirisplex.erasmusmc.nl/](https://hirisplex.erasmusmc.nl/)  
10. Forensic DNA Phenotyping: Genes and Genetic Variants for Eye Color Prediction \- MDPI, accessed February 2, 2026, [https://www.mdpi.com/2073-4425/14/8/1604](https://www.mdpi.com/2073-4425/14/8/1604)  
11. Improved eye- and skin-color prediction based on 8 SNPs \- PMC \- NIH, accessed February 2, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC3694299/](https://pmc.ncbi.nlm.nih.gov/articles/PMC3694299/)  
12. Association between brown eye colour in rs12913832:GG individuals and SNPs in TYR, TYRP1, and SLC24A4 \- PMC \- NIH, accessed February 2, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC7485777/](https://pmc.ncbi.nlm.nih.gov/articles/PMC7485777/)  
13. A comparative GWAS of eye colour in light and dark eye genetic backgrounds defined by HERC2 rs12913832 polymorphism \- bioRxiv, accessed February 2, 2026, [https://www.biorxiv.org/content/10.1101/2025.07.20.665796v3.full.pdf](https://www.biorxiv.org/content/10.1101/2025.07.20.665796v3.full.pdf)  
14. The Prediction of Human Pigmentation Traits from Genetic Data Susan Walsh, accessed February 2, 2026, [https://repub.eur.nl/pub/40312/130605\_Walsh,%20Susan%20-%20BEWERKT.pdf](https://repub.eur.nl/pub/40312/130605_Walsh,%20Susan%20-%20BEWERKT.pdf)  
15. DNA-based eye colour prediction across Europe with the IrisPlex system \- PubMed, accessed February 2, 2026, [https://pubmed.ncbi.nlm.nih.gov/21813346/](https://pubmed.ncbi.nlm.nih.gov/21813346/)  
16. Global skin colour prediction from DNA \- PMC \- PubMed Central, accessed February 2, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC5487854/](https://pmc.ncbi.nlm.nih.gov/articles/PMC5487854/)  
17. Genome-wide association analysis identifies 20 loci that influence adult height \- PMC \- NIH, accessed February 2, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC2681221/](https://pmc.ncbi.nlm.nih.gov/articles/PMC2681221/)  
18. Identification of ten loci associated with height highlights new biological pathways in human growth \- PMC \- PubMed Central, accessed February 2, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC2687076/](https://pmc.ncbi.nlm.nih.gov/articles/PMC2687076/)  
19. HMGA2 Is Confirmed To Be Associated with Human Adult Height \- PMC \- NIH, accessed February 2, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC2972475/](https://pmc.ncbi.nlm.nih.gov/articles/PMC2972475/)  
20. The common rs9939609 variant of the fat mass and obesity-associated gene is associated with obesity risk in children and adolescents of Beijing, China \- PubMed Central, accessed February 2, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC2914647/](https://pmc.ncbi.nlm.nih.gov/articles/PMC2914647/)  
21. FTO Biology and Obesity: Why Do a Billion of Us Weigh 3 kg More? \- PMC \- PubMed Central, accessed February 2, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC3355857/](https://pmc.ncbi.nlm.nih.gov/articles/PMC3355857/)  
22. Assessing effect of interaction between the FTO A/T polymorphism (rs9939609) and physical activity on obesity-related traits \- NIH, accessed February 2, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC6226419/](https://pmc.ncbi.nlm.nih.gov/articles/PMC6226419/)  
23. common obesity variant near MC4R gene is associated with higher intakes of total energy and dietary fat, weight change and diabetes risk in women \- Oxford Academic, accessed February 2, 2026, [https://academic.oup.com/hmg/article/17/22/3502/647433](https://academic.oup.com/hmg/article/17/22/3502/647433)  
24. MC4R Variant rs17782313 Associates With Increased Levels of DNAJC27, Ghrelin, and Visfatin and Correlates With Obesity and Hypertension in a Kuwaiti Cohort \- PubMed Central, accessed February 2, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC7358550/](https://pmc.ncbi.nlm.nih.gov/articles/PMC7358550/)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACgAAAAYCAYAAACIhL/AAAACTElEQVR4Xu2WTYhOURzG/75DQ6QxJqYs1CwwFjSbSTMj0iSsJCnJQqEUaWRjRZqNBcpC0xQp0TTMbOSjRBZkJco0mhWDhc8sKPE8/c/NOU/3ve4071sW86tfbz3P7bzn3nvuuddskv+LGfAGXKZFAQvgAJynRS24ALdrGLFcg8AGeBtO06Ka7IL9GoI62A4vwU9pldALj2tYCV7uE/AqvAnvw0ew2/LPcip8AzdLvga+Nx/nJfyc1gmt5sfO1kLZDYfhUfM/zlgEn8G7cFaUk61wBE6RPGbQiidIRuEhDWN64Bhs1iLQCX/Dk5JfhuckU8pMsA/e0zBjn/mfb9IiglfuF3wq+Sv7x5lbuQlyDl80JLxi3+FjLYS55ifxIcrmh2xblOVRZoLrzcdq0IK3h8V+LYRsgIdR1hIydkWUmeBq87FWxiGfynehqLRPZZwxPy5eb+tCtirK8uAEc29fRJP5WO1xOCeEdHpcCLzsXAY/LZ1MdgX5W0SZCS41H4sbd8LzUBTtQefNj9HNlK+1srf4q4YCby3HWqvFqVB0aRE4YN5f1ML+PjhbtBA4wW8aCm3mY9Vrwdv8Gr6w9AmaCU/DH/CIVd6IR+FhDYU75kuEJ1SJPZbuEAmL4Vn4wPz1xs33GjwGl0TH5cH36BUNwULz8fgOztb5R/PJ8mopXEa3NKwGe83PnJ9bE+EJ3KlhNeDHBbeqHVqMgxXwrRXvJBPiIBzScBz0ma/BmsEvH34PbtSiBB3ma77mcB+9Dhu1KIAPEj/huJNMUnX+ADsHeLXs4xiUAAAAAElFTkSuQmCC>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAsAAAAXCAYAAADduLXGAAAAu0lEQVR4XmNgGEEgB4hfAfF/IC5Ek8MK0hggim3QJbCBpUD8AYiZ0SXQAUjBSyBegS6BDVgwQJyQBOXbAvFqID4DxPYwRTBQywBRLAPEGUAcywDR+AmIs5HUgcEhIL4ExAVAHAoV8wDi2UDMD1MEAmEMEFPtGCAm3wPiRcgKkMEUIH7HgAgFkFtBtoBADBC7QNlgAJLYjMTfBMQ7GSCaQcHJApPgAOJfQBwJEwACayA+DMTHGCBOGwWUAQCj4iBRWQWdtAAAAABJRU5ErkJggg==>

[image3]: <data:image/png;base64,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>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFgAAAAYCAYAAAB+zTpYAAAEb0lEQVR4Xu2YeahVVRSHfw3SLAnRSCRNajRYYNAAFRViVFSQQQNa0UAalhFNf2TzQAOI0pxEg81a0kxZETRQVCollRUWNPwRDRRYSK3PdfY9+623z+1e8T14z/vBD+5Ze5999t177bXWOVKPHj1qdjU9HY3DmENNd0XjQLGJ6W3T6GAf7lxnuioaB4K7TRdF43rAxqblpoNjQ4kJptdMv5j+NX1eXaO3Kvs80zbphoqxpj9NI4M9soXpPNMLpi9NH5o+Md1p2sh0kumKVu/OeMz0l3y+40PbYHGp6blobAeTZsJ7B/s4+Z9hwXNuMz0QbJHjTd+ZvjVNNY3K2ibJF3u16bDM3imPm/4wjYgNg8RuKq9XIyzE99FY8al8sDGZjb6Ts+vIWfJ7HjZtGtoSbOpv6n6RNjD9bHo2Ngwy35hmRWOJfVUvRmRLuQej5IG7yPtzX4kDTX+bXpLHqyau1NotEuPz/HNiwyDzkGlhNJYgnjBhvC5yvrzt2sx2YmXbOrPlvKP+Hl/iVNPJ0SgPH8S39+Q5gI3fPGsngzP+jpktQW6YZ/pAfsrII5SSsLPpPtNX8v91jWmR6RXTPlWfbmAeS6KxxKvyCe+e2fDWqfKjeJNpw6ztQnnsLHGCfKy18UyOPsnvM3nsh+1MP5luSZ2MN+QLGDnD9KM89gNl5Mumd6vrR+SL/ah8juea9jR9Ybqj6tMN000/RGOEELBK/kASGZNfKQ8J95r2r7u2uET+R0rcIx9rRmzogFnye/cKdl5kvq5+U5WwuTfUzWs42vSPfNFymEca8/nKxgampL2ffMFHV9eEn4/kSfT/YEN5Zu58/ThOzfG3CTwYzy7xpnw83njawVE+Nrtmo6kKOE0RvJVNhxSejqib17DY9Ltps2C/XX3D1U7V9cxWj/4QRjpxkNPkY7Vd4NnyTlNiQxtOl+9cCQI/402MDYH5qmMjpNASa2IWBI9NDjBXXn9TQycIZ9z7YmZLLJVne8IPpEXBU5ug/wHRWOAC06/RGFkhf+D2saENx8jv2So2GEfJ24ilJVgY4h1hJgdv5r4UPxO3VvaDqmsS1ILqd4qbJFv6UJvnpDFJ4gnCHovSVN1Q35JYmScJmFqfU1MCZ+ClqRE8iAmUEkY70n2l+Aw3ytunBTveSPIrVQ7EVuLsxZmNKoOTkl7H8UJyw+XyEDGnssOT6ptYqQqo7bHnR5jKol1pNUW+gWfKF3uZ6ZQ+PWrul8fvfhwiL4GoVVkIMiFBH8/sFI4Rr8BNHC4vtT6WJ5fr5Yu3Q9Ynsoc8FLBQhBC+dcTyifLqdXllkJ86ThPx9in5vSSp+H/oQ8XQLnw9KN8E/luTlyco0fLTsU5hIl29iw8RcBxKRMpCylPYtm5uMVJ+uroJrV3BlyQeUCr2hyq8B6Rq5Wx5NUFOObLVowYPfyYa1zUcw8uicQjDlz1OJpBfFptuVl2BJAgdhIf8xWxA4BPm+/LktT5xtcqfFQYECvgnonEYwwtU8vIePYYh/wHXEPCn3RCLVAAAAABJRU5ErkJggg==>

[image5]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABUAAAAYCAYAAAAVibZIAAABLElEQVR4Xu3SvytFcRjH8cfP/AUGxYCU0R2w+pVJIbLcCElJmQxKsmGhZFCilOFuspnchRIxmQyUFKX8AQy8vz2P45xnkItFnU+96pzn8/12+p6+ImnS/L+0YR/HOMcsihMrCkwWj2iw91o8YdHe59Ftz99KC17Q4+abeEAJTlCWrL/OJa79kMzhDcNYj82bcYFcbJZIk+jGDV+QadHuDNWu28KMm0UZEt046gsyJdqN+YLcIuOHH2kX3ej/Z8iCaNfq5nV4Fv3Xg9hGX3xBBW6wFptVYVX0er1iAL2osX7EunC68IEr0RMnEq7PHg5whF10WTeBUxyi3GY7uMckSm3264T/2YgVLNms8rMuPPW4s+dx0VvQiY5oxQ/SL3r8kHAd81hGUbQizZ/nHdGrNN5czcbdAAAAAElFTkSuQmCC>

[image6]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABwAAAAYCAYAAADpnJ2CAAABv0lEQVR4Xu2VTyifcRzHPziQqJ1c5E8SV2LKHBbJstuiHIRos0TtZGJuclBs2WkrtewmhbDakoNaK7lIaydSlD8nauXisL0+fb+/n+/v8xNbPeTgVa96Pu/n0/P8vn+e70/knlsiFUfxC/7A95iZ0BEx77AuqBdwPKgjpROfm2wE10wWCen4DVNMvoqfTBYJHdhisho8wiKTR8I0PhC3WU7xJx5gZdgUJbo5lHocwi7cFLeukVOCEzaEV+JeGjk6iiYbwgs8F/dtxpjDZ0Ed0oqH2GtvWD5ijg3FjfrYZPrDLuuNsYPlNrQs2kDc57GBX+2NKyjGE0mckSR0Z+qutE3N+AerfV2GYzgb70hGN9o8ZoibVh1IQUIHPMV1HPZ1Grbhb3wZaxK3gUpxO8gsU/hGXK+O9gwLwwZFD2p90ACu4B4uYUPYBHniHvbW5CG6fr/wsb0RsmyDK9jCh+JebtER7YubTj0OGzHb13G00Dn/FyrEfZO5+NpnVfjEX+v6ffbXemq1iztA9KVxauVi7a5DD4fvOIlZPvuAu/5a/9Zip1I3zmCPr+P0S/Ja/S+DNrhJ8rHPhjfJI7mY3rvHX9HKRbsdl4B2AAAAAElFTkSuQmCC>

[image7]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAcAAAAXCAYAAADHhFVIAAAAa0lEQVR4XmNgGOQgEIifA3EAugQIxALxRSDWQJcgD6QA8T4oNkOWUAXidVD2CSBehiTHUA3E1kCsCMT/GSCmoAAWIL4LxIvQJUAgjAGiyxKIZYC4DlmyD4ivI7F1keTAnt7JAHGMH7LEMAEAhkkREHK1PNMAAAAASUVORK5CYII=>

[image8]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABUAAAAYCAYAAAAVibZIAAABNklEQVR4Xu2TvytFYRjHn1xyB5NkkQyKLFJSNkZGWWWw2CiDxY9koqRk9w8oNjFZFGUgBgsGJpMMKAY+z33ec++5T+dw0lnU/dSne/t+z33Pe97zXJEa/5oOXMZjvMdTvMap0G/gUPieiSV8wwscwcaQF3AVz0NfDPmv7OAXrmBddVWiHh/xwBdpzEhlwZ84xDkfJtGKL3gnlcdNYw27fJjEptguM+0gKzdii/b6IiN7OBYP9PB1wdd4GENHSvu4OgVxxsWOsAqdwU9JfuMRD/iBPb5IY1FsB8MujxgU6/dd3ofruOvyEnoER/iME9iJDWIDP4pn+I6T0Q8Cs9iNty4vo48+jSf4JLYz/dzGFrEX0Vy+2mjHBbHpyZUrHBC7QS704yW24bzr/oz+s/S4trDJdTVy5BtcFzleZfqDlwAAAABJRU5ErkJggg==>

[image9]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACYAAAAYCAYAAACWTY9zAAAB30lEQVR4Xu2VTSilYRTH/4bMGPkaYmGhJplGNrKRjA0WNhKyU3cxmmKajcgUGxQJGcxqIlKkWUgslJ2wGWlSMgtraVbzkaYhzfyPc+7cx7OYhXvzbt5f/eo553mfe8/z9b5ASEjIDVV0m36lf+gvekDn3YeCZA1aWIXfESQPoCv2xe8Imkroas34HUHTDy2s2e8Imh16SbP8jiCRYq6hxf2PZPqBXtFMJ18EvdX7Ti4hyPbJNg76HUY3LbD2C3ro9EXppZN+Ml5moYXV+h3kCd1z4gE65cRRNmmLn4yXE/qbpnv5JLpIu5ycbNlHOkJXaCpNoRc0156po9O0z+KndN3awkM6bi7RMqfvH8+gqyV/6JIG/fGfiF2IR/QHfW7xBm2l1fTIco/pS/qKvrfca2gBgkxWxtVb3EGbrH1DDbSYz9DCziyW8/PNcuJydAB0zK4Tf6IR+hax85VBs6FfkUbLLdBOa0tB59AjMUTbLB8Xb+iEteXP5fVSTrdwe9ay2t+h2yycQp+TMbK97mQTQgSxm9uD2FdCzlchdBWEEnps7VJokTnQibVDVzOKrFiDE9+JPOhleAfdOvm+CnIE5mixxXKO5JYO0zG6Cn3/5UPHjEInJb8l51GeDwm5F/4CDw9Za5bGCtAAAAAASUVORK5CYII=>

[image10]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAF0AAAAYCAYAAACY5PEcAAAD20lEQVR4Xu2YaaiWRRTHT6m5IYooWbmXC2qQJm7lggvol4rcQFFxA7VQW2iRLDONct9xATVcSJD8YJIY+EEroyxMo/xkgiSZX8w+hIrk/8eZh3ccXO7LvS8XZP7w486ceZ65M2fOnJnnNcvKysrKysqqMQ0QX4u/xf/iP3FSbI8fyqqMDpg7/dm0Iasyetg80s+mDVmVUz/zKF+fNmRVTu+ZO/3ltCGrcjomroumaUNWZYSjb5o7vip6TaxOjffQUNE5NdaiOoifxW+RrZw5PSmGp8ZyRUohtSxOG4LeEI9G9d6iT1S/n06LgamxljVTbInq5cxpg1iQGssVneD0YWmD1Fx8mxrLUEvxr6iXNtSyuB5PSY1VFLuk2kH0u7gmGif2h8Rn4pVQbyI+EkdFC3NHbhZfiUniLfPJEEVoqXmU/2n+8dU12FuLreIT8/4biNGh/KHYIQ6KLuIp8//Bh9qr4k3zvvigI9qWi712u3huo/lNbGKwcSX+WOwWq8Rl8zSRzqnQLPOdwLO885wYb56C+XhkDNRRfbEisEv0CPa7iokR5XQSq6FYZx6lxeHKQHDQedFRvCC6i1/EvPDMGPFFKCMmujCqPya+E0+YO2KbaCXeFRPEGdHMfGL0jZPbhnqx/deKL8Ujoq75+PmL3rFSmuxm7gi00vw99JK4EMrpnBDj+NG8T/4H/RfpdaTd7isCkwAZEeoEHP3fUYPMXz5l3unFUGfrXAk2iKOojfl7/ESAGAjp5x8rpQ+imwkW+l4MiepE1QnxgXjfPIIQfZPm4gUq7OwCdlOhb8SLocxCnA9lgoMgWSaWmO9QbKS4G+a7BnFGEb0onRNi4aeF8jPi16iNnRWPEWf/FWzMbVzUVmNiyzJoBouY/OFSs/1k7mSilXTFghBJbN064pCYXTyciFTETSfVp+Y7ARF5V80XGzFZFutx85RD8KTCMX9E9f1iqpWiN55TI/Ng6xTa5pqnN3YjOm4+P4KMMbCz0vRWo8Jpl8wHuybYiOq3Q7mdOGc+GPLt8+aDREQ125Vc/nqwMXAinlRD2uE7gbSWinTUP5TjPhGHPM7Gce3Nc3WRanqK+aKXla7DPENkcr5wRUznRMqjDwKFBSZIppufEbSR5hgjKYg+OMs4xwoR6aOierVF/iLXMbing+2I6BvKOO8H8bl5ZBM1pCxuCYPDM9g5KFmsPVa6BRDh6bmCcAq/CRWOnGOewgqR2/dZKadycO4Um8zPk+JywG4h12PjcOQs4aePO81psvkhv8h80TjEi93JQckYxoY6C8GzLDoXgRnmfWZlZWVlPcC6BXDuwgk4WX36AAAAAElFTkSuQmCC>

[image11]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAmwAAAAuCAYAAACVmkVrAAAEvklEQVR4Xu3dWahuYxgH8NcUMhxEpI5jnsucMcpMppRkKOLGlCHJkDnDDcp84sIpmcuUWSklFDem5ELKWJKSJCSex1pf33teZw9n+zafvX+/+rfX+6y1v/2dq/O0hmeVAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMDsujLyalsEAGB8vBC5ui0CADA+fo+s0RYBABgft1fbq0e27Lf3jFxW7QMA4D+wUuS4fnu7/ucZkSsil0d2i5zW1++NHBk5L7JRXwMAYITybNnO/fY79Y7Go5HbIg+Wrom7KXJi5MzIff0xq/Y/AQAYoT8i10cWR1Zr9gEAMAaebgsAANO1SmRhW5wlp7aFeeS9avvtahsAYFInR55si7Noi8jXbREAYL7aI/J96e6dykn6r/fr9atjvoocXq3Ty6X7nW9K93uZd6v930XOr9bL69m2AAAwn30R+bKpZTO2Tb99Z72jksNc16vWt0Qu7refKN04ipnKOWMHtkUAgPkqm7Oc6zVwVumeVEwLIsdW+wZ2jVxbrY+IfFat8zMHcszErZEV+nV79iz/1huRl5r6Xc16ID97otxQHQcAMGdkozOYnH965NvIiv16p8j+/XYt54Vlk3V36c6s5WXUtar9dcO2d7/OeWH5uY9U+w4qw4cMcq5YrT4OAGDeOrp0w1cnkg1bpvVLWyjDJm2dsvSLyteN3NNv531tg0ut2aDl71wVuTCyYV8feK1Z/xPtmTgZrwAAk/i0TP4Ko3zh+FFtsfz9P9mty/DJzvtLd//aBv06L1Ou3G/nmbjcl03iA5FP+npau9pOdzRrAIB5qW28luWCtlCWHruRT5B+HjmgXz9flm6+zi3Dqf359/K4i0rXCA7O1OVZt3buWN5LBwDANOQ9bTk499+0rAcdRmXw8MNs+rktjIH8Tt4vCgBzVJ4he64tzqKtIh+0xRHI++fej/za7pjAXm1hOYzy/rvakrawHK5rCwDA3JFPdv6bbzp4MbJ9Wxyhn9rCBA5uC8vhxrYwIu3ok+nK+wYPa4sAAONqug3bTBucfcvwgYvBAx2De/ou6X/OVL5RYiYur7aPr7Zb9Ty+mVizLfQm+5sAAH8zqoZtUele1j6YWfdQ6QYE5wMYefnx48hHkW37/W+W7unYHSOPRW6PbFK6p2o37o+ZynQatvqtFXmmMt/N+mPk5tJd2s4RKzuU4XfJ+9pO6I/Ps5v5gMjZkX1KN4Nvs8gukYf747KpezTyTOSK0s3fWxLZr3T/nnxDxeqlu1fwmjJUfy4AwKQmatjybFg7H6zOIcND//Jh5K1+O8ea5Ey7ZTm5dO9mzWbonNKNSsnm7pXIwtI1ORM9DJCjTdrvUad1SuSY0jVHh5bhOJVW/t18k8TgTOCS0jV3i8uwwUz1wx/5nbPJ3DxyaRk2j/nd8569nKeXn5dvthg0ZY9HNi3dZ9afCwAwqYkattZUZ9iyYdqjLc6yqc6w/dYWAAD+j0bZsC2q1nlJcLZN1bDlIOTaes0aAGCs5b1VOZw3G61sbKZqfqZq2E4q3b1heWnzqWbfbJnqO+drwH4o3XfKS5QAAHPagrYwBnZvCwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwp/0JlG4hTF8+9FgAAAAASUVORK5CYII=>

[image12]: <data:image/png;base64,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>

[image13]: <data:image/png;base64,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>

[image14]: <data:image/png;base64,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>

[image15]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB4AAAAXCAYAAAAcP/9qAAABXklEQVR4Xu3UvyvFURjH8cdvEbKwKNnEX2ASi1kGG1EkJgYGKSbJIBlYJBFlovwYlJJNDAaDSbHZjJR4P/dIzzlu3/v9ugy4n3rV7XnO7dx7fonk8gdSghU84B6bqPNG/FC2sYRadOIRt6i0g1owi3pbzCJtOEWeqQ3jFfOmlkoDFrGMpqCXNBN4xqip6TLrxPqv00aXZg5baA96cTMmbpI1U6t+r+meR6YK49hDN/L9dmSK0Cv+fraKm/jE1CKjp3MQB+hDod+OHT3hOnFH2MgUnXBH3NUoD3qZ0ogXTIWNqOiEPbjGmST/xWW4En+/I1OMIdxgXdyVSxq9TnpIV1EQ9D5FBwzgApOo8duJMo1d8Q/mgvmcSgVGcIR+cYcqm3ThXPzzoKuoD8tH9Kjvi3va7Gvz1TSLeyIvcSxu9e7whA0z7tujz6JenXRmzLh/GN1j3Ys4DlHqvpbLL8gbqdVEuHfVlAcAAAAASUVORK5CYII=>

[image16]: <data:image/png;base64,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>

[image17]: <data:image/png;base64,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>

[image18]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABIAAAAYCAYAAAD3Va0xAAABBElEQVR4XmNgGAUDBqyAeDcQ3wfi/0B8AlUaDHYA8W8GiPwzIG5ElUYFO4H4AQNEsRmqFBgUAfF8dEF0wA3E14E4gQFi0HoUWQiYAsRO6ILowA2IJwExGwPCVerICoDgFANEHi/oBuIAKLuYAWIQyGAYkAfirUh8nOAMEPNB2TxA/AaIPwGxAFQsjQESRniBOBAfQhNrY4C4CuQ6EFgJxAYIaewgCohr0MQkgPgbED8FYl4gvoEqjR3MYYCkJXQwgwHiqsVQTBBcA2IWdEEg0GCAGATCiWhyGMALiM8DMSO6BBSsZoAYJI0uAQM2DJCYgtn4AIjtkBVAgSUQX0IXHAWjAAgA8tMw5+vmET0AAAAASUVORK5CYII=>

[image19]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABEAAAAXCAYAAADtNKTnAAABKUlEQVR4XuXTvytFcRjH8ecykAx2WQysCoNMJINNlEm6IqOJW5dNBnUR/4DMCvlRJIO63ZJFMpoMMt4yGtz343vv8Xg495z9fuo1fD/fb+d0nnOOSEOkCZu4RAn7aPt1IkV2MWrWpyiYdWKyWHDdBu5cF5sWXCPj+lscuC42c5hx3TDe0e362ByiQ8JAy3jGGwbsoaToADVjyGMejxLmlCo92PYlWZZwoVTRu035kiziU8K3U8sxJs06ypkvJLylB1z5jf+iw9RB2rtppvGFoeq6D1s4ik6YTOAe69V1M2bxgaXaIQnz6cWL6aLof6KbOdzgFecYt4dIF9aw4/rvXPiiTp4wKOGCUVpxYos66ZfwujuxajdG5GcWSdFvqYg9tNuNFfn77I2cCnXOLf0d3+bpAAAAAElFTkSuQmCC>

[image20]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIYAAAAeCAYAAADpTGa/AAAEbklEQVR4Xu2ba6hVRRTHVy96WVQWWVbQQwtLwqjIpLqU9qKyT1aE3Zv0VIjsYRmlRg96o9ED7WFqZQVFEj1Ioz5EFhhUYEFEfQj9HAWF+iH/v9bM3XPGwn1O4r3n7PnBH/fM7HvOnD1r1lp7ZjTrbs6U3pIelxZLD0inttxRaBwnSx9JI0L5YOlXadfBOwqN5EXp1qzusaxcaCDPSRukGebeImeM9JL0lPS8tKe5N7lHWik9HQS3SB9Kd0pLzD3RLqHtiFD3iLRM2ivUDyUrpKPD9bnm4bQQGCWtkjZJf0v3Z20/S8dIh0p/mD/Ih8wfamSdNEW62dx4MIDJ5n+LER0mfSGNDuUXzD97KNlf+ssqA31YerBqLkQOMPcCGMeBoQ4DwCuk7Cdtlk5M6jCMa8w/4zupL2kDktm10nxpnjSptXmHgte67z+UhsyLpU+SMt6NunY4xNyT3pY3dDtPZmXCxO/SPqH8qXR91fwPF5h7gghG9Ju5R8EL4HnyMPG+uTcZTuAdonekv39KI81/R10ImRdaFY5qMct89jG7vpJWJ4pu+47Bu3c+u0kbzd18hBl1dVJeKl2blOkvr7bfJ3V4gevC9ZXSZ1XTIISWOKv2MP8bwsrU0AYMFAMD9GFAukjaV5ojXS5ND/8Srm63bQ27HdZIM8M1/f5WOkc6z/z3ECrnmk+MsebPZpp5LgLnSz+YeyK8aG1wTV+aJ10pT5gbxaKsfmdzmjTbfO2CPj0jXdVyhxvNu9K95rMrrm0QYhaaJ64LQh0w4DyoHJJajIyBfE06yzwpPSOUge8BZu835v3i2TE45CQYyeHSBOlt88GgrhP4Djwj4Y3Qg/HHRBrDPduqxJTvIwcjzPZZqxHEPteGH7DeqrWByN3mRsEsidl6k8ENE2IIQculI82TWAznPXNDfFk6KtxPqMOrvB7KncLnf55XJuDJ8PgRvHyEPgAG9GpSXwvcz41ZHVaJUfAAyuKRM848hAyYvyoyO5m1uOybzCcPrvsy81l8irkLz59tuxCaHs0rE/CI9C1CX/BufVblE6dLd8Ub6oLlp4NPwrZFetM8tteBWYQhtSMeWmH7ECYYk05hbPAoGEvHjDfP2j+Qds/aCt3Js/b/El871nzfgQx476yt0FDIqH8yX/FLk1Ay4neS8lCQh6CiHa9/hRUx3kp4XWU1MKXf6q2UdZJjsAxdGKbwnvt10EFZG4P9i7W3ulboAcgjyCcIIXiNCAbC6tqP5svDhYbBu3ju3nP1D95dKBQKhfqcZL70zeJf9KjsYZRX+wZznPkuLWcgyMfY0Lq05Y5CI2H1kJ3TCHtIJOjtwr4US9z5hmWhS2GNZ2K4ZrOM1/gTquZasMXwhvnmW9mt7hF4gzs+XN9gfuA4kh/GyQ/rANvfnNP4WLok1BV6ALbR2W0mpHAONJ5zgPwwTn5YJ8JJryuScqHHyQ/j5Id1IpzlSM9NFHqc/DBOflgn0s75lkJDIKS8klcWmg3/AYo9qXhie9iyFY/RNhYO7IvnAAAAAElFTkSuQmCC>

[image21]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEoAAAAYCAYAAABdlmuNAAADIklEQVR4Xu2WaahNURTHlylzhpIhJZTM0ycpeUSRhJL5FTJPkRQhGUJCIkPKPEUhU4SkEDJGPphFZCpKSBL/f2vv+/Zd596u7r3vvvfh/OpX96x9bnufvddee4vExMTExMTExMTkg/Vwg4lNhudMrCxpDvfBr/BvCjuXvFo6VBXtfJmJ34RHTaysaAM/wAeii3pfdHJOw8VwLqyUeLuUKBLtdFAQqw5/w/lBrKyoAu/BXbCii3FSnsMD/qVCsEh0ohoGsR4u1iuI5UILeB4+hJ1MWyYmiI6lgYmfgRdMLBcGwsvwhugui8AOH5sYM4kZxczKB2vgErgfNjZtmeD2umuD4DXcYoM5cB2OE83cCEzlLxJtPCVao0iHsCFLrkn22fkUbjOxbqJZNsXEs6U2/Amr2QZPW9EOudqeGqLFfSOsCa+6+Cx4Fs6D20VPxAqubQbcDDfB0S5GWou+xz64TWYHbR7WmzES3VoeboWlJsbMfALrBjHWMmYu+1kAd4gWfsKttNbJk7O9i5Mh8A78LPrf3kFbgkmiH3HIPfPDmc4/RDsbK1rD6sGpcKvoJPWBL0QzktvUn5iceA4mpB18aWIhvIZwDOlO2GmiH+AL+Xj4CXZNvKEMgB3hI1gsOqa9ot/EHdLXvTcRDna/Pfy2PSaWBBvfwiPwkugW5IxyMLfgTtEMqyW6ejyei/hHRx34TXQlV8DpLhYyCh4zsZB+8A98Yxsc/NCFotnMw+CE6IJYmsJG8LskbyFO0HvRa8RyOCxo8zAB5thgyCt40AbTwEH8kuRBdIfvgudUrBQdYCY4EbkyHF40MWZ8pm+8IiUZF4ErwJSfaRvSMEL0+AxpJroNKrvnLhKtQyfhSBOz1BetHbnCOmkXhdvwePDMjOofPBMW8iYmloAfzon633sNCz7T18LivVu0tjF7eACE8GKYqY91kryls4XZ1NPEWNtWix40LDW8l/lDiLSEH4PnCLz237bBPMOTjPXBF+JUsP6lWoBCMRQetsFCwSOfhZcnJ1eyPML74TO4SlIX+ILA1OaFlZnCq0V5pJVoEbc1NSYb/gHgSZsO68vduQAAAABJRU5ErkJggg==>

[image22]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGkAAAAYCAYAAAD5/NNeAAACrklEQVR4Xu2YXYgNYRjHHx+FUFKsRBEiwqZNlI9NPu5JKLU+Eq29WKy4UCJyo8SNQi4UIrkgUlz4KJFcUkSUXLjxmYQL/n/PnNM7z+6ZMzNnzplxen/1u9j/OzvNO895v0bE4/F4PE3KRBtUYT68Cu/Bu3BRqNWTGcNhOzwDP4WbIpkH38O5wd9L4Q+4pHxFTmyHf+Av+BjedvwZtPWUr86X3XCWDQ2t8AO8AJ/Dz+HmSJ7AEyY7D6+ZrOHcgo/gOJMfFS3QcZPnyUHRX3tcrkv8Ik0R7W+XyffDr3CgyRvGWPgMDjP5XtEHPgX7mbY8OST1K9Ia0T6vN/mOIF9s8loYCpfZsBJb4FaTbRR9qHOwv2nLm8NSvyLtFO03i+VSWg42mbwWBokuJ7EYL+FCrIC/4SU4wMmjGCPaiSQu//efyalnkfZJ30XaFuT2x1wrnBVKG5TYzBTt0E3Jcf6tQj2LtEf6LhKLw3yzyWuFo+kKbLENlZgE38E7cIhpy4PV0nv0RcmdqV1XCYv0xYYV4NTPe601eWeQrzR5FoyG9yXGvbmrewUfSrijg0UPdUUizUiKW6RVosXYYPJdQd5uche+bPfoksS38AVskwqMEt3dcQs+wrR1iC6m1UizJvGQmIY0ReL2OQ4TRJ+t2+RHRA+09v1kAftyViKWF57KnwaONG188W8kwXzZINIU6ZsNAxbCdSbjp6DTJuNBlmtH1kyGlyVig8Z1h+sPpzmOphIsFufkl/CGkxeFpEXidPJd9FziwrMfi8eRM8fJ+Z3vtej5kUyHH+HU8hXZcUx6f0AIwQraKcjaUb66OMQpEn9oHBH8ZlfqC180C7bAue6B6OcjO4tMgwfgRXgSzg43ZwLXft6/KYlTpP8BjmzuqJuSGVKMI4LH4/F4PB5PMfgLSVK3Q45Pn1gAAAAASUVORK5CYII=>

[image23]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGkAAAAYCAYAAAD5/NNeAAAC3UlEQVR4Xu2YWahNURjHP1MIhZsxihApKUk8GDI+KfGAqGt2w4MxHkSKPFCGF6IUJZEoIRnKUCJ5UGSIKElKMjwIif/ft865a3+3fc6+9r737HNbv/o9nP9a57TXXmevtb4tEggEAoEWRD94GX6BT+Fu2DHSI55x8By8BW/CCZHWQCZ0hs/gMlgDN8M/8ILfKYax8B0c4z5Phd/h5GKPCrFadBA/4X14zfOHa9tY7J1/tsFdJjslOo6ZJrc8gAdNdlKSTXCTcgXeE10ifPaKDuyAyfPORfgJjveyBaJjOe5lliGifdaYfDv8CtuavNnoC5+ILhE+W0Qv+AhsZdryznnRa1/iZbNcdsbLLHNF+yw0+TqXTzR5GjrBaTaMYzlcabLFohd1ArY2bdVATzhfote+VXRMO7zMsl60DyfLp7Ad+JOelvai20ki+kt0MDPgL3gatvHyUvQWHURjnP7vm80Dx/EYfoR9TJtPYSLtJNW53P6Z07JT6g8oiRkBP4seXSu2/jYBPOXxj8eTWikKp0A7SZwc5ktNnhY+TWdhL9sQxyD4Fl6X5PVENTBMtFbiwaEcXPo5GfNMvsrls02eBVyab0uC3+ap7iW8K9EDRAfRoq5SHJZoOVDKFe47Pt1El7mkT8Ac0clYZPINLp9kch/ebHtNSX0Dn8PREkMP0dMdj+BdTVut6GZajv/Zk8otPWlpB6/CTV7GSWMNFccA0Wtba3K+rWBBa+9PFrB4PiYltpcu8KGzu2njjX8tjVgvc8Z+eMhkfL2zx/vMOoqnQB++CjpqMhay3DuyZrBoSRB7QOO+w/2HyxyfpgKcLK7JL+AlL68mWOfwibjhfATfw99Svyyy9vvm+o1yGRkIX4nWj2S4aGE8tNgjO/ZJwxcIETiDdgmy1hZ7Vxdcuu1YCk7x+t2BH6ThKsLDBuspvkri0zgy2pwJ3Pv5+4EcwzcOPFEHAoFAIBAIBFo8fwFyBLmDV3OLPwAAAABJRU5ErkJggg==>

[image24]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABMAAAAXCAYAAADpwXTaAAAAbElEQVR4XmNgGAWjgKogAF2AErABiAXRBckFLkBcgS5ICegBYit0QXIBMxCvBOJKIGZFllgIxLvJwBeA+B0QJzJQCESBeD0Qi6FLkAqYgHgrEEuiS5ADgoE4Gl2QXADyHkqgUwL00AVGwSAAAG69EzceZiPbAAAAAElFTkSuQmCC>