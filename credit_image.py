from PIL import Image, ImageDraw, ImageFont
import math

margins = 60
title_size = 36
font_size = 32
spacing = 16
title_font = ImageFont.truetype('font/Roboto-Regular.ttf', size=title_size)
regular_font = ImageFont.truetype('font/Roboto-Regular.ttf', size=font_size)
light_font = ImageFont.truetype('font/Roboto-Light.ttf', size=font_size)


def generate(card):
    image = Image.new(mode='RGBA', size=(1920, 1080))
    draw = ImageDraw.Draw(image)

    credit_lines = []
    title_height = font_size + spacing
    subtitle_height = 0
    if card.subtitle:
        subtitle_height = font_size + 2 * spacing
    else:
        title_height += 3 * spacing / 2
    bounding_box = (1920 - 2 * margins, 1080 - 2 * margins - (title_height + subtitle_height))
    current_height = 0
    max_height = 0
    credit_height = 0
    if card.credit_data_format == 'special':
        credit_height = len(card.credits) * (font_size + spacing)
    else:
        for position in card.credits:
            credit_height += len(position['names']) * (font_size + spacing)
    estimated_height = credit_height / math.ceil(credit_height / bounding_box[1])

    position_avg_length = 0
    position_count = 0
    name_avg_length = 0
    name_count = 0
    position_list = ''
    name_list = ''
    if card.credit_data_format == 'special':
        for credit in card.credits:
            if current_height + font_size + spacing > estimated_height + spacing:
                credit_lines.append(name_list)
                max_height = max(max_height, current_height)
                current_height = 0
                name_list = ''
            name_list += credit + '\n'
            current_height += font_size + spacing
        credit_lines.append(name_list)
        max_height = max(max_height, current_height)
    else:
        for position in card.credits:
            if current_height + len(position['names']) * (font_size + spacing) > estimated_height + spacing:
                position_avg_length /= position_count
                name_avg_length /= name_count
                credit_lines.append((position_list, name_list, (position_avg_length, name_avg_length)))
                max_height = max(max_height, current_height)
                current_height = 0
                position_avg_length = 0
                name_avg_length = 0
                position_list = ''
                name_list = ''
            position_list += position['position'] + len(position['names']) * '\n'
            name_list += '\n'.join(position['names']) + '\n'
            current_height += len(position['names']) * (font_size + spacing)
            position_avg_length += draw.textlength(position['position'], font=light_font, font_size=font_size)
            position_count += len(position['names'])
            for name in position['names']:
                name_avg_length += draw.textlength(name, font=regular_font, font_size=font_size)
                name_count += 1
        position_avg_length /= position_count
        name_avg_length /= name_count
        credit_lines.append((position_list, name_list, (position_avg_length, name_avg_length)))
        max_height = max(max_height, current_height)

    total_height = max_height + title_height + subtitle_height
    draw.text(xy=(1920 / 2, 1080 / 2 - total_height / 2 + title_size), text=card.title,
              fill='white', font=title_font, anchor='ms', align='center', font_size=title_size)
    if card.subtitle:
        draw.text(xy=(1920 / 2, 1080 / 2 - total_height / 2 + title_height + font_size), text=card.subtitle,
                  fill='white', font=light_font, anchor='ms', align='center', font_size=font_size)

    match len(credit_lines):
        case 1:
            line_x_poses = [1920 / 2]
            line_align = ['center']
        case 2:
            line_x_poses = [bounding_box[0] / 3 + margins, bounding_box[0] * 2 / 3 + margins]
            line_align = ['center', 'center']
        case 3:
            line_x_poses = [margins, 1920 / 2, 1920 - margins]
            line_align = ['left', 'center', 'right']
        case _:
            line_x_poses = []
            line_align = []
    for i in range(len(credit_lines)):
        if card.credit_data_format != 'special':
            lengths = credit_lines[i][2]
            width = lengths[0] + lengths[1] + 2 * spacing
        y = 1080 / 2 - total_height / 2 + title_height + subtitle_height
        if card.credit_data_format == 'special':
            x = line_x_poses[i]
            match line_align[i]:
                case 'left':
                    draw.text(xy=(x, y,), text=credit_lines[i], fill='white', font=regular_font, anchor='la',
                              spacing=spacing, align='center', font_size=font_size)
                case 'center':
                    draw.text(xy=(x, y,), text=credit_lines[i], fill='white', font=regular_font, anchor='ma',
                              spacing=spacing, align='center', font_size=font_size)
                case 'right':
                    draw.text(xy=(x, y,), text=credit_lines[i], fill='white', font=regular_font, anchor='ra',
                              spacing=spacing, align='center', font_size=font_size)
        else:
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
            draw.text(xy=(position_x, y,), text=credit_lines[i][0], fill='white', font=light_font, anchor='ra',
                      spacing=spacing, align='right', font_size=font_size)
            draw.text(xy=(names_x, y,), text=credit_lines[i][1], fill='white', font=regular_font, anchor='la',
                      spacing=spacing, align='left', font_size=font_size)

    return image