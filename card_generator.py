import math
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import pandas as pd

COLS = 3
ROWS = 3
UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3

CENTER = 0.5
MAX = 1
MARGIN = 0.07
IMAGE_SIZE = 30

OUTPUT_FILE = "cards.pdf"
DATA_FILE_PATH = "data.csv"

LIFE_IMAGE_PATH = "life.png"
SCHOOL_IMAGE_PATH = "school.png"
HEALTH_IMAGE_PATH = "health.png"
PLACE_CARD_PATH = "place.png"
DISCARD_CARD_PATH = "discard.png"
TIME_IMAGE_PATH = "time.png"

TITLE_KEY = "title"
CONTENT_KEY = "content"
DISCARD_KEY = "discard"
TYPE_KEY = "type"

GAME_TITLE = "Don't Fail (Your Classes)"

FONT_BOLD = "Times-Bold"
FONT_NORMAL = "Times-Roman"
FONT_ITALIC = "Times-Italic"

SMALL_FONT_SIZE = 12
MEDIUM_FONT_SIZE = 14
LARGE_FONT_SIZE = 16
HUGE_FONT_SIZE = 18


LIFE = 0
SCHOOL = 1
HEALTH = 2
OTHER = 3

CHOICE_CARD = 0
TIME_CARD = 1

TIME_CARD_COUNT = 7

CREATE_BACK = True

def wrap_text(text, width=20):
    result = []
    current = ""
    for i,c in enumerate(text):
        current += c
        if (len(current) > 10 and c == " "):
            result.append(current)
            current = ""
    if (len(current) > 0):
        result.append(current)
    return result

# Maps directions to anchor positions on card
placements = [(CENTER,MAX-MARGIN),(MAX-MARGIN,CENTER),(CENTER,MARGIN),(MARGIN,CENTER)]

