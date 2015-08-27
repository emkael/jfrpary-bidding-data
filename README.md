
JFR Pary - dane licytacji
=========================

Narzędzie dodające do strony wyników z JFR Pary dane licytacji, zbierane w pliku
BWS "pierniczkami" nowego typu.

Przykładowy efekt działania: [rozdania szkoleniowe z BOOM 2015](http://www.pzbs.pl/wyniki/boom/2015/boom_wirtualne_me.html)

Wymagania systemowe
-------------------

* python 2.x (testowane i tworzone w wersji 2.7.10)
* BeautifulSoup4

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
python bidding_data.py DANE_LICYTACJI.csv DANE_USTAWIENIA.csv KATALOG_ROBOCZY_Z_PREFIKSEM_TURNIEJU [mapowanie numerów rozdań]
```

`DANE_LICYTACJI.csv` i `DANE_USTAWIENIA.csv` to pliki z danymi wyeskportowanymi
z BWS.

`KATALOG_ROBOCZY_Z_PREFIKSEM_TURNIEJU` to ściezka to katalogu WWW z doklejonym
Parowym prefiksem turnieju (czyli np. `..\www\moj_turniej`).

Udostępniany ze skryptem wrapper [`bidding_data.sh`](bidding_data.sh)
obsługuje eksport z BWS poprzez `mdb-export`, wystarczy więc:
```
./bidding_data.sh PLIK.bws KATALOG_ROBOCZY_Z_PREFIKSEM_TURNIEJU [mapowanie numerów rozdań]
```

Narzędzie obsługuje niestandardowe zakresy numeracji rozdań w turnieju.

Domyślnie, mapowanie numeru rozdań z Par na numer rozdania w BWS
(numer fizycznego pudełka), odbywa się automatycznie (na podstawie nagłówków
plików HTML z protokołami).

Możliwe jest jednak podanie własnego mapowania numerów rozdań (niezbędne np.
wtedy, gdy w turnieju te same pudełka używane są więcej niż jeden raz).

Osiąga się to poprzez podanie dodatkowych parametrów za katalogiem roboczym.
Mapowanie określają, kolejno, trzy liczby:
* numer pierwszego rozdania wg numeracji JFR Pary
* numer ostatniego rozdania wg numeracji JFR Pary
* numer pierwszego rozdania w BWS (zakłada się ciągłość numeracji
w ramach mapowania)

Na przykład, podanie parametrów `1 8 23` sprawi, że protokoły od `*001.html`
do `*008.html` zostaną uzupełnione o licytację z rozdań 23-30.

Lista przyszłych usprawnień
---------------------------

Patrz: [`TODO.md`](TODO.md)

Autor
-----

Michał Klichowicz (mkl)

Licencja
--------

Patrz: [`LICENSE.md`](LICENSE.md)
