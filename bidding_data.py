import csv, sys, json, glob, re
from os import path
from bs4 import BeautifulSoup as bs4

bidding_data = []

with file(sys.argv[1]) as bidding_file:
    bidding_csv = csv.reader(bidding_file)
    for line in bidding_csv:
        bidding_data.append(line)

sitting_data = []

with file(sys.argv[2]) as sitting_file:
    sitting_csv = csv.reader(sitting_file)
    for line in sitting_csv:
        sitting_data.append(line)

round_lineups = {}

for sitting in sitting_data[1:]:
    round_no = int(sitting[2])
    table_no = sitting[0] + '_' + sitting[1]
    if not round_lineups.has_key(round_no):
        round_lineups[round_no] = {}
    round_lineups[round_no][table_no] = sorted([int(sitting[3]), int(sitting[4])])

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

tournament_path_prefix = sys.argv[3] + '.html'

output_path = path.dirname(tournament_path_prefix)
tournament_prefix = path.splitext(path.realpath(tournament_path_prefix))[0]

directions = ['W', 'N', 'E', 'S']

def format_bidding(bidding):
    html_output = '<table>'
    html_output = html_output + '<tr>'
    for dir in directions:
        html_output = html_output + '<th>' + dir + '</th>'
    html_output = html_output + '</tr>'
    for bid_round in bidding:
        html_output = html_output + '<tr>'
        for bid in bid_round:
            html_output = html_output + '<td>' + bid + '</td>'
        html_output = html_output + '</tr>'
    html_output = html_output + '</table>'
    return html_output

for board_no, board_data in bids.items():
    for table_no, table_data in board_data.items():
        for round_no, round_data in table_data.items():
            bidding = sorted(round_data)
            dealer = round_data[bidding[0]]['direction']
            bidding_table = [[], [], [], []]
            for bid_index in bidding:
                bid = round_data[bid_index]
                bidding_table[directions.index(bid['direction'])].append(bid['bid'])
                last_bidder = bid['direction']
            for pos in range(0, directions.index(dealer)):
                bidding_table[pos].insert(0, '')
            for pos in range(directions.index(last_bidder), len(directions)):
                bidding_table[pos].append('')
            bidding_table = map(list, zip(*bidding_table))
            # TODO: file_number, a nie deal_number
            bidding_file_path = tournament_prefix + '_bidding_' + str(board_no) + '_' + '_'.join(map(str, round_lineups[round_no][table_no])) + '.txt'
            with file(bidding_file_path, 'w') as bidding_file:
                bidding_file.write(format_bidding(bidding_table))

tournament_files_match = re.compile(tournament_prefix + '([0-9]{3})\.html')
tournament_files = [f for f in glob.glob(tournament_prefix + '*.html') if re.search(tournament_files_match, f)]

deal_numbers = {}

for tournament_file in tournament_files:
    file_number = re.match(tournament_files_match, tournament_file).group(1)
    with file(tournament_file, 'r+') as board_html:
        board_content = bs4(board_html, from_encoding='utf-8')
        header_scripts = board_content.select('head script')
        jquery_scripts = [script for script in header_scripts if script['src'] == 'javas/jquery.js']
        if not len(jquery_scripts):
            board_content.head.append(bs4('<script src="javas/jquery.js" type="text/javascript"></script>').script)
        bidding_scripts = [script for script in header_scripts if script['src'] == 'javas/bidding.js']
        if not len(bidding_scripts):
            board_content.head.append(bs4('<script src="javas/bidding.js" type="text/javascript"></script>').script)
        board_number = board_content.select('h4')[0].contents[0].strip().replace('ROZDANIE ', '')
        deal_numbers[file_number] = board_number
        board_html.seek(0)
        board_html.write(board_content.prettify('utf-8'))
    board_text_path = path.splitext(tournament_file)[0] + '.txt'
    with file(board_text_path, 'r+') as board_text:
        board_text_content = bs4(board_text, from_encoding='iso-8859-2')
        for row in board_text_content.select('tr'):
            cells = row.select('td')
            if len(cells) == 11:
                pair_numbers = sorted([int(cells[1].contents[0]), int(cells[2].contents[0])])
                bidding_link = bs4('<a href="#" class="biddingLink">[lic]</a>')
                # TODO: file_number, a nie deal_number
                bidding_link.a['data-bidding-link'] = path.basename(tournament_prefix) + '_bidding_' + str(deal_numbers[file_number]) + '_' + '_'.join(map(str, pair_numbers)) + '.txt'
                for link in cells[3].select('a.biddingLink'):
                    link.extract()
                cells[3].append(bidding_link)
        board_text.seek(0)
        board_text.write(board_text_content.body.table.prettify('iso-8859-2'))
