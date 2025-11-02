import os
from dateutil.parser import parse as parse_date

from ydk_parser import Deck, read_ydk, write_ydk
from card_database_loader import load_card

# These cards are from the first TCG set, Legends of Blue Eyes White Dragon (LOB)
MAIN_REPLACEMENT_CARD_ID = 38142739 # Petit Angel
EXTRA_REPLACEMENT_CARD_ID = 9293977 # Metal Dragon

ydk_filename = "sample_deck/goat.ydk"
history_deck_latest_release_date = "2004-12-31"

def replace_card_in_list_after_date(card_list, threshold_date, replacement_card_id):
    assert type(card_list) is list

    for i_card in range(len(card_list)):
        card_id = card_list[i_card]
        card_info = load_card(card_id)
        card_earliest_release_date = card_info["earliest_release_date"]
        if parse_date(threshold_date) < parse_date(card_earliest_release_date):
            print(f"Card \"{card_info["name"]}\" first released on {card_earliest_release_date} is replaced")
            card_list[i_card] = replacement_card_id

    return card_list

def replace_card_in_deck_after_date(deck, threshold_date):
    assert type(deck) is Deck

    deck.main       = replace_card_in_list_after_date(deck.main,       threshold_date, MAIN_REPLACEMENT_CARD_ID)
    deck.extra      = replace_card_in_list_after_date(deck.extra,      threshold_date, EXTRA_REPLACEMENT_CARD_ID)
    deck.side_main  = replace_card_in_list_after_date(deck.side_main,  threshold_date, MAIN_REPLACEMENT_CARD_ID)
    deck.side_extra = replace_card_in_list_after_date(deck.side_extra, threshold_date, EXTRA_REPLACEMENT_CARD_ID)

    return deck

if __name__ == '__main__':
    assert os.path.exists(ydk_filename)
    assert ydk_filename.endswith(".ydk")

    deck = read_ydk(ydk_filename)
    deck = replace_card_in_deck_after_date(deck, history_deck_latest_release_date)

    output_filename = ydk_filename[:-4] + "_" + str(history_deck_latest_release_date) + ".ydk"
    if os.path.exists(output_filename):
        print(f"Warning: {output_filename} already exists, it will be overwritten.")
    write_ydk(output_filename, deck)
