from PIL import Image, ImageDraw, ImageFont
import math

margins = 100
title_size = 28
font_size = 20
small_size = 16
title_font = ImageFont.truetype('font/NotoSansJP-Regular.ttf', size=title_size)
regular_font = ImageFont.truetype('font/NotoSansJP-Regular.ttf', size=font_size)
small_font = ImageFont.truetype('font/NotoSansJP-Regular.ttf', size=small_size)
light_font = ImageFont.truetype('font/NotoSansJP-Light.ttf', size=font_size)
small_light_font = ImageFont.truetype('font/NotoSansJP-Light.ttf', size=small_size)


def generate(card, is_small):
    image = Image.new(mode='RGBA', size=(1920, 1080))
    draw = ImageDraw.Draw(image)
    title_line_height = sum(title_font.getmetrics())
    line_height = sum(small_font.getmetrics()) if is_small else sum(regular_font.getmetrics())
    line_spacing = small_font.getbbox("A")[3] if is_small else regular_font.getbbox("A")[3]
    spacing = line_height - line_spacing

    credit_lines = []
    title_height = title_line_height + 2 * spacing
    subtitle_height = 0
    if card.subtitle:
        subtitle_height = line_height + 2 * spacing
    else:
        title_height += 3 * spacing / 2
    bounding_box = (1920 - 2 * margins, 1080 - 2 * margins - (title_height + subtitle_height))
    current_height = 0
    max_height = 0
    max_pos_height = 0
    credit_height = 0
    if card.credit_data_format == 'special':
        credit_height = len(card.credits) * line_height
    else:
        for position in card.credits:
            credit_height += len(position['names']) * line_height
            max_pos_height = max(max_pos_height, len(position['names']) * line_height)
    estimated_height = credit_height / math.ceil(credit_height / bounding_box[1])
    if credit_height > estimated_height and estimated_height * 4 / 5 < max_pos_height:
        estimated_height = (credit_height - max_pos_height) / math.ceil((credit_height - max_pos_height) / max_pos_height)
    position_max_length = 0
    position_avg_length = 0
    position_count = 0
    name_max_length = 0
    name_avg_length = 0
    name_count = 0
    position_list = ''
    name_list = ''
    if card.credit_data_format == 'special':
        for credit in card.credits:
            if current_height + line_height > estimated_height + spacing:
                credit_lines.append(name_list)
                max_height = max(max_height, current_height)
                current_height = 0
                name_list = ''
            name_list += credit + '\n'
            current_height += line_height
        credit_lines.append(name_list)
        max_height = max(max_height, current_height)
    else:
        for position in card.credits:
            if current_height + len(position['names']) * line_height > estimated_height:
                position_avg_length /= position_count
                name_avg_length /= name_count
                credit_lines.append((position_list, name_list, (position_avg_length, name_avg_length), (position_max_length, name_max_length)))
                max_height = max(max_height, current_height)
                current_height = 0
                position_avg_length = 0
                name_avg_length = 0
                position_list = ''
                name_list = ''
            position_list += position['position'] + len(position['names']) * '\n'
            name_list += '\n'.join(position['names']) + '\n'
            current_height += len(position['names']) * line_height
            position_length = draw.textlength(position['position'], font=small_light_font if is_small else light_font, font_size=small_size if is_small else font_size)
            position_max_length = max(position_max_length, position_length)
            position_avg_length += position_length
            position_count += len(position['names'])
            for name in position['names']:
                name_length = draw.textlength(name, font=small_font if is_small else regular_font, font_size=small_size if is_small else font_size)
                name_max_length = max(name_max_length, name_length)
                name_avg_length += name_length
                name_count += 1
        position_avg_length /= position_count
        name_avg_length /= name_count
        credit_lines.append((position_list, name_list, (position_avg_length, name_avg_length), (position_max_length, name_max_length)))
        max_height = max(max_height, current_height)

    total_height = max_height + title_height + subtitle_height
    print(card.title)
    print(title_height, subtitle_height, total_height, bounding_box[1])
    draw.text(xy=(1920 / 2, 1080 / 2 - total_height / 2 + title_size), text=card.title,
              fill='white', font=title_font, anchor='ms', align='center', font_size=title_size)
    if card.subtitle:
        draw.text(xy=(1920 / 2, 1080 / 2 - total_height / 2 + title_height + font_size), text=card.subtitle,
                  fill='white', font=small_light_font if is_small else light_font, anchor='ms', align='center', font_size=small_size if is_small else font_size)
    # for i in range(len(credit_lines)):
    #     print(i)
    #     print(credit_lines[i][0].count('\n'))
    #     print(credit_lines[i][:2])
    match len(credit_lines):
        case 1:
            line_x_poses = [1920 / 2]
            line_align = ['center']
        case 2:
            line_x_poses = [bounding_box[0] / 3 + margins, bounding_box[0] * 2 / 3 + margins]
            line_align = ['center', 'center']
        case 3:
            line_x_poses = [2 * margins, 1920 / 2, 1920 - 2 * margins]
            line_align = ['left', 'center', 'right']
        case _:
            line_x_poses = []
            line_align = []
    for i in range(len(credit_lines)):
        y = 1080 / 2 - total_height / 2 + title_height + subtitle_height
        if card.credit_data_format != 'special':
            if len(credit_lines) == 3 and (i == 0 or i == 2):
                lengths = credit_lines[i][3]
            else:
                lengths = credit_lines[i][2]
            width = lengths[0] + lengths[1] + 2 * spacing
            
            match line_align[i]:
                case 'left':
                    position_x = line_x_poses[i] + lengths[0]
                    names_x = line_x_poses[i] + lengths[0] + 2 * spacing
                case 'center':
                    position_x = line_x_poses[i] - width / 2 + lengths[0]
                    names_x = line_x_poses[i] + width / 2 - lengths[1]
                case 'right':
                    position_x = line_x_poses[i] - lengths[1] - 2 * spacing
                    names_x = line_x_poses[i] - lengths[1]
                case _:
                    position_x = -1920
                    names_x = -1920
            draw.text(xy=(position_x, y,), text=credit_lines[i][0], fill='white', font=small_light_font if is_small else light_font, anchor='ra',
                      spacing=spacing, align='right', font_size=small_size if is_small else font_size)
            draw.text(xy=(names_x, y,), text=credit_lines[i][1], fill='white', font=small_font if is_small else regular_font, anchor='la',
                      spacing=spacing, align='left', font_size=small_size if is_small else font_size)
        else:
            x = line_x_poses[i]
            match line_align[i]:
                case 'left':
                    draw.text(xy=(x, y,), text=credit_lines[i], fill='white', font=small_font if is_small else regular_font, anchor='la',
                              spacing=spacing, align='center', font_size=small_size if is_small else font_size)
                case 'center':
                    draw.text(xy=(x, y,), text=credit_lines[i], fill='white', font=small_font if is_small else regular_font, anchor='ma',
                              spacing=spacing, align='center', font_size=small_size if is_small else font_size)
                case 'right':
                    draw.text(xy=(x, y,), text=credit_lines[i], fill='white', font=small_font if is_small else regular_font, anchor='ra',
                              spacing=spacing, align='center', font_size=small_size if is_small else font_size)

    return image