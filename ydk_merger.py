import os, random

from ydk_parser import Deck, read_ydk, write_ydk, list_to_counter_map, counter_map_to_list

WORKING_FOLDER_NAME = "processing"
OUTPUT_YDK_FILE_NAME = "merged.ydk"

# random.seed(100)

def merge_decks_random(decks):
    merged_deck = Deck()
    merged_deck.main  = [ id for deck in decks for id in (deck.main + deck.side_main) ]
    merged_deck.extra = [ id for deck in decks for id in (deck.extra + deck.side_extra) ]
    random.shuffle(merged_deck.main)
    random.shuffle(merged_deck.extra)
    random_0_1 = random.random()
    main_deck_count = 40 if (random_0_1 < 0.75) else 60
    extra_deck_count = 15
    merged_deck.main  = merged_deck.main[: main_deck_count]
    merged_deck.extra = merged_deck.extra[: extra_deck_count]

    funny_cards = read_ydk("funny_cards.ydk")
    funny_cards.main  = sum([[id] * 3 for id in funny_cards.main ], [])
    funny_cards.extra = sum([[id] * 3 for id in funny_cards.extra], [])
    random.shuffle(funny_cards.main)
    random.shuffle(funny_cards.extra)

    def funny_replace_repeated_card(deck_with_repeated, funny_deck):
        replaced = []
        deck_with_repeated = list_to_counter_map(deck_with_repeated)
        funny_deck = funny_deck.copy()
        for key, value in deck_with_repeated.items():
            if value > 3:
                replaced.extend([key] * 3)
                for i in range(value - 3):
                    funny_card = funny_deck.pop()
                    while funny_card in deck_with_repeated:
                        funny_card = funny_deck.pop()
                    replaced.append(funny_card)
            else:
                replaced.extend([key] * value)
        return replaced

    merged_deck.main  = funny_replace_repeated_card(merged_deck.main,  funny_cards.main)
    merged_deck.extra = funny_replace_repeated_card(merged_deck.extra, funny_cards.extra)
    merged_deck.main.sort()
    merged_deck.extra.sort()

    merged_deck.sanity_check()

    return merged_deck

def merge_decks_at_least_one(decks):
    merged_deck = Deck()
    merged_deck.main  = [ id for deck in decks for id in (deck.main + deck.side_main) ]
    merged_deck.extra = [ id for deck in decks for id in (deck.extra + deck.side_extra) ]

    def remove_repeated(deck_with_repeated, target_count):
        deck_with_repeated = list_to_counter_map(deck_with_repeated)

        card_count = { 1:0, 2:0, 3:0 }
        for key, value in deck_with_repeated.items():
            if value > 3:
                deck_with_repeated[key] = 3
                value = 3
            card_count[value] += 1
        total_card_count = card_count[1] * 1 + card_count[2] * 2 + card_count[3] * 3
        if total_card_count <= target_count:
            return counter_map_to_list(deck_with_repeated)

        n_extra = total_card_count - target_count
        for max_repeated_card in range(3, 0, -1):
            if card_count[max_repeated_card] < n_extra:
                assert max_repeated_card > 1
                for key, value in deck_with_repeated.items():
                    if value == max_repeated_card:
                        deck_with_repeated[key] -= 1
                n_extra -= card_count[max_repeated_card]
                card_count[max_repeated_card - 1] += card_count[max_repeated_card]
                card_count[max_repeated_card] = 0
            else:
                card_with_count = deck_with_repeated
                if max_repeated_card > 1:
                    card_with_count = [key for key, value in deck_with_repeated.items() if value == max_repeated_card]
                random.shuffle(card_with_count)
                for i_extra in range(n_extra):
                    deck_with_repeated[card_with_count[i_extra]] -= 1
                break
        return counter_map_to_list(deck_with_repeated)

    random_0_1 = random.random()
    main_deck_count = 40 if (random_0_1 < 0.75) else 60
    extra_deck_count = 15
    merged_deck.main = remove_repeated(merged_deck.main, main_deck_count)
    merged_deck.extra = remove_repeated(merged_deck.extra, extra_deck_count)

    merged_deck.sanity_check()

    return merged_deck

if __name__ == '__main__':
    dir_exist = os.path.isdir(WORKING_FOLDER_NAME)
    if not dir_exist:
        os.mkdir(WORKING_FOLDER_NAME)
        print(f"Folder {WORKING_FOLDER_NAME} not exist. I've created it for you. Please place more than two ydk files in there.")
        exit()

    ydk_filenames = []
    for filename in os.listdir(WORKING_FOLDER_NAME):
        if filename.endswith(".ydk"):
            full_path = os.path.join(WORKING_FOLDER_NAME, filename)
            assert os.path.isfile(full_path)
            ydk_filenames.append(filename)

    if len(ydk_filenames) == 0:
        print(f"No ydk file found in {WORKING_FOLDER_NAME} folder. Please place more than two ydk files in there.")
        exit()
    if len(ydk_filenames) == 1:
        print(f"Only one ydk file ({ydk_filenames[0]}) found in {WORKING_FOLDER_NAME} folder. Please place more than two ydk files in there.")
        exit()

    if OUTPUT_YDK_FILE_NAME in ydk_filenames:
        print(f"Warning: {OUTPUT_YDK_FILE_NAME} already exists, it will be overwritten.")
        ydk_filenames.remove(OUTPUT_YDK_FILE_NAME)

    decks = []
    for ydk_filename in ydk_filenames:
        full_path = os.path.join(WORKING_FOLDER_NAME, ydk_filename)
        deck = read_ydk(full_path)
        decks.append(deck)

    # merged_deck = merge_decks_random(decks)
    merged_deck = merge_decks_at_least_one(decks)
    print(merged_deck)

    output_full_path = os.path.join(WORKING_FOLDER_NAME, OUTPUT_YDK_FILE_NAME)
    write_ydk(output_full_path, merged_deck)
