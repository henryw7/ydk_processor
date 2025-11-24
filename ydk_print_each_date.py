import os

from ydk_parser import Deck, read_ydk
from card_database_loader import load_card

ydk_filename = "sample_deck/exodia sky striker.ydk"

def print_card_in_list_name_and_date(card_list):
    assert type(card_list) is list

    for i_card in range(len(card_list)):
        card_id = card_list[i_card]
        card_info = load_card(card_id)
        card_name = card_info["name"]
        card_earliest_release_date = card_info["earliest_release_date"]
        print(f"{card_earliest_release_date}  {card_name}")

def print_card_in_deck_name_and_date(deck):
    assert type(deck) is Deck

    print("main deck:")
    print_card_in_list_name_and_date(deck.main)
    print()
    print("extra deck:")
    print_card_in_list_name_and_date(deck.extra)
    print()
    print("side:")
    print_card_in_list_name_and_date(deck.side_main)
    print_card_in_list_name_and_date(deck.side_extra)
    print()

if __name__ == '__main__':
    assert os.path.exists(ydk_filename)
    assert ydk_filename.endswith(".ydk")

    deck = read_ydk(ydk_filename)
    print_card_in_deck_name_and_date(deck)

    latest_release_date = deck.get_date()
    print(f"The whole deck is available at {latest_release_date}")
    if latest_release_date == "9999-12-31":
        print(f"A timestamp of {latest_release_date} means the card is released very recently and is not updated in our database.")
