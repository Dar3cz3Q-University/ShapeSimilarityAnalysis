from generate_image.generate_image import generate_image
from analyze_image.shape_detector import ShapeDetector
import argparse

def analyze_cmd(args: argparse.Namespace):
  detector = ShapeDetector(args.input)
  detector.process(args.threshold)

def generate_cmd(args: argparse.Namespace):
  generate_image(
    args.width,
    args.height,
    args.output,
    args.Nci,
    args.Nsq,
    args.Ntri,
    args.seed,
  )
