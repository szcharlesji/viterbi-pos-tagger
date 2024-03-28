import sys


def parse(train, test, output):
    with open(train, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # print("Number of lines: ", len(lines))
    frequency = {}
    tag_word = {}
    bigram = {}
    previous_tag = ""
    for line in lines:
        if line == "\n":
            word = " "
            tag = "START"
        else:
            word, tag = line.strip("\n").split("\t")
            word = word.lower()

        # if tag not in the dictionary
        if tag not in tag_word:
            tag_word[tag] = {}
            frequency[word] = 1

        else:
            # if word not in the dictionary
            if word not in tag_word[tag]:
                tag_word[tag][word] = 1
                frequency[word] = 1

            # if word in the dictionary
            else:
                tag_word[tag][word] += 1
                frequency[word] += 1
        if previous_tag != "":
            if previous_tag not in bigram:
                bigram[previous_tag] = {}
                bigram[previous_tag][tag] = 1
            else:
                if tag not in bigram[previous_tag]:
                    bigram[previous_tag][tag] = 1
                else:
                    bigram[previous_tag][tag] += 1

        previous_tag = tag

    # produce the likelihood table
    likelihoods = {}
    for tag, words in tag_word.items():
        total = sum(words.values())
        likelihoods[tag] = {}
        for word, count in words.items():
            likelihoods[tag][word] = count / total
            # print(tag, word, likelihoods[tag][word])

    # produce the bigram probability table
    bigram_probabilities = {}
    for tag, next_tags in bigram.items():
        bigram_probabilities[tag] = {}
        total = sum(next_tags.values())
        for next_tag, count in next_tags.items():
            bigram_probabilities[tag][next_tag] = count / total
            # print(tag, next_tag, bigram_probabilities[tag][next_tag])

    # all the pos
    pos = list(tag_word.keys())
    # print(pos)

    # parse the test file
    with open(test, "r", encoding="utf-8") as f:
        lines = f.readlines()
    # prepare the output file
    output_file = open(output, "w", encoding="utf-8")

    backtrace = {}
    for i, line in enumerate(lines):
        word_backup = line.strip("\n")
        word = word_backup.lower()
        if word:  # if not empty line
            backtrace[i] = {}

            for tag in pos:
                likelihood = likelihoods.get(tag, {}).get(
                    word, 0.00000001
                )  # if word not in the dictionary, use 0.00000001
                bigram_prob = bigram_probabilities.get(previous_tag, {}).get(
                    tag, 0.00000001  # if tag not in the dictionary, use 0.00000001
                )
                backtrace[i][tag] = likelihood * bigram_prob

            best_prob = max(backtrace[i].values())  # best tag for this word
            best_tag = ""
            for tag, prob in backtrace[i].items():
                if prob == best_prob:
                    best_tag = tag
                    break

            # numbers
            if any(char.isdigit() for char in word_backup):
                if any(char == "-" for char in word_backup):
                    best_tag = "JJ"
                else:
                    best_tag = "CD"

            # VB words
            VB_words = ["will", "may", "can", "wo", "would", "should", "could"]
            if word_backup.lower() in VB_words:
                best_tag = "VB"
            # "-ed" past tense verbs
            # if word_backup[-2:] == "ed" and (best_tag in ["VBD"]):
            #     best_tag = "VBD"
            # proper nouns
            if word_backup[0].isupper() and best_tag == "NN":
                best_tag = "NNP"

            # non-DT
            DT_words = [
                "a",
                "an",
                "the",
                "any",
                "that",
                "this",
                "all",
                "these",
                "those",
                "another",
                "some",
                "each",
                "every",
                "both",
                "either",
                "neither",
                "no",
                "half",
            ]
            if best_tag == "DT" and word_backup.lower() not in DT_words:
                best_tag = "NN"
            output_file.write(f"{word_backup}\t{best_tag}\n")

            previous_tag = best_tag
        else:
            output_file.write("\n")
            previous_tag = "START"


def main():
    if len(sys.argv) != 4:
        print(
            "Usage: python cj2220_viterbi_HW3.py <train_file> <test_file> <output_file>"
        )
        return

    train_file = sys.argv[1]
    test_file = sys.argv[2]
    output_file = sys.argv[3]

    parse(train_file, test_file, output_file)


if __name__ == "__main__":
    main()
