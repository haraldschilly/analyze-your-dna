# **Technical Specification for Genomic-to-Phenotypic Reconstruction and Generative Visualization**

## **1\. Architectural Overview and System Objectives**

This technical report delineates the architectural and logic specifications for extending the analyze-your-dna project into a comprehensive **Genomic-to-Phenotypic (G2P) Translation Engine**. The primary objective is to empower a coding agent to ingest raw consumer genetic data (specifically the 23andMe format), rigorously parse informative Single Nucleotide Polymorphisms (SNPs), and utilize statistical prediction models to infer a user’s visible physical traits and relevant non-benign ocular conditions.

Crucially, this system transcends traditional static reporting by integrating a **Generative AI Interface**. The inferred phenotypic profile—encompassing pigmentation, craniofacial morphology, dermatological texture, and body habitus—will be synthesized into a deterministic text prompt. This prompt allows image generation models, such as Stable Diffusion XL (SDXL) or DALL-E 3, to render a photorealistic "Digital Twin" or forensic sketch of the subject at a specified age.

The scope of this analysis is stratified into five functional domains:

1. **Pigmentation Prediction:** Leveraging the forensic-grade HIrisPlex-S system for eye, hair, and skin coloration.  
2. **Craniofacial and Anthropometric Morphology:** Inference of facial features (nose, chin, ears) and body statue indices (BMI predisposition, height potential).  
3. **Dermatological and Integumentary Traits:** Analysis of hair texture, male pattern alopecia, canities (graying), and freckling.  
4. **Ocular Refraction and Pathology:** Assessment of "non-benign" visual traits including myopia, hyperopia, and age-related macular degeneration (AMD), which influence the visual depiction of the subject (e.g., the necessity for corrective lenses).  
5. **Generative Synthesis:** The translation of probabilistic biological data into semantic token weights for AI image generation.

## ---

**2\. Data Ingestion and Normalization Layer**

To ensure the coding agent can reliably process user inputs, a robust data ingestion pipeline must be established. Consumer genetic files, particularly those from 23andMe, follow specific formatting conventions that require normalization before analysis.

### **2.1. File Parsing Logic (23andMe Standards)**

The input is typically a tab-delimited text file, often compressed. The parser must handle the header metadata and the four-column structure: rsid, chromosome, position, and genotype.

**Parsing Requirements:**

* **Header Stripping:** The agent must programmatically ignore all lines originating with the \# character, which contain build versions (e.g., GRCh37/hg19) and processing timestamps.1  
* **Genotype Representation:** 23andMe reports genotypes as base pairs (e.g., AA, GT).  
  * **No Calls:** The string \-- or II indicates a genotyping failure (no call) at that locus.1 The agent must treat these as NULL and apply fallback logic (e.g., population-based imputation or skipping the specific trait prediction).  
  * **Indels:** Insertions and Deletions are sometimes marked as I or D, or explicitly written (e.g., GTTT). For most predictive models discussed below, these must be mapped to the standard I/D nomenclature used in the scientific literature.  
  * **Hemizygosity:** Markers on the X or Y chromosomes in biological males may appear as single characters (e.g., G). To ensure compatibility with diploid logic gates used in standard prediction algorithms, the agent must normalize these to a pseudo-homozygous format (e.g., GG).4

### **2.2. Reference Genome Alignment**

Most 23andMe raw data is aligned to **GRCh37 (hg19)**. However, newer chips or third-party sequencing might use **GRCh38**. The agent must verify the assembly version from the header. If there is a mismatch between the input coordinates and the prediction model's expected coordinates, the rsID (Reference SNP Cluster ID) should be the primary key for lookup, as it remains constant across builds unlike physical position.

### **2.3. Strand Orientation Handling**

A critical source of error in G2P systems is strand orientation. 23andMe typically reports alleles on the positive (+) strand of the reference genome. However, some scientific literature reports risk alleles on the negative (-) strand.

* **Logic:** If the user's genotype is GG and the model expects CC, and G is the complement of C, the agent must recognize this as a match.  
* **Agent Instruction:** Implement a complement flipper function: ![][image1], ![][image2]. If an allele does not match the expected forward variants but matches the reverse complement, flip the input before processing.5

## ---

**3\. Pigmentation Analysis: The HIrisPlex-S Protocol**

For the prediction of Eye, Hair, and Skin color, the system must implement the **HIrisPlex-S** logic. This is the current forensic standard, validated for high accuracy in identifying phenotype from DNA traces.7

### **3.1. Ocular Pigmentation (Eye Color)**

Eye color is an oligogenic trait primarily driven by a regulatory element in the *HERC2* gene that controls the expression of the *OCA2* (Oculocutaneous Albinism II) gene. The prediction model relies on a hierarchy of epistatic interactions.

#### **3.1.1. The Master Regulator: *HERC2* rs12913832**

This single polymorphism accounts for the majority of blue-brown variability in European populations. The SNP is located in intron 86 of *HERC2* and acts as an enhancer for *OCA2*.11

| Genotype | Phenotypic Implication | Mechanism |
| :---- | :---- | :---- |
| **GG** (Ancestral) | **Blue / Light Eyes** (Recessive) | Reduces chromatin looping, silencing *OCA2* expression. Low melanin production in the iris stroma. |
| **AA** (Derived) | **Brown / Dark Eyes** (Dominant) | Enables *OCA2* activation. High production of eumelanin. |
| **AG** (Heterozygous) | **Intermediate / Hazel / Green** | Variable penetrance. Requires secondary modifier analysis. |

**Agent Logic:**

1. **Primary Check:** Query rs12913832.  
2. If GG: Base prediction is **Blue**.  
3. If AA: Base prediction is **Brown**.  
4. If AG: Base prediction is **Hazel/Intermediate**.

#### **3.1.2. Modifier Loci for Fine-Grained Prediction**

To distinguish between Blue, Green, Grey, and Hazel, the agent must analyze secondary loci that modulate melanin density and structure.8

| rsID | Gene | Alleles (Effect \> Ref) | Impact on Phenotype |
| :---- | :---- | :---- | :---- |
| **rs1800407** | *OCA2* | **A** \> G | **Arg419Gln**. The A allele acts as a hypomorphic mutation, further reducing melanin. In rs12913832(AG) carriers, this shifts the eye color from Hazel to **Green** or **Blue-Green**.8 |
| **rs12896399** | *SLC24A4* | **T** \> G | Associated with lighter iris pigmentation. TT genotypes correlate with lighter/greyer shades of blue.8 |
| **rs16891982** | *SLC45A2* | **G** \> C | **Phe374Leu**. A major skin lightening allele that also affects the iris. GG contributes to "clear" blue or green eyes; CC contributes to darker or "muddy" pigment.8 |
| **rs1393350** | *TYR* | **A** \> G | Variants in Tyrosinase affect the rate of melanin synthesis. A alleles are associated with lighter pigmentation.8 |

