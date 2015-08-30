
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
* pypyodbc

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
* pliku BWS sesji

Skrypt przyjmuje parametry w sposób następujący:
```
python bidding_data.py DANE_SESJI.bws KATALOG_ROBOCZY_Z_PREFIKSEM_TURNIEJU [mapowanie numerów rozdań]
```

`DANE_SESJI.bws` to plik BWS z zebranymi danymi sesji.

`KATALOG_ROBOCZY_Z_PREFIKSEM_TURNIEJU` to ściezka to katalogu WWW z doklejonym
Parowym prefiksem turnieju (czyli np. `..\www\moj_turniej`).

Narzędzie obsługuje niestandardowe zakresy numeracji rozdań w turnieju.

Domyślnie, mapowanie numeru rozdań z Par na numer rozdania w BWS
(numer fizycznego pudełka), odbywa się automatycznie (na podstawie danych z BWS).

Możliwe jest jednak podanie własnego mapowania numerów rozdań (przydatne np.
wtedy, gdy w turnieju te same pudełka używane są więcej niż jeden raz, a gdy 
fizyczne numery rozdań używane są wiele razy w jednym BWS - wręcz niezbędne).

Osiąga się to poprzez podanie dodatkowych parametrów za katalogiem roboczym.
Mapowanie określają, kolejno, trzy liczby:
* numer pierwszego rozdania wg numeracji JFR Pary
* numer ostatniego rozdania wg numeracji JFR Pary
* numer pierwszego rozdania w BWS (zakłada się ciągłość numeracji
w ramach mapowania)

Na przykład, podanie parametrów `1 8 23` sprawi, że protokoły od `*001.html`
do `*008.html` zostaną uzupełnione o licytację z rozdań 23-30.

Kompatybilność
--------------

Narzędzie łączy się przez ODBC do bazy MSAccess, więc działa jedynie
pod Windowsem.

Wersja operująca na wyeksportowanych plikach CSV (np. przez `mdb-export`),
kompatybilna z pozostałymi systemami operacyjnymi i niewymagająca ODBC,
dostępna jest w gałęzi [csv](//github.com/emkael/jfrpary-bidding-data/tree/csv).

Lista przyszłych usprawnień
---------------------------

Patrz: [`TODO.md`](TODO.md)

Autor
-----

Michał Klichowicz (mkl)

Licencja
--------

Patrz: [`LICENSE.md`](LICENSE.md)
