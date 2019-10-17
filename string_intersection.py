import re
import pymorphy2

from collections import Counter, OrderedDict


def _parse_to_lemmas(
    analyzer,
    string,
    forms={"NOUN", "ADJF", "ADJS", "PRTF", "PRTS", "NUMR"},
    forms_exceptions={"PREP", "CONJ", "PRCL", "INTJ"},
):
    words = string.split()
    words_normalized = []
    for word in words:
        # Iterate over all possible word lemmas
        lemmas = analyzer.parse(word)
        for i in range(len(lemmas)):
            p = lemmas[i]
            if p.tag.POS in forms:
                words_normalized.append(p.normal_form)
                break
    return words_normalized


def _clear_string(string):
    clearing_list = [", ", " ", "\n", " - ", " + ", " (", ") "]
    for ch in clearing_list:
        if ch in string:
            string = string.replace(ch, " ")
    return string


def get_max_lemmas_intersection(
    analyzer, input_string: str, source_list: list, without_prepositions: bool = True
) -> list:
    """
        Finding max matching string from source_list of strings for input_string
        Firstly all words are being normalized (i.e. getting lemmas)
        Then Counters of lemmas are being intersected, 
        and Counter with max count of intersected elements is returned
    """
    input_string_lemmas = _parse_to_lemmas(
        analyzer, _clear_string(input_string).strip()
    )
    sources_lemmas = [
        _parse_to_lemmas(analyzer, _clear_string(source)) for source in source_list
    ]
    if without_prepositions:
        input_string_lemmas = filter(lambda word: len(word) > 2, input_string_lemmas)
        sources_lemmas = [
            filter(lambda word: len(word) > 2, words) for words in sources_lemmas
        ]
    input_string_counter = Counter(input_string_lemmas)
    sources_counter = [Counter(source) for source in sources_lemmas]

    counter_intersect = lambda el1, el2: el1 & el2
    try:
        intersection_index, intersection_value = max(
            enumerate(
                map(
                    counter_intersect,
                    [input_string_counter] * len(sources_counter),
                    sources_counter,
                )
            ),
            key=lambda x: sum(x[1].values()),
        )
        result = source_list[intersection_index]
    except:
        print(f"No matches were found for {input_string}")
        result, intersection_value = None, None
    return result, intersection_value


def run():
    analyzer = pymorphy2.MorphAnalyzer()
    name = "Пена бытовая монтажная 620 мл"
    some_products_list = [
        "Монтажные крепления SomeBrand",
        "AnotherBrand пена для ванн",
        "Монтажные пены TrueBrand",  # expected
    ]
    result, intersection_values = get_max_lemmas_intersection(
        analyzer, name, some_products_list
    )
    print(f"Found match {result} based on intersection value {intersection_values}")


if __name__ == "__main__":
    run()
