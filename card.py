class Card:
    def __init__(self, card_data):
        self.title = card_data[0]
        print(card_data)
        if type(card_data[1]) is str:
            self.subtitle = card_data[1].replace("\\n", "\n")
            self.credit_data_format = get_credit_format(card_data[2])
            self.credits = credit_format(card_data[2:])
        else:
            self.subtitle = ''
            self.credit_data_format = get_credit_format(card_data[1])
            self.credits = credit_format(card_data[1:])

def parse(line):
    if not ''.join(line[1:]):
        return line[0]
    return line

def credit_format(credit_data):
    credit_1 = []
    credit_2 = []
    credit_format_type = get_credit_format(credit_data[0])
    for credit_line in credit_data:
        match credit_format_type:
            case 'single':
                if ''.join(credit_line):
                    credit_1.append(tuple(credit_line[1:-1]))
            case 'double':
                if ''.join(credit_line[:2]):
                    credit_1.append(tuple(credit_line[0:2]))
                if ''.join(credit_line[2:]):
                    credit_2.append(tuple(credit_line[2:]))
            case 'special':
                if ''.join(credit_line):
                    credit_1.append(credit_line[1])

    consolidated_credits = credit_1 + credit_2

    credit_list = []
    position_list = {}
    for credit in consolidated_credits:
        if credit_format_type == 'special':
            credit_list.append(credit)
        elif credit[0]:
            if position_list:
                position_list['names'] = sorted(position_list['names'])
                credit_list.append(position_list)
                position_list = {}
            position_list['position'] = credit[0]
            position_list['names'] = [credit[1]]
        else:
            position_list['names'].append(credit[1])
    if credit_format_type != 'special':
        position_list['names'] = sorted(position_list['names'])
        credit_list.append(position_list)
    return credit_list

def get_credit_format(credit_line):
    columns = len(list(filter(None, credit_line)))

    match columns:
        case 1:
            return 'special'
        case 2:
            return 'single'
        case 4:
            return 'double'
        case _:
            return 'error'