def create_choice_card(c, data, x, y, width, height):
    c.setFont(FONT_BOLD, SMALL_FONT_SIZE)
    c.setFillColorRGB(0, 0, 0)

    valid = validateChoiceCardData(data)
    if not valid:
        errorText = "Invalid Card"
        text_width = c.stringWidth(errorText)
        c.drawString(x+(width-text_width)/2, y+width/2, errorText)
        return
    
    
    title = data[TITLE_KEY]
    
    text_width = c.stringWidth(title)
    text_height = SMALL_FONT_SIZE
    wrapped_lines = wrap_text(title)
   
    start_y = y + (height + len(wrapped_lines)//2*text_height)/2 
    for i, line in enumerate(wrapped_lines):
        text_width = c.stringWidth(line)
        centered_x = x + (width - text_width) / 2
        current_y = start_y - (i * text_height) 
        c.drawString(centered_x, current_y, line)
    

    content = data[CONTENT_KEY]
    farthest_effect = 0
    for i in range(0,len(content)):
        if len(content[i]) > 0:
            farthest_effect = i

    for i in range(0,farthest_effect+1):
        (x_anchor, y_anchor) = placements[i]
        draw_card_choice_content(c,x,y,width,height,x_anchor,y_anchor,i,content[i])
    
    discard = data['discard']
    if (discard == 'F'):
        path = DISCARD_CARD_PATH
    else:
        path = PLACE_CARD_PATH
    c.drawImage(path,x+(width-IMAGE_SIZE)/2,start_y-len(wrapped_lines)*text_height-IMAGE_SIZE/2-5, IMAGE_SIZE, IMAGE_SIZE,mask='auto')

def create_time_card(c, data, x, y, width, height):
    c.setFont(FONT_BOLD, MEDIUM_FONT_SIZE)
    c.setFillColorRGB(0, 0, 0)

    timeText = "Time Passes"
    text_width = c.stringWidth(timeText)
    c.drawString(x+(width-text_width)/2, y+height/2, timeText)
    c.drawImage(TIME_IMAGE_PATH,x+(width-IMAGE_SIZE)/2,y+(height-IMAGE_SIZE)/2-20, IMAGE_SIZE, IMAGE_SIZE,mask='auto')

def create_card_front(c, data, x, y, width, height):
    c.setFillColorRGB(1,1,1)
    c.rect(x, y, width, height, fill=True)
    if (TYPE_KEY not in data.keys()):
        errorText = "Unknown Type"
        text_width = c.stringWidth(errorText)
        c.drawString(x+(width-text_width)/2, y+width/2, errorText)
    type = data[TYPE_KEY]
    if (type == CHOICE_CARD):
        create_choice_card(c,data,x,y,width,height)
    elif (type == TIME_CARD):
        create_time_card(c,data,x,y,width,height)
    

def validateChoiceCardData(data):
    valid = True
    keys = data.keys()
    
    required_keys = [TITLE_KEY,CONTENT_KEY,DISCARD_KEY]
    for key in required_keys:
        if (key not in keys):
            print(f"Warning: key {key} not in {data}")
            valid = False
    return valid

def draw_card_choice_content(c, x, y, width, height, anchor_x, anchor_y, direction, content):
    text_width = c.stringWidth(str(direction+1))
    text_height = 0
    PADDING = 20
    paddingDirection = -1
    if (direction == LEFT or direction == RIGHT):
        (text_height,text_width) = (text_width,text_height)
        text_width = 0
        paddingDirection = -1
    if (direction == DOWN):
        text_width *= -1
        text_height *= -1
    if (direction == RIGHT):
        text_height *= -1
    centered_x = x + (width-text_width) * anchor_x
    centered_y = y + (height-text_height) * anchor_y
    
    c.saveState()
    c.translate(centered_x, centered_y)
    
    c.rotate(direction * -90)

    c.setFont(FONT_BOLD, HUGE_FONT_SIZE)
    c.drawString(0, 0, str(direction+1))
    
    c.setFont(FONT_NORMAL, SMALL_FONT_SIZE)
    image_count = 0
    images = {HEALTH:HEALTH_IMAGE_PATH,LIFE:LIFE_IMAGE_PATH,SCHOOL:SCHOOL_IMAGE_PATH}
    for key in content.keys():
        if (key in images):
            image_count += 1
    
    image_padding = IMAGE_SIZE+10
    image_offset = (image_count)//2*image_padding/2
    for i, key in enumerate(content.keys()):
        if (key in images):
            c.drawImage(images[key],-IMAGE_SIZE/2-image_offset+i*image_padding,-IMAGE_SIZE/2+paddingDirection*PADDING, IMAGE_SIZE, IMAGE_SIZE,mask='auto')
            image_text = content[key]
            value = int(image_text)
            if (value > 0):
                c.setFillColorRGB(1/255, 64/255, 2/255)
            else:
                c.setFillColorRGB(64/255, 6/255, 0/255)
            c.setFont(FONT_NORMAL, LARGE_FONT_SIZE)
            contentWidth = c.stringWidth(image_text)
            c.drawString(-contentWidth/2+IMAGE_SIZE/2-image_offset+i*image_padding, paddingDirection*PADDING+IMAGE_SIZE/4+2, image_text)
        else:
            contentWidth = c.stringWidth(content[key])
            c.drawString(-contentWidth/2, paddingDirection*PADDING, content[key])
    c.setFillColorRGB(0, 0, 0)

    if (len(content) == 0):
        c.setFont(FONT_ITALIC, SMALL_FONT_SIZE)
        content = "No Effect"
        contentWidth = c.stringWidth(content)
        c.drawString(-contentWidth/2, paddingDirection*PADDING, content)
    
    c.restoreState()

def create_card_back(c, x, y, width, height):
    c.setFillColorRGB(1, 1, 1)
    c.rect(x, y, width, height, fill=True)
    c.setFont(FONT_BOLD, MEDIUM_FONT_SIZE)
    c.setFillColorRGB(0, 0, 0)
    
    text_width = c.stringWidth(GAME_TITLE)
    text_height = MEDIUM_FONT_SIZE
    centered_x = x + (width - text_width) / 2

    c.drawString(centered_x, y+(height-text_height)/2, GAME_TITLE)

def generate_pdf(cards):
    page_width, page_height = letter
    c = canvas.Canvas(OUTPUT_FILE, pagesize=letter)

    y_offset = page_height

    card_width = page_width/COLS
    card_height = card_width
    
    cards_per_page = ROWS * COLS

    FRONT = 0
    BACK = 1
    if (CREATE_BACK):
        modes = [FRONT,BACK]
    else:
        modes = [FRONT]
    
    page = 0
    i = 0
    mode_index = 0
    card_index = 0
    while card_index < len(cards):
        card = cards[card_index]
        mode = modes[mode_index]
        
        idx = page * cards_per_page+i

        x = idx % COLS * card_width
        y = y_offset - (((idx // COLS)% ROWS+1) * card_height)
        if (mode == FRONT):
            create_card_front(c, card, x, y, card_width, card_height)
        elif (mode == BACK):
            create_card_back(c, x, y, card_width, card_height)
        i += 1
        
        if (i >= cards_per_page):
            mode_index += 1
            if (mode_index < len(modes)):
                card_index -= cards_per_page
            else:
                mode_index = 0
            page += 1
            i = 0
            c.showPage()
        card_index += 1
    print(f"Created {len(cards)} Cards on {page} Pages")
    c.save()

def parse_effects(effect_data):
    categories = {"life":LIFE,"health":HEALTH,"school":SCHOOL}
    data = {}
    if (not isinstance(effect_data, str)):
        return data
    words = effect_data.split(" ")
   
    i = 0
    while i < len(words):
        word = words[i]
        lower = word.lower()
        if (lower in categories):
            data[categories[lower]] = words[i+1]
            i += 2
            continue
        if (OTHER not in data.keys()):
            data[OTHER] = ""
        data[OTHER] += words[i] + " " 
        i += 1
    return data
    
def cvs_to_dict(df):
    TITLE_INDEX = 0
    CONTENT_LOWER_INDEX = 1
    CONTENT_UPPER_INDEX = 5
    DISCARD_INDEX = 5
    COUNT_INDEX = 6
    
    data = []
    for index, row in df.iterrows():
        row_data = {TYPE_KEY:CHOICE_CARD}
        title = row.iloc[TITLE_INDEX]
        if (title == "TEMPLATE"): 
            continue
        row_data[TITLE_KEY] = title
        content = []
        effects =  row.iloc[CONTENT_LOWER_INDEX:CONTENT_UPPER_INDEX]
        for effect in effects:
            content.append(parse_effects(effect))
        row_data[CONTENT_KEY] = content
        row_data[DISCARD_KEY] = row.iloc[DISCARD_INDEX]
        count = format_count_data(row.iloc[COUNT_INDEX])
        while (count > 0):
            data.append(row_data)
            count -= 1
    return data

def format_count_data(count_data):
    DEFAULT_COUNT = 1
    if (count_data is None):
        return DEFAULT_COUNT
    try:
        return int(count_data)
    except (ValueError, TypeError):
        return DEFAULT_COUNT

def count_stats(card_data):
    POSITIVE = 0
    NEGATIVE = 1
    EFFECT_COUNT = 3
    results = {}
    for i in range(0,EFFECT_COUNT):
        results[i] = {POSITIVE:0,NEGATIVE:0}
    
    for data in card_data:
        keys = data.keys()
        if (TYPE_KEY not in keys):
            continue
        type = data[TYPE_KEY]
        if (type != CHOICE_CARD):
            continue
        if (CONTENT_KEY not in keys):
            continue
        content = data[CONTENT_KEY]
        for i in range(0,EFFECT_COUNT):
            for effects in content:
                if (i in effects.keys()):
                    value = effects[i]
                    int_value = int(value)
                    if (int(value) < 0):
                        results[i][NEGATIVE] += int_value
                    else:
                        results[i][POSITIVE] += int_value
    
    def print_result(header, positive, negative):
        print(header + str(positive) + " & " + str(negative) + ",Sum=" + str(positive+negative))
    print(15*"="+ "Data Results" + 15 * "=")
    print_result("Health",results[HEALTH][POSITIVE],results[HEALTH][NEGATIVE])
    print_result("Life",results[LIFE][POSITIVE],results[LIFE][NEGATIVE])
    print_result("School",results[SCHOOL][POSITIVE],results[SCHOOL][NEGATIVE])


if __name__ == "__main__":
    df = pd.read_csv(DATA_FILE_PATH)
    card_data = cvs_to_dict(df)
    #count_stats(card_data)
    #for i in range(TIME_CARD_COUNT):
        #card_data.append({TYPE_KEY:TIME_CARD})
    generate_pdf(card_data)