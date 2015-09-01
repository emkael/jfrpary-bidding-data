
JFR Pary - dane licytacji
=========================

Narzędzie dodające do strony wyników z JFR Pary dane licytacji, zbierane w pliku
BWS "pierniczkami" nowego typu.

Przykładowe efekty działania:
[rozdania szkoleniowe z BOOM 2015](http://www.pzbs.pl/wyniki/boom/2015/boom_wirtualne_me.html),
[Kadra U-20 z butlerem ligowym](http://emkael.info/brydz/wyniki/2015/u20_szczyrk/ligowe.html).

Wymagania systemowe
-------------------

* python 2.x (testowane i tworzone w wersji 2.7.10)
* BeautifulSoup4
* lxml (jako parser dla BS4)
* argparse

Opcjonalnie, wrapper Basha konwertujący dane z BWS do CSV, używa `mdb-export`
z pakietu `mdbtools`.

Instalacja
----------

Ściągnij zawartość tego repozytorium.

W katalogu WWW Par skonfiguruj JS i CSS niezbędny do prezentacji danych
licytacji:
* skopiuj [`css/bidding.css`](css/bidding.css) do katalogu WWW
* dołącz plik [`css/bidding.css`](css/bidding.css) gdzieś w arkuszach stylów turnieju
(np. poprzez `@import` w `kolorki.css`)
* skopiuj [`javas/bidding.js`](javas/bidding.js) do podkatalogu javas katalogu WWW (plik dołączany
jest automatycznie do stron z wynikami)
* skopiuj [`images/link.png`](images/link.png) do podkatalogu images katalogu WWW

Już, gotowe.

Użycie
------

Skrypt [`bidding_data.py`](bidding_data.py) operuje na następujących
danych wejściowych:
* plikach HTML wygenerowanych po zakończeniu turnieju stron statycznych
* plikach CSV z danymi o licytacji i ustawieniu par, wyeksportowanymi z pliku
BWS

Aby uzyskać pliki CSV niezbędne do działania narzędzia, należy zapisać całą
zawartość tabel `BiddingData` oraz `RoundData` do osobnych plików CSV.

W środowiskach linuksowych dokonuje tego narzędzie `mdb-export` z pakietu
`mdb-tools`:
```
mdb-export PLIK.bws BiddingData > DANE_LICYTACJI.csv
mdb-export PLIK.bws RoundData > DANE_USTAWIENIA.csv
```

Po wygenerowaniu w/w plików CSV, [`bidding_data.py`](bidding_data.py)
przyjmuje następujące parametry:
```
python bidding_data.py DANE_LICYTACJI.csv DANE_USTAWIENIA.csv PLIK_TURNIEJU.html
```

`DANE_LICYTACJI.csv` i `DANE_USTAWIENIA.csv` to pliki z danymi wyeskportowanymi
z BWS.

`PLIK_TURNIEJU.html` to ściezka do pliku turnieju w katalogu WWW
([ŚCIEŻKA]\PREFIX.html).

Udostępniany ze skryptem wrapper [`bidding_data.sh`](bidding_data.sh)
obsługuje eksport z BWS poprzez `mdb-export`, wystarczy więc:
```
./bidding_data.sh PLIK.bws KATALOG_ROBOCZY_Z_PREFIKSEM_TURNIEJU
```

Narzędzie obsługuje niestandardowe zakresy numeracji rozdań w turnieju.

Mapowanie numeru rozdań z Par na numer rozdania w BWS (numer fizycznego pudełka)
odbywa się automatycznie (na podstawie danych z BWS).

Lista przyszłych usprawnień
---------------------------

Patrz: [`TODO.md`](TODO.md)

Autor
-----

Michał Klichowicz (mkl)

Licencja
--------

Patrz: [`LICENSE.md`](LICENSE.md)
