from reedsolo import RSCodec

def main():
    data = [32,65,205,69,41,220,46,128,236]
    print(data)

    rsc = RSCodec(17)
    e1 = rsc.encode(data)
    print(list(e1))
    print(list(rsc.decode(e1)[0]))

    print("make error")
    e2 = rsc.encode(data)
    e2[0] = 0
    print(list(e2))

    print("correct error")
    print(list(rsc.decode(e2)[0]))

if __name__ == "__main__":
    main()
