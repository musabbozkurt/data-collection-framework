# word ngrams technique (split text into word group)
class NGrams():
    def ngrams(input, n):
        input = input.split(' ')
        output = {}
        for i in range(len(input) - n + 1):
            g = ' '.join(input[i:i + n])
            output.setdefault(g, 0)
            output[g] += 1
            # print(g)
