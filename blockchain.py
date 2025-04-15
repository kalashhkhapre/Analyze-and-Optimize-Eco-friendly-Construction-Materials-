def verify_source(source: str) -> bool:
    verified_sources = [
        "EcoCement Co.",
        "NatureBricks",
        "EarthInnovations",
        "PlasticCycle",
        "Sustainable Works",
        "GreenBuild Ltd.",
        "certified-supplier-a",
        "eco-source-b",
        "govt-agency-c"
    ]
    return source.strip().lower() in (s.lower() for s in verified_sources)