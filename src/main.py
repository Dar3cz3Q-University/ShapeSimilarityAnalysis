from cli.parser import build_parser

def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)

    input("Press Enter to continue...")

if __name__ == "__main__":
    main()
