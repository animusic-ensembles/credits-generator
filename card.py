import copy

class Card:
    def __init__(self, card_data):
        self.title = card_data[0]
        if type(card_data[1]) is str:
            self.subtitle = card_data[1]
            self.credits = copy.deepcopy(credit_format(card_data[2:]))
            self.lines = calculate_lines(card_data[2:])
        else:
            self.subtitle = ''
            self.credits = copy.deepcopy(credit_format(card_data[1:]))
            self.lines = calculate_lines(card_data[2:])
        #print(self.credits)

def parse(line):
    if ''.join(line[1:]) == '':
        return line[0]
    if line[0] == '' and line[-1] == '':
        return tuple(line[1:-1])
    return [tuple(line[:2]), tuple(line[2:])]

def credit_format(credit_data):
    credit_1 = []
    credit_2 = []
    for credit_line in credit_data:
        if type(credit_line) is tuple:
            if ''.join(credit_line) != '':
                credit_1.append(credit_line)
        else:
            if ''.join(credit_line[0]) != '':
                credit_1.append(credit_line[0])
            if ''.join(credit_line[1]) != '':
                credit_2.append(credit_line[1])
    consolidated_credits = credit_1 + credit_2

    credit_list = []
    position_list = {}
    for credit in consolidated_credits:
        if credit[0]:
            if position_list:
                credit_list.append(position_list)
                position_list = {}
            position_list['position'] = credit[0]
            position_list['names'] = [credit[1]]
        else:
            position_list['names'].append(credit[1])
    credit_list.append(position_list)
    return credit_list

def calculate_lines(credit_data):
    credit_1 = []
    credit_2 = []
    for credit_line in credit_data:
        if type(credit_line) is tuple:
            credit_1.append(credit_line)
        else:
            credit_1.append(credit_line[0])
            credit_2.append(credit_line[1])
    return len(credit_1 + credit_2)