**Calculated Output for User Report:**

"Your genotype at the primary locus rs12913832 is \[Genotype\], which sets your baseline eye color to. However, the presence of the \[Allele\] variant at rs1800407 (OCA2) suggests a reduction in eumelanin density, shifting your likely phenotype towards. The statistical confidence for this prediction is \>90% based on the HIrisPlex validation datasets."

### ---

**3.2. Hair Pigmentation and Biochemistry**

Hair color prediction requires analyzing the ratio of eumelanin (black/brown) to pheomelanin (red/yellow). The *MC1R* gene is the central switch in this pathway.

#### **3.2.1. The Red Hair Epistasis Check**

The agent must *first* screen for Red Hair alleles on the *MC1R* gene. These alleles result in a loss-of-function receptor that fails to stimulate eumelanin production, defaulting to pheomelanin.8

**Key *MC1R* Variants (The "R" Alleles):**

* **rs1805007 (Arg151Cys):** T allele.  
* **rs1805008 (Asp294His):** T allele.  
* **rs11547464 (Arg160Trp):** A allele.

**Logic:**

* Count the number of risk alleles across these three loci.  
* **Count ![][image3] 2 (Homozygous or Compound Heterozygous):** Phenotype is **Red / Ginger**.  
* **Count \= 1:** Phenotype is **Carrier** (likely has hidden red highlights, "strawberry blonde" potential if other genes are light, or reddish beard in males).

#### **3.2.2. The Blonde-Brown-Black Continuum**

If the subject is *not* Red, the agent proceeds to determine the darkness of the hair using *SLC45A2*, *KITLG*, and *TYRP1*.8

| rsID | Gene | Alleles (Light \> Dark) | Logic |
| :---- | :---- | :---- | :---- |
| **rs16891982** | *SLC45A2* | **G** \> C | GG is strongly associated with **Blonde** to **Light Brown** hair in European populations. CC strongly predicts **Dark Brown** to **Black**.8 |
| **rs12821256** | *KITLG* | **A** \> G | The A allele is a major driver of **Blonde** hair frequency. AA \+ *SLC45A2* GG \= High probability of **Platinum/Ash Blonde**.8 |
| **rs12203592** | *IRF4* | **T** \> C | A distinct marker where the T allele is associated with **Darker Hair** but **Lighter Skin** (creating high contrast phenotypes).20 |

**Generative AI Prompting Strategy:**

* **Red:** "Fiery red hair, pale complexion, freckles."  
* **Blonde:** Differentiate based on *TYRP1*. If *TYRP1* alleles are light, prompt "Golden Blonde." If *KITLG* is the driver, prompt "Ash Blonde."  
* **Brown/Black:** If *SLC45A2* is CC, prompt "Deep dark brown to black hair."

### ---

**3.3. Skin Pigmentation and Phototype**

Skin prediction utilizes the Fitzpatrick Scale (Type I-VI). The HIrisPlex-S model integrates global ancestry markers to refine this prediction.22

#### **3.3.1. The Global Melanin Drivers**

Two genes explain a vast majority of the variation in skin reflectance between populations.

1. **rs1426654 (*SLC24A5*):** The "Golden" mutation.  
   * **Alleles:** A (Ala111Thr \- Light) vs. G (Ancestral \- Dark).  
   * **Context:** The A allele is nearly fixed (100% frequency) in European populations. The G allele is dominant in Sub-Saharan African and East Asian populations.23  
   * **Logic:** GG genotype sets the base phenotype to **Fitzpatrick V-VI** (Dark/Black). AA sets the base to **Fitzpatrick I-III** (White/Intermediate).  
2. **rs16891982 (*SLC45A2*):** The Phe374Leu variant.  
   * **Alleles:** G (Light) vs. C (Dark).  
   * **Context:** This SNP differentiates European light skin from East Asian light skin (convergent evolution). East Asians typically carry the ancestral C (Dark) allele here, despite having light skin due to other mechanisms, whereas Europeans carry G.19  
   * **Logic:** AA at *SLC24A5* \+ GG at *SLC45A2* \= **Fitzpatrick I-II (Very Pale/Pale)**.

#### **3.3.2. Undertone and Freckling (The Texture)**

* **Undertone:** If *MC1R* variants are present (even single copies), the skin tone should be described as **"Pink" or "Rosy" undertones**. If *OCA2* and *SLC24A5* are light but *MC1R* is wild-type, the undertone is **"Neutral" or "Cream"**.  
* **Freckling:** The *IRF4* rs12203592 T allele and *MC1R* variants are strong predictors of ephelides (freckles) and solar lentigines.  
  * **Agent Logic:** If rs12203592 is TT or *MC1R* score ![][image4], set Freckles \= True.  
  * **Prompt Keyword:** "Dusting of freckles across the nose and cheeks," "High detailed skin texture with visible pores and freckles".21

## ---

**4\. Craniofacial and Anthropometric Morphology**

This domain moves beyond color to the *structure* of the face and body. While less deterministic than pigmentation, GWAS summary statistics provide high-confidence associations for specific features.29

### **4.1. Nasal Morphology**

Nose shape is highly heritable and polygenic, but four genes show signals strong enough for inclusion in the report.

| rsID | Gene | Alleles | Phenotypic Descriptor for Prompt |
| :---- | :---- | :---- | :---- |
| **rs11175967** | *PAX3* | **A** (Derived) | Associated with the **Nasal Bridge**. The A allele correlates with a higher, more prominent nasal root (nasion). G correlates with a lower/flatter root.29 **Prompt:** "High, prominent nasal bridge" vs "Low nasal root." |
| **rs3827760** | *EDAR* | **G** (Derived) | The V370A variant. While primarily a hair/tooth trait, it is associated with a specific facial flatness and reduced nasal prominence common in East Asian populations.34 **Prompt:** "Button nose" or "Less prominent nasal bridge." |
| **rs6184** | *GHR* | **A** vs C | Growth Hormone Receptor. The A allele influences nasal width and overall facial projection.35 |
| **rs11170678** | *DCHS2* | \-- | Influences "columella inclination" (nose tip). Variants here determine if the nose is "turned up" (celestial) or "hooked" (aquiline).30 |

**Logic for Agent:**

