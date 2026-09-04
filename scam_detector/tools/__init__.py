"""
tools
-----
Utility scripts and tools for scam_detector (threshold tuning, model evaluation, data maintenance).
"""

__all__: list[str] = [
    "BenchmarkMetrics",
    "compute_benchmark_metrics",
    "generate_markdown_benchmark_report",
    "map_kaggle_row_to_ifind",
    "run_kaggle_benchmark",
]


def __getattr__(name: str):
    if name in __all__:
        import scam_detector.tools.benchmark_kaggle as bk
        return getattr(bk, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

