
JFR Pary - dane licytacji
=========================

Narzędzie dodające do strony wyników z JFR Pary dane licytacji, zbierane w pliku
BWS "pierniczkami" nowego typu.

Przykładowe efekty działania:
[rozdania szkoleniowe z BOOM 2015](http://www.pzbs.pl/wyniki/boom/2015/boom_wirtualne_me.html),
[Kadra U-20 z butlerem ligowym](http://emkael.info/brydz/wyniki/2015/u20_szczyrk/ligowe.html).

Wymagania systemowe
-------------------

* system operacyjny MS Windows (testowane na Win7 i Win8.1)
* sterownik ODBC dla plików MS Access (zwykle obecny domyślnie z Windows,
weryfikowalny w Panelu Sterowania -> Narzędziach Administracyjnych ->
Żródła danych ODBC)

Instalacja
----------

Ściągnij paczkę z programem, dostępną w katalogu [`bundle`](bundle) tego
repozytorium i rozpakuj ją do wybranego przez siebie katalogu roboczego
programu.

Uwaga: paczki z sufiksem `-gui` zawierają wersję aplikacji z okienkowym
interfejsem graficznym.

W katalogu WWW Par skonfiguruj zasoby niezbędnę do prezentacji danych
licytacji:
* skopiuj [`css/bidding.css`](res/css/bidding.css) do katalogu WWW
* dołącz plik [`css/bidding.css`](res/css/bidding.css) gdzieś w arkuszach
stylów turnieju (np. poprzez `@import` w `kolorki.css`)
* skopiuj [`javas/bidding.js`](res/javas/bidding.js) do podkatalogu javas
katalogu WWW (plik dołączany jest automatycznie do stron z wynikami)
* skopiuj [`images/link.png`](res/images/link.png) do podkatalogu images
katalogu WWW

Już, gotowe.

Kompilacja i praca z kodem narzędzia
------------------------------------

Patrz: [`BUILD.md`](BUILD.md)

Użycie (wersja linii poleceń)
-----------------------------

Program składa się ze skompilowanego skryptu języka Python, dostępnego
w katalogu [`src`](src) tego repozytorium.

Skrypt [`bidding_data.py`](src/bidding_data.py) operuje na następujących
danych wejściowych:
* plikach HTML wygenerowanych po zakończeniu turnieju stron statycznych
* pliku BWS sesji

Program przyjmuje parametry w sposób następujący:
```
bidding_data.exe DANE_SESJI.bws PLIK_TURNIEJU.html
```

`DANE_SESJI.bws` to plik BWS z zebranymi danymi sesji.

`PLIK_TURNIEJU.html` to ściezka do pliku turnieju w katalogu WWW
([ŚCIEŻKA]\PREFIX.html).

Narzędzie obsługuje niestandardowe zakresy numeracji rozdań w turnieju.

Mapowanie numeru rozdań z Par na numer rozdania w BWS (numer fizycznego
pudełka) odbywa się automatycznie (na podstawie danych z BWS).

Użycie (wersja z interfejsem okienkowym)
----------------------------------------

Się klika, się wybiera i się robi.

Kompatybilność
--------------

Narzędzie łączy się przez ODBC do bazy MS Access, więc działa jedynie
pod Windowsem.

Wersja operująca na wyeksportowanych plikach CSV (np. przez `mdb-export`),
kompatybilna z pozostałymi systemami operacyjnymi i niewymagająca ODBC,
dostępna jest w gałęzi [csv](//github.com/emkael/jfrpary-bidding-data/tree/csv).

Do wersji z gałęzi CSV nie ma interfejsu graficznego.

Lista przyszłych usprawnień
---------------------------

Patrz: [`TODO.md`](TODO.md)

Autor
-----

Michał Klichowicz (mkl)

Licencja
--------

Patrz: [`LICENSE.md`](LICENSE.md)