If *PAX3* is AA and *DCHS2* variants suggest pointedness: **Prompt \= "Aristocratic, aquiline nose structure."**

If *EDAR* is GG: **Prompt \= "Softer, less prominent nose bridge."**

### **4.2. Mandibular and Chin Structure**

The jawline is a critical component of the "statue" aspect of the generated image.

* **Prognathism (Lantern Jaw):** The *GHR* gene (Growth Hormone Receptor) variant **rs6184** is statistically associated with mandibular prognathism.  
  * **Risk Allele:** A (associated with Class III malocclusion/prognathism).  
  * **Normal Allele:** C.36  
  * **Prompt:** If AA, add "Strong, prominent chin" or "Defined jawline."  
* **Cleft Chin:** The "dimple" in the chin is a heritable trait linked to markers near *rs2013162*.  
  * **Logic:** If risk alleles are present, set Cleft\_Chin \= True.  
  * **Prompt:** "Distinctive cleft chin.".39

### **4.3. Earlobe Attachment**

The "Free" vs. "Attached" earlobe trait is governed by the *GPR126* gene on chromosome 6\.

* **Marker:** **rs2080401** (or linked SNPs).  
* **Genotype:**  
  * C allele is associated with **Free/Detached** lobes (Dominant-like effect).  
  * T allele is associated with **Attached** lobes (Recessive-like effect).  
* **Prompt:** "Detached earlobes" or "Attached earlobes" (Relevant for side-profile generation).40

### **4.4. Body Morphology: Height and Weight**

The user explicitly requested "height, weight" and "overall statue". While environment plays a huge role, *FTO* and *HMGA2* provide genetic baselines.

* **Adiposity (Weight/BMI):** The *FTO* gene (Fat Mass and Obesity-associated) is the strongest genetic signal for BMI.  
  * **Marker:** **rs9939609**.  
  * **Alleles:** A (Risk) vs. T (Normal).  
  * **Effect:** AA homozygotes weigh, on average, 3 kg more and have a 1.7x increased risk of obesity compared to TT.43  
  * **Prompt Nuance:** If AA, avoid keywords like "gaunt" or "skinny." Use "Robust build" or "Heavier set." If TT, use "Slender build" or "Lean physique."  
* **Stature (Height):** Height is highly polygenic (thousands of SNPs). However, *HMGA2* (rs1042725) is a known effect size leader.  
  * **Logic:** While a precise height cannot be predicted from a few SNPs, the agent can calculate a "polygenic score" if the 23andMe file allows, or use *HMGA2* as a proxy.  
  * **Prompt:** "Tall stature" vs "Average height."

## ---

**5\. Dermatological and Integumentary Traits**

These "texture" traits add significant realism to the AI-generated image.

### **5.1. Hair Texture (Trichohyalin)**

Hair curliness is determined by the shape of the follicle and the protein structure of the hair shaft.

* **Primary Marker:** **rs11803731** in the *TCHH* (Trichohyalin) gene.  
  * **Alleles:** T (Straight) vs. A (Curly).  
  * **Mechanism:** *TCHH* cross-links keratin filaments in the inner root sheath. The A variant alters this structure.  
  * **Effect:** TT \= Straight. AT \= Wavy. AA \= Curly.46  
* **Asian Specific Marker:** **rs3827760** (*EDAR*).  
  * **Effect:** G allele creates thick, coarse, straight hair fibers (circular cross-section).

**Prompt Logic:**

* EDAR(GG) \-\> "Thick, straight hair."  
* TCHH(AA) \-\> "Curly, textured hair."  
* TCHH(AT) \-\> "Wavy hair."

### **5.2. Male Pattern Baldness (Androgenetic Alopecia)**

This is a sex-dependent trait. The agent must check the user's sex (XX vs XY) before applying this logic.

* **X-Chromosome Marker:** **rs6152** in the *AR* (Androgen Receptor) gene.  
  * **Risk Allele:** G. Increases receptor sensitivity to Dihydrotestosterone (DHT).50  
* **Autosomal Marker:** **rs1160312** (Chr 20p11).  
  * **Risk Allele:** A. Men with AA have a 1.6x increased risk. Combined with the *AR* risk allele, the risk increases 7-fold.51

**Age-Dependent Prompting:**

The prompt must be adjusted based on the input Age.

* **Age \< 25:** Ignore balding risk in prompt (or "widow's peak").  
* **Age 30-50 (High Risk):** "Receding hairline," "Thinning hair."  
* **Age 50+ (High Risk):** "Male pattern baldness," "Bald pate with side fringe."

### **5.3. Premature Graying (Canities)**

* **Marker:** **rs12203592** in *IRF4*.  
* **Alleles:** T (Graying Risk) vs. C.  
* **Effect:** The T allele serves a dual role: it darkens hair color during youth but accelerates the depletion of melanocyte stem cells, leading to graying. 50% of carriers are gray by age 50\.20  
* **Prompt Logic:** If Age \> 35 and Genotype \= TT, append "Salt and pepper hair" or "Silvering temples."

## ---

**6\. Ocular Refraction and Pathology (Non-Benign Traits)**

The user specifically requested analysis of vision defects (myopia, hyperopia) and diseases. These traits affect the visual representation (e.g., glasses) and provide critical health insights.

### **6.1. Myopia vs. Hyperopia (Refractive Error)**

Refractive error is determined by the axial length of the eye.

* **Myopia (Nearsightedness):**  
  * **Gene:** *GJD2* (Connexin-36) and *RASGRF1*.  
  * **Marker:** **rs524952** (*GJD2*). A allele is the risk factor for Myopia. T allele is protective (Hyperopia direction).54  
  * **Marker:** **rs8027411** (*RASGRF1*). T allele is associated with high myopia.56  
* **Hyperopia (Farsightedness):**  
  * **Logic:** Individuals homozygous for the protective alleles at these loci (TT at *GJD2*, GG at *RASGRF1*) have a shorter axial length, predisposing them to hyperopia.56  
* **Astigmatism:**  
  * Linked to *PDGFRA* variants (though less deterministic in 23andMe data).

**Prompt Integration:**

* High Myopia Risk: "Wearing modern prescription glasses" or "Myopic squint."  
* Hyperopia Risk: "Reading glasses" (if Age \> 40).

### **6.2. Age-Related Macular Degeneration (AMD)**

AMD is a leading cause of blindness. While not visible on the face, it is a critical "non-benign" trait for the report.

