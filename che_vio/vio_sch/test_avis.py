
def test():
    list_a = [1, 2, 3, 4, 5]
    list_b = [3, 4, 5, 6, 7]

    for a in list_a:
        print(a)
        for b in list_b:
            # print(b)
            if a == b:
                print(a, b)
                list_b.remove(b)
                list_a.remove(a)
                break

    print(list_a)
    print(list_b)


if __name__ == "__main__":
    test()
