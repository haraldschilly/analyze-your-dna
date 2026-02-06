from analyze_dna.generate_portrait_prompt import format_prompt_output, generate_portrait_prompt, get_trait_value


def test_get_trait_value():
    # Test missing SNP
    assert get_trait_value({}, "rs123") is None

    # Test valid SNP from TRAITS_SNPS
    # Example: rs12913832 (HERC2)
    genome = {"rs12913832": "GG"}
    result = get_trait_value(genome, "rs12913832")
    assert result is not None
    assert result["gene"] == "HERC2"
    assert "blue eyes" in result["description"].lower()


def test_generate_portrait_prompt_basic():
    # Use minimal genome
    genome = {
        "rs12913832": "GG",  # Blue eyes
        "rs16891982": "CC",  # Dark hair
        "rs1426654": "GG",  # Fair skin
    }

    prompt = generate_portrait_prompt(genome, birth_year=1990, sex="male")

    assert "blue eyes" in prompt["front_view"]
    assert "35-year-old male" in prompt["subject"] or "36-year-old male" in prompt["subject"]
    # age depends on current year, but 1990 is roughly 35-36 in 2025/2026.

    assert "front_view" in prompt
    assert "side_profile" in prompt


def test_format_prompt_output():
    data = {
        "subject": "35-year-old male",
        "front_view": "Front view text",
        "side_profile": "Side profile text",
        "body_type": "Body type text",
        "notes": ["Note 1"],
        "traits_used": 10,
        "eye_color_confidence": 0.9,
    }
    formatted = format_prompt_output(data)
    assert "PORTRAIT GENERATION PROMPT" in formatted
    assert "35-year-old male" in formatted
    assert "Note 1" in formatted