* **Marker:** **rs1061170** in *CFH* (Complement Factor H).  
  * **Alleles:** C (Risk \- His402) vs. T (Protective \- Tyr402).  
  * **Mechanism:** The C allele alters the binding of Factor H to C-reactive protein and heparin, leading to uncontrolled complement activation and inflammation in the retina (Drusen formation).59  
  * **Risk:** Homozygous CC carriers have a 7.4x increased risk of AMD compared to TT.  
* **Marker:** **rs10490924** in *ARMS2*.  
  * **Risk Allele:** T. Strong independent risk factor.62

**Report Output:**

"Non-Benign Finding: You carry the high-risk C allele at rs1061170 (CFH). This variant significantly reduces the eye's ability to suppress inflammation, predisposing you to Age-Related Macular Degeneration. Regular retinal exams are recommended."

### **6.3. Glaucoma Risk**

* **Marker:** **rs4656461** near *TMCO1*.  
* **Alleles:** G (Risk). Associated with elevated intraocular pressure (IOP) and Primary Open-Angle Glaucoma (POAG).63

## ---

**7\. Generative AI Integration Layer**

This section defines how the coding agent translates the derived phenotypes into a structured API call for image generation.

### **7.1. Prompt Construction Architecture**

The prompt is constructed as a concatenated string of **Tokens**. Each token represents a phenotype derived from the analysis above, weighted by the confidence of the genetic prediction.

**Base Template:**

", \[Pigmentation\], \[Morphology\],,"

### **7.2. Dynamic Token Dictionary**

The agent must map the genetic output to these specific visual tokens:

| Trait | Genetic Output | Visual Token for Prompt | Weighting |
| :---- | :---- | :---- | :---- |
| **Skin** | *SLC24A5*(AA) \+ *MC1R*(Risk) | pale skin, rosy undertone, scattered freckles | (freckles:1.3) |
| **Skin** | *SLC45A2*(CC) | olive skin tone, warm undertone | 1.0 |
| **Eyes** | *HERC2*(GG) \+ *SLC24A4*(TT) | piercing blue eyes, limbal ring | (blue eyes:1.2) |
| **Eyes** | *HERC2*(AG) \+ *OCA2*(AA) | hazel green eyes, heterochromia | 1.1 |
| **Hair** | *MC1R*(Risk) | natural red hair, ginger, copper tones | 1.4 |
| **Texture** | *TCHH*(AA) | curly hair, textured coils | 1.2 |
| **Nose** | *PAX3*(AA) | aquiline nose, high bridge | 1.0 |
| **Chin** | *GHR*(AA) | strong jawline, prominent chin | 1.1 |
| **Weight** | *FTO*(AA) | robust build, heavy set | 1.1 |
| **Vision** | *GJD2*(AA) | wearing glasses, spectacles | 1.0 |

### **7.3. Stylistic Modifiers (The "Photorealistic" Wrapper)**

To ensure the output looks like a person and not a cartoon, the agent must append technical photography keywords.

* **Keywords:** 8k resolution, raw photo, hyperrealistic, highly detailed skin texture, subsurface scattering, shot on 85mm lens, f/1.8 aperture, cinematic lighting, global illumination.  
* **Negative Prompt:** cartoon, anime, drawing, illustration, 3d render, plastic, deformed, blur, bad anatomy, bad eyes, crossed eyes.

### **7.4. Python Implementation Logic (Pseudocode)**

Python

def generate\_sdxl\_prompt(genotype\_results, user\_age, user\_sex):  
    \# Base Subject  
    prompt \= f"hyperrealistic portrait of a {user\_age} year old {user\_sex}, "  
      
    \# 1\. Pigmentation Integration  
    if genotype\_results\['eye\_color'\] \== 'Blue':  
        prompt \+= "(piercing blue eyes:1.2), "  
    elif genotype\_results\['eye\_color'\] \== 'Hazel':  
        prompt \+= "(hazel green eyes:1.1), "  
      
    \# 2\. Hair Logic (Texture \+ Color \+ Graying \+ Balding)  
    hair\_string \= f"{genotype\_results\['hair\_texture'\]} {genotype\_results\['hair\_color'\]} hair, "  
      
    \# Premature Graying Check  
    if user\_age \> 35 and genotype\_results\['graying\_risk'\]:  
        hair\_string \= f"salt and pepper {genotype\_results\['hair\_texture'\]} hair, silvering temples, "  
          
    \# Balding Check (Male only)  
    if user\_sex \== 'Male' and genotype\_results\['balding\_risk'\] and user\_age \> 40:  
        hair\_string \= "receding hairline, thinning hair, "  
          
    prompt \+= hair\_string  
      
    \# 3\. Skin Details  
    prompt \+= f"{genotype\_results\['skin\_tone'\]} skin, highly detailed skin texture, pores, "  
    if genotype\_results\['freckles'\]:  
        prompt \+= "(visible freckles on nose and cheeks:1.3), "  
          
    \# 4\. Morphology  
    if genotype\_results\['nose\_shape'\] \== 'High\_Bridge':  
        prompt \+= "aquiline nose, "  
    if genotype\_results\['chin\_shape'\] \== 'Cleft':  
        prompt \+= "cleft chin, "  
    if genotype\_results\['bmi\_pred'\] \== 'High':  
        prompt \+= "robust build, full face, "  
    elif genotype\_results\['bmi\_pred'\] \== 'Low':  
        prompt \+= "gaunt features, slender build, "

    \# 5\. Ocular Accessories  
    if genotype\_results\['myopia\_risk'\] \== 'High':  
         prompt \+= "wearing prescription glasses, "

    \# 6\. Style Wrapper  
    prompt \+= "shot on Sony A7R IV, 85mm lens, f/1.8, soft studio lighting, sharp focus on eyes, 8k uhd"  
      
    return prompt

## ---

**8\. Technical Implementation Details for the Coding Agent**

### **8.1. Data Dictionary Structure**

The agent should load the master SNP list into a dictionary for O(1) access.

JSON

{  
  "rs12913832": {"gene": "HERC2", "risk": "G", "type": "Pigmentation"},  
  "rs9939609":  {"gene": "FTO",   "risk": "A", "type": "Body"},  
  "rs524952":   {"gene": "GJD2",  "risk": "A", "type": "Vision"},  
  "rs11803731": {"gene": "TCHH",  "risk": "A", "type": "Texture"}  
}

### **8.2. Error Handling and Imputation**

* **Missing Data:** If a primary driver (e.g., *HERC2*) is missing, the system must fallback to a "Neutral" prompt or ask the user for manual input (e.g., "Eye color not found in DNA, please specify").  
* **Confidence Scores:** The report should output a confidence score alongside the prediction (e.g., "Eye Color: Blue (Confidence: High \- Homozgyous GG detected)").

