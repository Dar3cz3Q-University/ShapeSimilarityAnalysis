import argparse

def main():
  parser = argparse.ArgumentParser(
    description=""
  )

  parser.add_argument(
    "--image-path",
    type=str,
    required=True,
  )

  args = parser.parse_args()

  print(args.image)

if __name__ == "__main__":
    main()
