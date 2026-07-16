"""Stage criticality constants for DevScore calculation."""

__all__ = ["STAGE_CRITICALITY"]

STAGE_CRITICALITY = {
    "zygote": 0.88,
    "blastocyst": 0.85,
    "gastrulation": 1.00,
    "neurulation": 1.00,
    "organogenesis": 0.95,
    "fetal_early": 0.65,
    "fetal_late": 0.50,
    "neonatal": 0.30,
    "childhood": 0.28,
    "adult": 0.25,
}