## ---

**9\. Conclusion and Future Outlook**

This technical specification provides a complete roadmap for transforming raw 23andMe data into a visual and textual phenotype report. By integrating the forensic precision of **HIrisPlex-S** with the generative capabilities of **Stable Diffusion**, the analyze-your-dna project can evolve from a simple data parser into a sophisticated "Digital DNA Mirror."

While current genetic models can predict pigmentation with \>90% accuracy, craniofacial morphology remains probabilistic due to its polygenic nature. However, as GWAS sample sizes grow (e.g., GIANT consortium data), the "polygenic scores" for height and facial structure will become increasingly deterministic, allowing for even higher fidelity in the generative output.

### **Appendix: Master SNP Lookup Table**

| Phenotype Domain | Gene | rsID | Alleles (Effect / Ref) | Prediction / Prompt Token |
| :---- | :---- | :---- | :---- | :---- |
| **Eye Color** | *HERC2* | rs12913832 | G / A | G=Blue, A=Brown |
| **Eye Color** | *OCA2* | rs1800407 | A / G | A=Light, G=Dark |
| **Hair Color** | *MC1R* | rs1805007 | T / C | T=Red |
| **Hair Color** | *SLC45A2* | rs16891982 | G / C | G=Blonde, C=Dark |
| **Hair Texture** | *TCHH* | rs11803731 | A / T | A=Curly, T=Straight |
| **Skin Tone** | *SLC24A5* | rs1426654 | A / G | A=Pale, G=Dark |
| **Freckles** | *IRF4* | rs12203592 | T / C | T=Freckles, C=Clear |
| **Balding** | *AR* | rs6152 | G / A | G=High Risk |
| **Graying** | *IRF4* | rs12203592 | T / C | T=Premature Graying |
| **Weight (BMI)** | *FTO* | rs9939609 | A / T | A=High BMI Risk |
| **Chin** | *GHR* | rs6184 | A / C | A=Prognathism (Prominent) |
| **Nose** | *PAX3* | rs11175967 | A / G | A=High/Prominent Bridge |
| **Earlobes** | *GPR126* | rs2080401 | C / T | C=Free, T=Attached |
| **Myopia** | *GJD2* | rs524952 | A / T | A=Nearsighted |
| **AMD** | *CFH* | rs1061170 | C / T | C=High Risk (Macular Degeneration) |

*(End of Report)*

#### **Works cited**

