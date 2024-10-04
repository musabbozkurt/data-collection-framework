# character ngrams technique (split word into character group)
class CharNGrams:
    def char_n_grams(input, n):
        input = input.split(' ')
        output = {}
        for i in range(len(input) - n + 1):
            g = ' '.join(input[i:i + n])
            asd = [g[i:i + n] for i in range(len(g) - n + 1)]
            # print(asd)
            output.setdefault(g, 0)
            output[g] += 1
            # print(output)
