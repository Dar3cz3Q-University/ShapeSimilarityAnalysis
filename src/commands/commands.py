from generate_image.generate_image import generate_image
import argparse

def analyze_cmd(args: argparse.Namespace):
  pass

def generate_cmd(args: argparse.Namespace):
  generate_image(
    args.width,
    args.height,
    args.output,
    args.Nci,
    args.Nrect,
    args.Ntri,
    args.seed,
  )