1. Raw Genotype Data Technical Details \- 23andMe Customer Care, accessed February 2, 2026, [https://eu.customercare.23andme.com/hc/en-us/articles/115002090907-Raw-Genotype-Data-Technical-Details](https://eu.customercare.23andme.com/hc/en-us/articles/115002090907-Raw-Genotype-Data-Technical-Details)  
2. Navigating Your Raw Data \- 23andMe Customer Care, accessed February 2, 2026, [https://customercare.23andme.com/hc/en-us/articles/115004310067-Navigating-Your-Raw-Data](https://customercare.23andme.com/hc/en-us/articles/115004310067-Navigating-Your-Raw-Data)  
3. genotype in downloaded raw data : r/23andme \- Reddit, accessed February 2, 2026, [https://www.reddit.com/r/23andme/comments/1kmv1qa/genotype\_in\_downloaded\_raw\_data/](https://www.reddit.com/r/23andme/comments/1kmv1qa/genotype_in_downloaded_raw_data/)  
4. How 23andMe Reports Genotypes, accessed February 2, 2026, [https://customercare.23andme.com/hc/en-us/articles/212883677-How-23andMe-Reports-Genotypes](https://customercare.23andme.com/hc/en-us/articles/212883677-How-23andMe-Reports-Genotypes)  
5. HIrisPlex-S: Tools & Pipelines \- Walsh FDP Lab \- Indiana University, accessed February 2, 2026, [https://walshlab.indianapolis.iu.edu/tools/hps.html](https://walshlab.indianapolis.iu.edu/tools/hps.html)  
6. HIRISPLEX-S, HIRISPLEX & IRISPLEX Eye, Hair and Skin colour DNA Phenotyping webtool USER MANUAL \- Erasmus MC, accessed February 2, 2026, [https://hirisplex.erasmusmc.nl/pdf/hirisplex.erasmusmc.nl.pdf](https://hirisplex.erasmusmc.nl/pdf/hirisplex.erasmusmc.nl.pdf)  
7. The HIrisPlex-S system for eye, hair and skin colour prediction from DNA: Introduction and forensic developmental validation | National Institute of Justice, accessed February 2, 2026, [https://nij.ojp.gov/library/publications/hirisplex-s-systemffor-eye-hair-and-skin-color-prediction-dna-introduction-and](https://nij.ojp.gov/library/publications/hirisplex-s-systemffor-eye-hair-and-skin-color-prediction-dna-introduction-and)  
8. HIrisPlex-S Eye, Hair and Skin Colour DNA Phenotyping Webtool, accessed February 2, 2026, [https://hirisplex.erasmusmc.nl/](https://hirisplex.erasmusmc.nl/)  
9. Prognostic capacity of the hIrisPlex genetic phenotyping system in the belarusian population \- Eco-Vector Journals Portal, accessed February 2, 2026, [https://journals.eco-vector.com/ecolgenet/article/download/54547/57373](https://journals.eco-vector.com/ecolgenet/article/download/54547/57373)  
10. The HIrisPlex-S system for eye, hair and skin colour prediction from DNA: Introduction and forensic developmental validation \- PubMed, accessed February 2, 2026, [https://pubmed.ncbi.nlm.nih.gov/29753263/](https://pubmed.ncbi.nlm.nih.gov/29753263/)  
11. Association between brown eye colour in rs12913832:GG individuals and SNPs in TYR, TYRP1, and SLC24A4 \- PMC \- NIH, accessed February 2, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC7485777/](https://pmc.ncbi.nlm.nih.gov/articles/PMC7485777/)  
12. Eye Color Genetics \- 23andMe, accessed February 2, 2026, [https://www.23andme.com/topics/traits/eye-color/](https://www.23andme.com/topics/traits/eye-color/)  
13. Blue eye color in humans may be caused by a perfectly associated founder mutation in a regulatory element located within the HERC2 gene inhibiting OCA2 expression \- PubMed, accessed February 2, 2026, [https://pubmed.ncbi.nlm.nih.gov/18172690/](https://pubmed.ncbi.nlm.nih.gov/18172690/)  
14. Association between Variants in the OCA2-HERC2 Region and Blue Eye Colour in HERC2 rs12913832 AA and AG Individuals \- MDPI, accessed February 2, 2026, [https://www.mdpi.com/2073-4425/14/3/698](https://www.mdpi.com/2073-4425/14/3/698)  
15. A global view of the OCA2-HERC2 region and pigmentation \- PMC \- PubMed Central, accessed February 2, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC3325407/](https://pmc.ncbi.nlm.nih.gov/articles/PMC3325407/)  
16. A Genome-Wide Association Study Identifies Novel Alleles Associated with Hair Color and Skin Pigmentation \- NIH, accessed February 2, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC2367449/](https://pmc.ncbi.nlm.nih.gov/articles/PMC2367449/)  
17. SLC45A2 solute carrier family 45 member 2 \[ (human)\] \- NCBI, accessed February 2, 2026, [https://www.ncbi.nlm.nih.gov/gene/51151](https://www.ncbi.nlm.nih.gov/gene/51151)  
18. Why did 23andMe get my eye color wrong? \- The Tech Interactive, accessed February 2, 2026, [https://www.thetech.org/ask-a-geneticist/articles/2016/genetics-does-not-match-eye-color/](https://www.thetech.org/ask-a-geneticist/articles/2016/genetics-does-not-match-eye-color/)  
19. Light skin \- Wikipedia, accessed February 2, 2026, [https://en.wikipedia.org/wiki/Light\_skin](https://en.wikipedia.org/wiki/Light_skin)  
20. Interferon Regulatory Factors 4 (IRF4) Gene and Hair Graying | 2021, Volume 2 \- Issue 2, accessed February 2, 2026, [https://jebms.org/full-text/51](https://jebms.org/full-text/51)  
21. A polymorphism in IRF4 affects human pigmentation through a tyrosinase-dependent MITF/TFAP2A pathway \- NIH, accessed February 2, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC3873608/](https://pmc.ncbi.nlm.nih.gov/articles/PMC3873608/)  
22. The HIrisPlex-S system for eye, hair and skin colour prediction from DNA \- IU Indianapolis ScholarWorks, accessed February 2, 2026, [https://scholarworks.indianapolis.iu.edu/bitstream/1805/15921/1/Chaitanya\_2018\_HIrisPlex.pdf](https://scholarworks.indianapolis.iu.edu/bitstream/1805/15921/1/Chaitanya_2018_HIrisPlex.pdf)  
23. Skin Pigmentation: Skin color Genetics and More \- 23andMe, accessed February 2, 2026, [https://www.23andme.com/topics/traits/skin-pigmentation/](https://www.23andme.com/topics/traits/skin-pigmentation/)  
24. The Light Skin Allele of SLC24A5 in South Asians and Europeans Shares Identity by Descent \- PMC \- PubMed Central, accessed February 2, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC3820762/](https://pmc.ncbi.nlm.nih.gov/articles/PMC3820762/)  
25. Distribution of allele A of the SLC24A5 gene, an allele responsible for fair skin in most Europeans \[1000x737\] : r/MapPorn \- Reddit, accessed February 2, 2026, [https://www.reddit.com/r/MapPorn/comments/afjgy4/distribution\_of\_allele\_a\_of\_the\_slc24a5\_gene\_an/](https://www.reddit.com/r/MapPorn/comments/afjgy4/distribution_of_allele_a_of_the_slc24a5_gene_an/)  
26. What skintone category do I fit into? : r/23andme \- Reddit, accessed February 2, 2026, [https://www.reddit.com/r/23andme/comments/1n05lbu/what\_skintone\_category\_do\_i\_fit\_into/](https://www.reddit.com/r/23andme/comments/1n05lbu/what_skintone_category_do_i_fit_into/)  
27. Haplotypes from the SLC45A2 gene are associated with the presence of freckles and eye, hair and skin pigmentation in Brazil, accessed February 2, 2026, [https://repositorio.unesp.br/bitstreams/c48946f8-9faa-4553-ba48-c5b5c077d314/download](https://repositorio.unesp.br/bitstreams/c48946f8-9faa-4553-ba48-c5b5c077d314/download)  
28. Association of Interferon Regulatory Factor-4 Polymorphism rs12203592 With Divergent Melanoma Pathways \- PMC \- PubMed Central, accessed February 2, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC4948568/](https://pmc.ncbi.nlm.nih.gov/articles/PMC4948568/)  
29. Hunting for genes that shape human faces: initial successes and challenges for the future, accessed February 2, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC6550302/](https://pmc.ncbi.nlm.nih.gov/articles/PMC6550302/)  
30. Genes for nose shape found | UCL News, accessed February 2, 2026, [https://www.ucl.ac.uk/news/2016/may/genes-nose-shape-found](https://www.ucl.ac.uk/news/2016/may/genes-nose-shape-found)  
31. Scientists sniff out genes controlling human nose shapes | Genetics \- The Guardian, accessed February 2, 2026, [https://www.theguardian.com/science/2016/may/19/scientists-sniff-out-genes-controlling-human-nose-shapes](https://www.theguardian.com/science/2016/may/19/scientists-sniff-out-genes-controlling-human-nose-shapes)  
32. Insights into the genetic architecture of the human face \- PMC \- NIH, accessed February 2, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC7796995/](https://pmc.ncbi.nlm.nih.gov/articles/PMC7796995/)  
33. A Genome-Wide Association Study Identifies Five Loci Influencing Facial Morphology in Europeans \- NIH, accessed February 2, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC3441666/](https://pmc.ncbi.nlm.nih.gov/articles/PMC3441666/)  
34. Genome-wide Variants of Eurasian Facial Shape Differentiation and DNA based Face Prediction | bioRxiv, accessed February 2, 2026, [https://www.biorxiv.org/content/10.1101/062950v4.full-text](https://www.biorxiv.org/content/10.1101/062950v4.full-text)  
35. Association of Growth Hormone Receptor Gene Polymorphisms (rs6180, rs6182, rs6184) with Skeletal Class III Malocclusion and Prognathic Mandibles in the Deutero-Malay Race \- PMC \- NIH, accessed February 2, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC12182412/](https://pmc.ncbi.nlm.nih.gov/articles/PMC12182412/)  
36. (PDF) Association of Growth Hormone Receptor Gene Polymorphisms (rs6180, rs6182, rs6184) with Skeletal Class III Malocclusion and Prognathic Mandibles in the Deutero-Malay Race \- ResearchGate, accessed February 2, 2026, [https://www.researchgate.net/publication/391389983\_Association\_of\_Growth\_Hormone\_Receptor\_Gene\_Polymorphisms\_rs6180\_rs6182\_rs6184\_with\_Skeletal\_Class\_III\_Malocclusion\_and\_Prognathic\_Mandibles\_in\_the\_Deutero-Malay\_Race](https://www.researchgate.net/publication/391389983_Association_of_Growth_Hormone_Receptor_Gene_Polymorphisms_rs6180_rs6182_rs6184_with_Skeletal_Class_III_Malocclusion_and_Prognathic_Mandibles_in_the_Deutero-Malay_Race)  
37. Growth hormone receptor gene variant and three-dimensional mandibular morphology \- NIH, accessed February 2, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC8388580/](https://pmc.ncbi.nlm.nih.gov/articles/PMC8388580/)  
38. Association analysis between rs6184 and rs6180 polymorphisms of growth hormone receptor gene regarding skeletal-facial profile in a Colombian population | European Journal of Orthodontics | Oxford Academic, accessed February 2, 2026, [https://academic.oup.com/ejo/article/40/4/378/4558706](https://academic.oup.com/ejo/article/40/4/378/4558706)  
39. Association between IRF6 SNPs and Oral Clefts in West China \- PMC, accessed February 2, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC2901597/](https://pmc.ncbi.nlm.nih.gov/articles/PMC2901597/)  
40. SNP markers included in the Ear-Plex system for ear morphology... \- ResearchGate, accessed February 2, 2026, [https://www.researchgate.net/figure/SNP-markers-included-in-the-Ear-Plex-system-for-ear-morphology-prediction-ordered\_tbl1\_365588415](https://www.researchgate.net/figure/SNP-markers-included-in-the-Ear-Plex-system-for-ear-morphology-prediction-ordered_tbl1_365588415)  
41. SINGLE NUCLEOTIDE POLYMORPHISMS AND THEIR ROLE IN PREDICTING EARLOBE ATTACHMENT FOR FORENSIC IDENTIFICATION \- PJOSR, accessed February 2, 2026, [https://pjosr.com/index.php/pjs/article/download/1462/1202/4963](https://pjosr.com/index.php/pjs/article/download/1462/1202/4963)  
42. Genetics of Earlobes \- News-Medical, accessed February 2, 2026, [https://www.news-medical.net/health/Genetics-of-Earlobes.aspx](https://www.news-medical.net/health/Genetics-of-Earlobes.aspx)  
43. Minor alleles in the FTO SNPs contributed to the increased risk of obesity among Korean adults: meta-analysis from nationwide big data-based studies \- PMC \- NIH, accessed February 2, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC9884590/](https://pmc.ncbi.nlm.nih.gov/articles/PMC9884590/)  
44. Effects of the FTO Gene on Lifestyle Intervention Studies in Children \- PMC, accessed February 2, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC6515795/](https://pmc.ncbi.nlm.nih.gov/articles/PMC6515795/)  
45. The FTO gene rs9939609 obesity-risk allele and loss of control over eating1 \- PMC \- NIH, accessed February 2, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC2777464/](https://pmc.ncbi.nlm.nih.gov/articles/PMC2777464/)  
46. Meta-analysis of genome-wide association studies identifies 8 novel loci involved in shape variation of human head hair \- PMC \- PubMed Central, accessed February 2, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC5886212/](https://pmc.ncbi.nlm.nih.gov/articles/PMC5886212/)  
47. Common Variants in the Trichohyalin Gene Are Associated with Straight Hair in Europeans, accessed February 2, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC2775823/](https://pmc.ncbi.nlm.nih.gov/articles/PMC2775823/)  
48. Evaluation of the predictive capacity of DNA variants associated with straight hair in Europeans \- PubMed, accessed February 2, 2026, [https://pubmed.ncbi.nlm.nih.gov/26414620/](https://pubmed.ncbi.nlm.nih.gov/26414620/)  
49. rs11803731 SNP \- SelfDecode, accessed February 2, 2026, [https://selfdecode.com/en/snp/rs11803731/](https://selfdecode.com/en/snp/rs11803731/)  
50. SNP: rs1160312 \- Infinome, accessed February 2, 2026, [https://www.infino.me/snp/rs1160312/](https://www.infino.me/snp/rs1160312/)  
51. rs1160312 \- SNPedia, accessed February 2, 2026, [https://bots.snpedia.com/index.php/Rs1160312](https://bots.snpedia.com/index.php/Rs1160312)  
52. Male-pattern baldness susceptibility locus at 20p11 \- PMC \- NIH, accessed February 2, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC2672151/](https://pmc.ncbi.nlm.nih.gov/articles/PMC2672151/)  
53. Exploring the possibility of predicting human head hair greying from DNA using whole-exome and targeted NGS data \- PMC \- PubMed Central, accessed February 2, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC7430834/](https://pmc.ncbi.nlm.nih.gov/articles/PMC7430834/)  
54. Phenotypic Consequences of the GJD2 Risk Genotype in Myopia Development | IOVS, accessed February 2, 2026, [https://iovs.arvojournals.org/article.aspx?articleid=2776610](https://iovs.arvojournals.org/article.aspx?articleid=2776610)  
55. Phenotypic Consequences of the GJD2 Risk Genotype in Myopia Development \- PMC \- NIH, accessed February 2, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC8375003/](https://pmc.ncbi.nlm.nih.gov/articles/PMC8375003/)  
56. Frequency of GJD2 and RASGRF1 genotypes and allele (%) | Download Table \- ResearchGate, accessed February 2, 2026, [https://www.researchgate.net/figure/Frequency-of-GJD2-and-RASGRF1-genotypes-and-allele\_tbl2\_325355103](https://www.researchgate.net/figure/Frequency-of-GJD2-and-RASGRF1-genotypes-and-allele_tbl2_325355103)  
57. Polymorphism in the RASGRF1 gene with high myopia: A meta-analysis \- PubMed Central, accessed February 2, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC4645451/](https://pmc.ncbi.nlm.nih.gov/articles/PMC4645451/)  
58. Novel Myopia Genes and Pathways Identified From Syndromic Forms of Myopia \- PMC \- NIH, accessed February 2, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC5773233/](https://pmc.ncbi.nlm.nih.gov/articles/PMC5773233/)  
59. Complement Factor H (Y402H) polymorphism for age-related macular degeneration alters retinal lipids | bioRxiv, accessed February 2, 2026, [https://www.biorxiv.org/content/10.64898/2026.01.06.697989v1.full-text](https://www.biorxiv.org/content/10.64898/2026.01.06.697989v1.full-text)  
60. Complement factor H genotypes impact risk of age-related macular degeneration by interaction with oxidized phospholipids \- NIH, accessed February 2, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC3427125/](https://pmc.ncbi.nlm.nih.gov/articles/PMC3427125/)  
61. Association of complement factor H Y402H polymorphism with phenotype of neovascular age related macular degeneration in Israel \- PMC \- NIH, accessed February 2, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC2566586/](https://pmc.ncbi.nlm.nih.gov/articles/PMC2566586/)  
62. Genetic Determinants of Age-Related Macular Degeneration in Diverse Populations From the PAGE Study | IOVS, accessed February 2, 2026, [https://iovs.arvojournals.org/article.aspx?articleid=2212605](https://iovs.arvojournals.org/article.aspx?articleid=2212605)  
63. Association of Genetic Variants in the TMCO1 Gene with Clinical Parameters Related to Glaucoma and Characterization of the Protein in the Eye | IOVS, accessed February 2, 2026, [https://iovs.arvojournals.org/article.aspx?articleid=2168271](https://iovs.arvojournals.org/article.aspx?articleid=2168271)  
64. Glaucoma Risk Alleles in the Ocular Hypertension Treatment Study (OHTS) \- PMC, accessed February 2, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC5121091/](https://pmc.ncbi.nlm.nih.gov/articles/PMC5121091/)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADsAAAAYCAYAAABEHYUrAAACC0lEQVR4Xu2WTUgVURTHT9GnBmKiZfixkDBK3QiCBvkWlbQKQkFc1C7QjYnUJhFBV4kLoWVaoIgbN+ImNMoWrSKDaJXQIlcuJIqKkND/6cww9503zb1306O4P/jBe/8zM9w7M/fcIQoEAoF/nBtwW4dFZhruwe/wDVyP/rNf4Av41jjm0O+zLFTATZKTjqtasTgCP8FueDjKjsGv8GN8UMRtkpvhxB34hGSyZ/NLTrTDWh0atMBGHVq4CkdUliMZ4yOVn4cLKkvlOskEH5BcqDO/7MQKZU/2EpzQoYUZWKeycZIx9qq8C46qrIBykteEGab0C9lohfM6TOEpPKHDDJp0AF6SjJGXnUkVrFZZAf3wQPT7JsmFhpKylTK4DM/oQgrN8DEl68+XUviLPNamyRXKv3vXSCbLr7MLDfAZvKALGXTA5yQT9yUe35Qu2DgJtyhp46ZzxnF/4hz8DHfgqqfcTddIlpAPkyTj40l78RCeUhk3A74YD8iF+Mn26UIGg3BAh45swJ/wqC5kwd2XtxoNrwme7HtdyOAgScu/qAsp9MD7OnSEGxCPjd8IZ3iL+QBLdCHiG8lr5sNpctvjlihphr7cIpmsdXth2uBrkm4WPz3+QokZo6Sts6/gXaNuYxbW69AgB+/p0MJlStb5D5Jx7cJ3cNE47q9TAyt1aMAfHHpvDAQCgcB/yz5SFWmENWIi+QAAAABJRU5ErkJggg==>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAD0AAAAYCAYAAABJA/VsAAACSElEQVR4Xu2WTYhPURjGH9+fyUxDNrKbDYpSPprMZEEWhKJMkVjY+MjCApmFlYXQxEIKESsiIV81kyYKRVlYkKYkWVqglHge7zWOd+499/yb0sT51a/+vc+993/OPV8XyGQymX+UWbSL9tA39BF9QbcW+RHaXvweLkyi2+lN+oo+pc/pMTqKrqP7Bq52HKSf6UO6go4r6rrxEH1S5OOL+nBgNX1L38MGpinIVsJewDdUDNQZ+p3u9EHBaNjDb/mghrV0jC8GrMLvl9so6qTafINOcdkvLtGPKGnDLtjNmtYxbtM9vhhBndGsGeGDgAN0uS8msIB+pXdR0qGA/fSqL06HvQmthdjN4jBt9cUIu2FrLcY0es0XE+iDTdvZPnB00vW+eBQ2yo2MYApqzGXYsqhjE93rixHWwNo8aARTeQl7wHwfDAFNV0077aqpaIldoC0+KOEUrM07fJCC1pxu/gLboWNsoDN9sYSNsGe+pvcasBe2RrtRz33Yfyz2ATkHy0J7wgtEPyyY4OohE2ENG+mDCjTSz+gcH1SgF36WLvFBBSdhbW73QcB52DXbULKR6vxVqAO8jGZ6nS7zQQ1T6QP8eW5WcZx2+GKEDlib9V1RhgbpQ+FYl/1kMr1D39GlLmuDHVPzXD0VfThoB48xg57wxQR0vKrjGjRtmuqo0N6kNqs/p4taKdpht8DW1WN6EfbQzRja15emlV7ooOkVoNFa5IuJaPZpw+yHvYBP9ApsWcmFA1f+ZfTnsfN/Luo30Uwmk8n81/wAywdwpZkSeaMAAAAASUVORK5CYII=>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAXCAYAAADUUxW8AAAAqElEQVR4Xu3RrQoCQRSG4fEHFUS2aRSrd2AStphNtgUFRbBbvIDFaDJbDLaFXQ1Gq9Vg9kZ8h0lzWPFgU3zhSR8nzK4x/z6qhxhtOWjrYIMtumJT18Iae4RiUxdgiQQjFP1ZVxUzZBij7M+67NEBD9TF9jJ7FOGGCwb+nF8Fc9yxM+53vq2EKa5YoenP+TWwwAkT4z6Uqj5SDFEQ269m33xWOqLmzr6yJ+jvGdzJzJD+AAAAAElFTkSuQmCC>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB4AAAAXCAYAAAAcP/9qAAABEUlEQVR4Xu3Vv0tCYRSH8ZNGBhFtthmtbUElTUIOzk5tgUERtbcE0haNTa21NLQJakOTuLo2uAWt/QUu9RxeX+I9oPd6bw6ZD3wWv8oZ/CUyb8YqIGsfnFZL2MY1PrETrMP2cYMNO6ToA2284ktGHNY2cYd7bJktTZcScdi3jls84cBsSYp92Lcm7kUNHCITzrGb+LAvh1O0UMNiOEeW+LBPDz6L+9CsmG1ciQ/rwSO8oYtKOEfmD+/aYVT6PTxDH4/ivnJJin1Yf2FO0MMV8uE8cf7wnh18q7jAC47Ffah+I3+4aAethCaqWDBb2uriDpftMK0e8C7uqBqgg/Ofp/zH9D3Wf5E49B9n2b1s3h/oG9XQNbaRlsBpAAAAAElFTkSuQmCC>