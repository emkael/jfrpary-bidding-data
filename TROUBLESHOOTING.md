Zdecydowana większość problemów z bidding-data wynika z jednej z dwóch
rzeczy:

1. Na stronie nie ma plików stylów i skryptów.
2. Pliki z licytacją kiedyś się nie wysłały i nie chcą się wysłać ponownie.

W przypadku 1 należy:
 - przegrać ręcznie pliki [`css/bidding.css`](res/css/bidding.css), [`javas/bidding.js`](res/javas/bidding.js),
[`javas/jquery.js`](res/javas/jquery.js) i [`images/link.png`](res/images/link.png) do katalogu turnieju
 - ALBO kliknąć w programie "ślij kolorki", przy włączonym Gońcu
skierowanym na katalog turnieju

W przypadku 2 należy:
 - upewnić się, że ma się najnowszą wersję programu
 - ORAZ zaznaczyć "wymuś przesłanie" i ponownie przepuścić turniej przez
program
 - ALBO skasować *lokalny* katalog `bidding-data` z plikami licytacji i
przepuścić ponownie turniej przez program (upewniając się, że Goniec
poprawnie śle pliki)

Jeśli żaden z tych sposobów nie pomoże, należy, kolejno, jeśli
poprzednie punkty nie pomagają:
 - upewnić się, że bidding-data to ostatni program, który generuje pliki
turnieju (czyli np. nie chodzi nam Kolektor dla rund, dla których
generujemy licytację a także nie kliknęliśmy globusika w Parach)
 - przegenerować ponownie pliki turnieju, czyli:
   + dla zakończonego turnieju przerobić globusik w Parach
   + dla trwającego turnieju odpalić "prześlij rozdania na stronę" w
Kolektorze
   + przegenerować i wysłać ponownie pliki licytacji w bidding-data
