from service import Pipline


def main():
    pipline = Pipline()
    output = pipline.main()

    with open("result.txt", "w") as f:
        f.write(output)


if __name__ == "__main__":
    main()
