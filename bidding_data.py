import csv, sys, json, glob, re
from os import path
from bs4 import BeautifulSoup as bs4

class JFRBidding:

    # alignment of the bidding table
    __directions = ['W', 'N', 'E', 'S']

    # converts csv file to list of row lists
    def __csv_to_list(self, file_path):
        file_data = []
        with file(file_path) as csv_file:
            csv_data = csv.reader(csv_file)
            for line in csv_data:
                file_data.append(line)
        return file_data

    # converts CSV lineup data to {round}.{sector}_{table}.{pair numbers} structure
    def __parse_lineup_data(self, sitting_data):
        round_lineups = {}
        for sitting in sitting_data[1:]:
            round_no = int(sitting[2])
            table_no = sitting[0] + '_' + sitting[1]
            if not round_lineups.has_key(round_no):
                round_lineups[round_no] = {}
            round_lineups[round_no][table_no] = sorted([int(sitting[3]), int(sitting[4])])
        return round_lineups

    # converts CSV bidding to {board}.{sector}_{table}.{round}.{bidding}[] structure,
    # including erased calls
    def __parse_bidding_data(self, bidding_data):
        bids = {}
        for bid in bidding_data[1:]:
            board_no = int(bid[4])
            round_no = int(bid[3])
            table_no = bid[1] + '_' + bid[2]
            bid_counter = int(bid[5])
            bid_erased = int(bid[10])
            if not bids.has_key(board_no):
                bids[board_no] = {}
            if not bids[board_no].has_key(table_no):
                bids[board_no][table_no] = {}
            if not bids[board_no][table_no].has_key(round_no):
                bids[board_no][table_no][round_no] = {}
            if bid_erased == 1:
                if bids[board_no][table_no][round_no].has_key(bid_counter):
                    if bids[board_no][table_no][round_no][bid_counter]['direction'] == bid[6]:
                        bids[board_no][table_no][round_no].pop(bid_counter, None)
            else:
                bids[board_no][table_no][round_no][bid_counter] = {'direction': bid[6], 'bid': bid[7] }
        return bids

    # converts bidding data into HTML table
    def __format_bidding(self, bidding):
        html_output = '<table>'
        html_output = html_output + '<tr>'
        for dir in self.__directions:
            html_output = html_output + '<th>' + dir + '</th>'
        html_output = html_output + '</tr>'
        for bid_round in bidding:
            html_output = html_output + '<tr>'
            for bid in bid_round:
                bid_match = re.match(r'(\d)([SHDCN])', bid)
                if bid_match:
		    bid = bid_match.group(1) + '<img src="images/' + bid_match.group(2) + '.gif" />'
                html_output = html_output + '<td>' + bid + '</td>'
            html_output = html_output + '</tr>'
        html_output = html_output + '</table>'
        return html_output

    # returns file path for bidding HTML output
    # {prefix}_bidding_{jfr_board_number}_{pair_numbers}.txt
    def __get_bidding_file_output_path(self, board_no, round_no=None, table_no=None, pair_numbers=None):
        return '{0}_bidding_{1:03}_{2}.txt'.format(
            self.__tournament_prefix,
            board_no,
            '_'.join(
                map(str,
                    self.__round_lineups[round_no][table_no] if pair_numbers is None # read pair numbers from lineup
                    else pair_numbers)                                               # or use numbers provided, e.g. from JFR HTML
            )
        )

    def __map_board_numbers(self, custom_mapping=None):
        self.__tournament_files = [f for f
                                   in glob.glob(self.__tournament_prefix + '*.html')
                                   if re.search(self.__tournament_files_match, f)]
        if custom_mapping is not None:
            custom_files = []
            for jfr_number in range(custom_mapping[0], custom_mapping[1]+1):
                # only include these board numbers from custom mapping which actually exist in JFP output
                board_files = [f for f in self.__tournament_files if f.endswith('{0:03}.html'.format(jfr_number))]
                if len(board_files):
                    self.__board_number_mapping[jfr_number - custom_mapping[0] + custom_mapping[2]] = jfr_number
                    custom_files = custom_files + board_files
            self.__tournament_files = custom_files
        else:
            for tournament_file in self.__tournament_files:
                # scan for all JFR board HTML files and read actual board numbers from HTML headers
                file_number = re.match(self.__tournament_files_match, tournament_file).group(1)
                with file(tournament_file, 'r+') as board_html:
                    board_content = bs4(board_html, from_encoding='utf-8')
                    # first found <h4> element should be actual board number
                    board_number = re.sub('[^0-9]', '', board_content.select('h4')[0].contents[0].strip())
                    self.__board_number_mapping[int(board_number, 10)] = int(file_number, 10)

    # sitting read from BWS
    __round_lineups = {}
    # bidding read from BWS
    __bids = {}

    # full path + JFR prefix
    __tournament_prefix = ''
    # RegEx matching board HTML files
    __tournament_files_match = None
    # matched files, including board number mapping boundaries
    __tournament_files = []

    # BWS number -> JFR number mapping
    __board_number_mapping = {}

    def __init__(self, bidding_file, lineup_file, file_prefix, board_mapping):
        self.__round_lineups = self.__parse_lineup_data(self.__csv_to_list(lineup_file))
        self.__bids = self.__parse_bidding_data(self.__csv_to_list(bidding_file))
        self.__tournament_prefix = path.splitext(path.realpath(file_prefix + '.html'))[0]
        self.__tournament_files_match = re.compile(re.escape(self.__tournament_prefix) + '([0-9]{3})\.html')
        self.__map_board_numbers(board_mapping)

    def write_bidding_tables(self):
        for board_no, board_data in self.__bids.items():
            if board_no in self.__board_number_mapping:
                for table_no, table_data in board_data.items():
                    for round_no, round_data in table_data.items():
                        bidding = sorted(round_data)
                        dealer = round_data[bidding[0]]['direction']
                        bidding_table = [[], [], [], []]
                        # compile bidding player-by-player
                        for bid_index in bidding:
                            bid = round_data[bid_index]
                            bidding_table[self.__directions.index(bid['direction'])].append(bid['bid'])
                            last_bidder = bid['direction']
                        # fill skipped calls for players before dealer in the first round
                        for pos in range(0, self.__directions.index(dealer)):
                            bidding_table[pos].insert(0, '')
                        # fill skipped calls for players after pass out (so that bidding table is a proper matrix)
                        for pos in range(self.__directions.index(last_bidder), len(self.__directions)):
                            bidding_table[pos].append('')
                        # transpose the bidding table, align it row-by-row (bidding round-by-round)
                        bidding_table = map(list, zip(*bidding_table))
                        bidding_file_path = self.__get_bidding_file_output_path(self.__board_number_mapping[board_no], round_no, table_no)
                        with file(bidding_file_path, 'w') as bidding_file:
                            bidding_file.write(self.__format_bidding(bidding_table))

    def write_bidding_scripts(self):
        for tournament_file in self.__tournament_files:
            with file(tournament_file, 'r+') as board_html:
                board_content = bs4(board_html, from_encoding='utf-8')
                header_scripts = board_content.select('head script')
                # check for jQuery, append if necessary
                jquery_scripts = [script for script in header_scripts if script['src'] == 'javas/jquery.js']
                if not len(jquery_scripts):
                    jquery_scripts.append(bs4('<script src="javas/jquery.js" type="text/javascript"></script>').script)
                    board_content.head.append(jquery_scripts[0])
                # check for bidding.js
                bidding_scripts = [script for script in header_scripts if script['src'] == 'javas/bidding.js']
                # and make sure bidding.js is appended after jQuery
                for script in bidding_scripts:
                    script.extract()
                jquery_scripts[0].insert_after(bs4('<script src="javas/bidding.js" type="text/javascript"></script>').script)
                board_html.seek(0)
                board_html.write(board_content.prettify('utf-8', formatter='html'))
                board_html.truncate()

    def write_bidding_links(self):
        for tournament_file in self.__tournament_files:
            file_number = re.match(self.__tournament_files_match, tournament_file).group(1)
            board_text_path = path.splitext(tournament_file)[0] + '.txt'
            with file(board_text_path, 'r+') as board_text:
                board_text_content = bs4(board_text, from_encoding='iso-8859-2')
                for row in board_text_content.select('tr'):
                    cells = row.select('td')
                    # traveller table rows for specific score entries should have 11 cells
                    if len(cells) == 11:
                        pair_numbers = sorted([int(cells[1].contents[0]), int(cells[2].contents[0])])
                        bidding_link = bs4('<a href="#" class="biddingLink">[lic]</a>')
                        bidding_link.a['data-bidding-link'] = path.basename(self.__get_bidding_file_output_path(
                            int(file_number, 10),
                            pair_numbers=pair_numbers
                        ))
                        # fourth cell is the contract
                        for link in cells[3].select('a.biddingLink'):
                            link.extract()
                        cells[3].append(bidding_link)
                board_text.seek(0)
                board_text.write(board_text_content.table.prettify('iso-8859-2', formatter='html'))
                board_text.truncate()

bidding_parser = JFRBidding(bidding_file=sys.argv[1],
                            lineup_file=sys.argv[2],
                            file_prefix=sys.argv[3],
                            board_mapping=map(int, sys.argv[4:]) if len(sys.argv) > 4 else None)
bidding_parser.write_bidding_tables()
bidding_parser.write_bidding_scripts()
bidding_parser.write_bidding_links()
