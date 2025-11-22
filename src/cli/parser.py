import argparse
from pathlib import Path

from commands.commands import analyze_cmd, generate_cmd

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Tool for analyzing images and generating sample images.",
    )

    subparsers = parser.add_subparsers(
        title="commands",
        dest="command",
        required=True,
    )

    # --- subcommand: analyze ---
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze an existing image file.",
        description="Analyze an existing image file and optionally write a report.",
    )
    analyze_parser.add_argument(
        "-i", "--input",
        type=Path,
        help="Path to the input image file.",
    )
    analyze_parser.add_argument(
        "-o", "--output",
        type=Path,
        default=Path("report.json"),
        help="Path to the output report file (default: output/report.json).",
    )
    analyze_parser.set_defaults(func=analyze_cmd)

    # --- subcommand: generate ---
    generate_parser = subparsers.add_parser(
        "generate",
        help="Generate a sample image.",
        description="Generate a sample image using predefined presets.",
    )
    generate_parser.add_argument(
        "--width",
        type=int,
        default=512,
        help="Output image width in pixels (default: 512).",
    )
    generate_parser.add_argument(
        "--height",
        type=int,
        default=512,
        help="Output image height in pixels (default: 512).",
    )
    generate_parser.add_argument(
        "--Nci",
        type=int,
        default=5,
        help="Number of circles to generate (default: 5).",
    )
    generate_parser.add_argument(
        "--Ntri",
        type=int,
        default=5,
        help="Number of triangles to generate (default: 5).",
    )
    generate_parser.add_argument(
        "--Nsq",
        type=int,
        default=5,
        help="Number of squares to generate (default: 5).",
    )
    generate_parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducible results (default: none).",
    )
    generate_parser.add_argument(
        "-o", "--output",
        type=Path,
        default=Path("sample.png"),
        help="Path to the generated image file (default: sample.png).",
    )
    generate_parser.set_defaults(func=generate_cmd)

    return parser
