"""
Python script for creating foldable, mailable radiogram
Uses tkinter pulldown menu to choose the .m2s file from flmsg

Started 8 March 2026

v. 7: 9 March 2026
TODO: Format a little better9 
v. 8: DK March 2026
Put in light boxes for words
v. 9: 4 April 2026
Get the back of mailer orientation right.
v. 10:4 April 2026
Get the parsing of the address line correct
Did that.
TODO:
Fill in remaining ARRL numbered radiograms
Include return address on mailing side
v. 11:05July2026
Added return address method.
Looks for .txt file in directory that has Python code.
If present, adds it as a return address label.
v. 12:08 July 2026
Adding additional ARRL numbered radiograms and including metadata field
v. 12: 09 July 2026
Added all ARRL numbered radiograms with metadata for number of blanks to fill in
v. 14: 11 July 2026
Changing the parser to accept text after numbered radiograms that use fill-ins.
v. 15 13 July 2026 Continuing the parser rewrite

"""



from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# for pulldown file menu:
import tkinter as tk
from tkinter import filedialog
import os

# for formatting the boilerplate paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

PAGE_WIDTH, PAGE_HEIGHT = letter

# ---------------------------------------------------------

# Precedence mapping

# ---------------------------------------------------------

PRECEDENCE_MAP = {
"0": "ROUTINE",
"1": "W",
"2": "PRIORITY",
"3": "EMERGENCY"
}

# ---------------------------------------------------------

# ARRL numbered radiogram support

# ---------------------------------------------------------

NUMBER_WORDS = {
"ZERO":0,"ONE":1,"TWO":2,"THREE":3,"FOUR":4,"FIVE":5,
"SIX":6,"SEVEN":7,"EIGHT":8,"NINE":9,"TEN":10,
"ELEVEN":11,"TWELVE":12,"THIRTEEN":13,"FOURTEEN":14,
"FIFTEEN":15,"SIXTEEN":16,"SEVENTEEN":17,"EIGHTEEN":18,"NINETEEN":19,
"TWENTY":20,"THIRTY":30,"FORTY":40,"FIFTY":50,"SIXTY":60,
"SEVENTY":70,"EIGHTY":80,"NINETY":90
}

MONTHS = {
    "JAN","JANUARY","FEB","FEBRUARY","MAR","MARCH",
    "APR","APRIL","MAY","JUN","JUNE","JUL","JULY",
    "AUG","AUGUST","SEP","SEPT","SEPTEMBER",
    "OCT","OCTOBER","NOV","NOVEMBER","DEC","DECEMBER"
}

def parser_msg_to_date_time(words, upper, start, fields):
    """
    Parser for ARL 47:
        message number
        addressee
        delivery date
        UTC time
    """

    if start + 1 >= len(words):
        return parser_first_rest(words, upper, start, fields)

    # first two fields
    msg_number = words[start]
    addressee = words[start + 1]

    j = start + 2

    # date
    date_words = []

    if j < len(words) and upper[j] in MONTHS:
        date_words.append(words[j])
        j += 1

        if j < len(words):
            date_words.append(words[j])
            j += 1

    # time
    utc = ""

    if j < len(words):
        utc = words[j]
        j += 1

    return [msg_number,
            addressee,
            " ".join(date_words),
            utc], j


ARL_TEXT = {
#
# Group One—For Possible Relief Emergency Use
#
1: {
    "text": "Everyone safe here. Please don't worry.",
    "fields": 0,
},
2: {
    "text": "Coming home as soon as possible.",
    "fields": 0,
},
3: {
    "text": "Am in _____ hospital. Receiving excellent care and recovering fine.",
    "fields": 1,
},
4: {
    "text": "Only slight property damage here. Do not be concerned about disaster reports.",
    "fields": 0,
},
5: {
    "text": "Am moving to new location. Send no further mail or communication. Will inform you of new address when relocated.",
    "fields": 0,
},
6: {
    "text": "Will contact you as soon as possible.",
    "fields": 0,
},
7: {
    "text": "Please reply by Amateur Radio through the amateur delivering this message. This is a free public service.",
    "fields": 0,
},
8: {
    "text": "Need additional _____ mobile or portable equipment for immediate emergency use.",
    "fields": 1,
},
9: {
    "text": "Additional _____ radio operators needed to assist with emergency at this location.",
    "fields": 1,
},
10: {
    "text": "Please contact _____. Advise to standby and provide further emergency information, instructions or assistance.",
    "fields": 1,
},
11: {
    "text": "Establish Amateur Radio emergency communications with _____ on _____ MHz.",
    "fields": 2,
},
12: {
    "text": "Anxious to hear from you. No word in some time. Please contact me as soon as possible.",
    "fields": 0,
},
13: {
    "text": "Medical emergency situation exists here.",
    "fields": 0,
},
14: {
    "text": "Situation here becoming critical. Losses and damage from _____ increasing.",
    "fields": 1,
},
15: {
    "text": "Please advise your condition and what help is needed.",
    "fields": 0,
},
16: {
    "text": "Property damage very severe in this area.",
    "fields": 0,
},
17: {
    "text": "REACT communications services also available. Establish REACT communication with _____ on channel _____.",
    "fields": 2,
},
18: {
    "text": "Please contact me as soon as possible at _____.",
    "fields": 1,
},
19: {
    "text": "Request health and welfare report on _____. (State name, address and telephone number.)",
    "fields": 1,
},
20: {
    "text": "Temporarily stranded. Will need some assistance. Please contact me at _____.",
    "fields": 1,
},
21: {
    "text": "Search and Rescue assistance is needed by local authorities here. Advise availability.",
    "fields": 0,
},
22: {
    "text": "Need accurate information on the extent and type of conditions now existing at your location. Please furnish this information and reply without delay.",
    "fields": 0,
},
23: {
    "text": "Report at once the accessibility and best way to reach your location.",
    "fields": 0,
},
24: {
    "text": "Evacuation of residents from this area urgently needed. Advise plans for help.",
    "fields": 0,
},
25: {
    "text": "Furnish as soon as possible the weather conditions at your location.",
    "fields": 0,
},
26: {
    "text": "Help and care for evacuation of sick and injured from this location needed at once.",
    "fields": 0,
},
27: {
    "text": "I am safe and well.",
    "fields": 0,
},
28: {
    "text": "Household safe and well.",
    "fields": 0,
},
29: {
    "text": "Currently at shelter.",
    "fields": 0,
},
30: {
    "text": "Currently at home.",
    "fields": 0,
},
31: {
    "text": "Currently at family/friend's house.",
    "fields": 0,
},
32: {
    "text": "Currently at hotel.",
    "fields": 0,
},
33: {
    "text": "Safe but moving to a safer location.",
    "fields": 0,
},
34: {
    "text": "Evacuating to a shelter.",
    "fields": 0,
},
35: {
    "text": "Evacuating to family member/friend's house.",
    "fields": 0,
},
36: {
    "text": "Evacuating and safe.",
    "fields": 0,
},
37: {
    "text": "At home and plan to remain here.",
    "fields": 0,
},
38: {
    "text": "Will contact you when able.",
    "fields": 0,
},
39: {
    "text": "All communications are down.",
    "fields": 0,
},
40: {
    "text": "Share this message with others.",
    "fields": 0,
},
#
# Group Two—Routine Messages
#
46: {
    "text": "Greetings on your birthday and best wishes for many more to come.",
    "fields": 0,
},
47: {
    "text": "Reference your message number _____ to _____ delivered on _____ at _____ UTC.",
    "fields": 4,
    "parser": parser_msg_to_date_time, # added to correct two space parser need 13 July 2026
},
48: {
    "text": "Reference your message number _____ to _____ not delivered. Telephone _____ (insert number as received) inoperative. Please give better address.",
    "fields": 3,
},
49: {
    "text": "Reference your message number _____ to _____. Unable to contact addressee or receive confirmation of delivery.",
    "fields": 2,
},
50: {
    "text": "Greetings by Amateur Radio.",
    "fields": 0,
},
51: {
    "text": "Greetings by Amateur Radio. This message is sent as a free public service by ham radio operators at _____. Am having a wonderful time.",
    "fields": 1,
},
52: {
    "text": "Really enjoyed being with you. Looking forward to getting together again.",
    "fields": 0,
},
53: {
    "text": "Received your _____. It's appreciated; many thanks.",
    "fields": 1,
},
54: {
    "text": "Many thanks for your good wishes.",
    "fields": 0,
},
55: {
    "text": "Good news is always welcome. Very delighted to hear about yours.",
    "fields": 0,
},
56: {
    "text": "Congratulations on your _____, a most worthy and deserved achievement.",
    "fields": 1,
},
57: {
    "text": "Wish we could be together.",
    "fields": 0,
},
58: {
    "text": "Have a wonderful time. Let us know when you return.",
    "fields": 0,
},
59: {
    "text": "Congratulations on the new arrival. Hope mother and child are well.",
    "fields": 0,
},
60: {
    "text": "Wishing you the best of everything on _____.",
    "fields": 1,
},
61: {
    "text": "Wishing you a very Merry Christmas and a Happy New Year.",
    "fields": 0,
},
62: {
    "text": "Greetings and best wishes to you for a pleasant _____ holiday season.",
    "fields": 1,
},
63: {
    "text": "Victory or defeat, our best wishes are with you. Hope you win.",
    "fields": 0,
},
64: {
    "text": "Arrived safely at _____.",
    "fields": 1,
},
65: {
    "text": "Arriving _____ on _____. Please arrange to meet me there.",
    "fields": 2,
},
66: {
    "text": "DX QSLs are on hand for you at the _____ QSL Bureau. Send _____ self addressed envelopes.",
    "fields": 2,
},
67: {
    "text": "Your message number _____ undeliverable because of _____. Please advise.",
    "fields": 2,
},
68: {
    "text": "Sorry to hear you are ill. Best wishes for a speedy recovery.",
    "fields": 0,
},
69: {
    "text": "Welcome to the _____. We are glad to have you with us and hope you will enjoy the fun and fellowship of the organization.",
    "fields": 1,
},
70: {
    "text": "Thank you for the QSO on _____ (frequency/band) _____ (mode) at _____ (time) _____ (date).",
    "fields": 4,
},
71: {
    "text": "Order wire net established on _____ (frequency) to coordinate and prioritize access to _____ (digital network name) on _____ (frequency) _____ (mode).",
    "fields": 4,
},
72: {
    "text": "Establish communications with _____ (name of EmComm group) on _____ frequency _____ mode.",
    "fields": 3,
},
73: {
    "text": "Establish communications with _____ agency on channel _____ (spell channel number) _____ (mode).",
    "fields": 3,
},
74: {
    "text": "Establish communications with _____ agency on _____ (frequency) _____ mode.",
    "fields": 3,
},
75: {
    "text": "Priority Entry Point frequencies established on _____ (list frequencies and modes).",
    "fields": 1,
},
76: {
    "text": "Point to point circuit established on _____ (frequency) _____ (mode). Please establish liaison.",
    "fields": 2,
},
78: {
    "text": "SITREP messages requested every _____ (spell number) hours your location. Transmit to station _____ (call sign) in _____ (state/section).",
    "fields": 3,
},
79: {
    "text": "WXOBS messages requested every _____ (spell number) hours your location. Transmit to station _____ (call sign) in _____ (state/section).",
    "fields": 3,
},
80: {
    "text": "OPRED messages requested your station. Update when changes occur. Transmit to station _____ (call sign) in _____ (state/section).",
    "fields": 2,
},
82: {
    "text": "Digital Traffic Station connect/download frequency at _____ (spell number) minute intervals requested in support of disaster operations.",
    "fields": 1,
},
83: {
    "text": "RRI Winlink gateway connect/download frequency at _____ (spell number) minute intervals requested in support of disaster operations.",
    "fields": 1,
},
84: {
    "text": "Request activate _____ Region Net until further notice.",
    "fields": 1,
},
85: {
    "text": "Request activate _____ Area Net until further notice.",
    "fields": 1,
},
86: {
    "text": "Advise frequency and mode of _____ state/section nets.",
    "fields": 1,
},
87: {
    "text": "Request assistance with establishment of a temporary message center at _____ (address and/or agency).",
    "fields": 1,
},
88: {
    "text": "Welfare traffic being originated on (frequency/mode). Request assistance with RRI/NTS liaison.",
    "fields": 0,
},
89: {
    "text": "Priority and/or emergency traffic being originated on _____ (frequency/mode). Request assistance with RRI/NTS liaison.",
    "fields": 1,
},
90: {
    "text": "Please provide a list of stations operational on National SOS Radio Network.",
    "fields": 0,
},
91: {
    "text": "Widespread disruptions to cellular data and public switched telephone network this location.",
    "fields": 0,
},
92: {
    "text": "Widespread disruptions to Internet service this location.",
    "fields": 0,
},
93: {
    "text": "The following broadcast stations are off-air in this area (list call sign, frequency/channel).",
    "fields": 1,
},
94: {
    "text": "Received your message _____ (number) for _____ (addressee) from _____ (station) _____ on _____ (date) _____ (time). Relayed/delivered to _____ (station) on _____ (date) _____ (time) via _____ (net/method) [Note: for use with handling instruction HXD]",
    "fields": 9,
},
}





# ---------------------------------------------------------

# Decode FLMSG length/value format

# Example: "2 85" → "85"

# ---------------------------------------------------------

def decode_flmsg_value(text):

    text = text.strip()
    parts = text.split(" ", 1) # 1 splits first element only

    # Only treat as FLMSG length field if length matches actual string length
    if len(parts) == 2 and parts[0].isdigit():
        length = int(parts[0])
        value = parts[1]

        # Only strip if length matches (prevents stripping street numbers)
        if len(value) == length:
            return value.strip()

    return text


# ---------------------------------------------------------

# Parse FLMSG radiogram (.m2s)

# ---------------------------------------------------------

def parse_flmsg_radiogram(filename):

    raw = {}
    current = None
    buffer = []

    with open(filename,"r",encoding="utf-8") as f:

        for line in f:

            line = line.rstrip()

            if line.startswith(":"):

                if current:
                    raw.setdefault(current, []).extend(buffer)
                    buffer.clear()

                parts = line.split(":",2)

                tag = parts[1]
                value = parts[2].strip() if len(parts)>2 else ""

                current = tag

                if value:
                    buffer.append(value)

            else:

                if current:
                    buffer.append(line)

        if current:
            raw.setdefault(current, []).extend(buffer)


    data = {
        "number":"",
        "prec":"",
        "station":"",
        "check":"",
        "date":"",
        "place":"",
        "address":[],
        "telephone":"",
        "message":"",
        "signature":""
    }


    if "nbr" in raw:
        data["number"] = decode_flmsg_value(raw["nbr"][0])

    if "prec" in raw:
        p = decode_flmsg_value(raw["prec"][0])
        data["prec"] = PRECEDENCE_MAP.get(p,p)

    if "sta" in raw:
        data["station"] = decode_flmsg_value(raw["sta"][0])

    if "org" in raw:
        data["place"] = decode_flmsg_value(raw["org"][0])

    if "ck" in raw:
        data["check"] = decode_flmsg_value(raw["ck"][0])
        
    if "d1" in raw:
        data["date"] = decode_flmsg_value(raw["d1"][0])

    if "sig" in raw:
        data["signature"] = decode_flmsg_value(raw["sig"][0])

    if "tel" in raw:
        data["telephone"] = decode_flmsg_value(raw["tel"][0])
        
    if "to" in raw: # needs special treatment because can be multiple lines
        addr_lines = []

        for i, x in enumerate(raw["to"]):

            x = x.strip()

            # ONLY strip length on first line
            if i == 0:
                parts = x.split(" ", 1)
                if len(parts) == 2 and parts[0].isdigit():
                    x = parts[1]

            addr_lines.append(x)

        data["address"] = addr_lines


    if "msg" in raw:
        msg_lines = []

        for i, x in enumerate(raw["msg"]):

            x = x.strip()

            if i == 0:
                parts = x.split(" ", 1)
                if len(parts) == 2 and parts[0].isdigit():
                    x = parts[1]

            msg_lines.append(x)

        data["message"] = " ".join(msg_lines)

    return data

# ---------------------------------------------------------
# Read return address if present
# ---------------------------------------------------------

def read_return_address():

    script_dir = os.path.dirname(os.path.abspath(__file__))

    filename = os.path.join(script_dir, "return_address.txt")

    if not os.path.exists(filename):
        return []

    with open(filename, "r", encoding="utf-8") as f:
        return [line.rstrip() for line in f if line.strip()]

# ---------------------------------------------------------

# Expand ARRL numbered radiograms

# ---------------------------------------------------------

def expand_arl_codes(words):

    result = []
    i = 0

    while i < len(words):

        if words[i] == "ARL":

            j = i + 1
            value = 0

            while j < len(words) and words[j] in NUMBER_WORDS:
                value += NUMBER_WORDS[words[j]]
                j += 1

            if value in ARL_TEXT:
                entry = ARL_TEXT[value]
                result.append(f"ARL {value} ({entry['text']})")
            else:
                result.append(f"ARL {value}")

            i = j
            continue

        result.append(words[i])
        i += 1

    return result

def expand_arl(text):

    words = text.upper().split()
    expanded = expand_arl_codes(words)

    return " ".join(expanded)

# ---------------------------------------------------------

# Radiogram message grid (5-word rows)

# ---------------------------------------------------------

def split_into_rows(words, size=5):

    rows = []

    for i in range(0, len(words), size):
        rows.append(words[i:i+size])

    return rows

# -------------
# Added to help put radiogram translations at bottom of text
# -------------

def fill_arl_template(template, values):
    """
    Replace successive occurrences of _____ with supplied values.
    """
    result = template

    for value in values:
        result = result.replace("_____", value, 1)

    return result

# ---------------------------------------------------------
# ARRL numbered radiogram parsers
# ---------------------------------------------------------

def parser_no_fields(words, upper, start, fields):
    """ARLs with no variable fields."""
    return [], start


def parser_remainder(words, upper, start, fields):
    """
    One field: everything until next ARL or end of message.
    """
    k = start

    while k < len(words) and upper[k] != "ARL":
        k += 1

    return [" ".join(words[start:k])], k


def parser_first_rest(words, upper, start, fields):
    """
    Two or more fields:
        first fields-1 are single words
        last field is remainder.
    """

    replacements = []
    j = start

    for _ in range(fields - 1):

        if j < len(words):
            replacements.append(words[j])
            j += 1
        else:
            replacements.append("")

    k = j

    while k < len(words) and upper[k] != "ARL":
        k += 1

    replacements.append(" ".join(words[j:k]))

    return replacements, k

PARSER_FUNCTIONS = {
    "msg_to_date_time": parser_msg_to_date_time,
}

ARL_PARSERS = {
    0: parser_no_fields,
    1: parser_remainder,
    "default": parser_first_rest,
}

def collect_arl_meanings(text):

    words = text.split()          # preserve original capitalization
    upper = [w.upper() for w in words]

    meanings = []

    i = 0

    while i < len(words):

        if upper[i] == "ARL":

            j = i + 1
            value = 0

            # Decode ARL number
            while j < len(words) and upper[j] in NUMBER_WORDS:
                value += NUMBER_WORDS[upper[j]]
                j += 1

            if value not in ARL_TEXT:
                i = j
                continue
            
            ### replaced from here...
            entry = ARL_TEXT[value]
            fields = entry["fields"]

            # Look for a special parser assigned to this ARL.
            parser = entry.get("parser")

            # Otherwise fall back to the generic parser.
            if parser is None:
                if fields == 0:
                    parser = ARL_PARSERS[0]
                elif fields == 1:
                    parser = ARL_PARSERS[1]
                else:
                    parser = ARL_PARSERS["default"]

            replacements, j = parser(words, upper, j, fields)

            expanded = fill_arl_template(entry["text"], replacements)
            meanings.append(f"ARL {value}: {expanded}")
            ### to here
            
            i = j
            continue

        i += 1

    return meanings


def draw_radiogram_grid(c, text, x, y):

    words = text.split()
    rows = split_into_rows(words,5)

    col_width = 90
    row_height = 15
    
    # draw vertical message boxes (ARRL style)
    c.setLineWidth(0.25)

    max_rows = 5   # number of visible rows on the form

    for r in range(max_rows + 1):
        y_line = y - 10 - r * row_height
        c.line(x, y_line, x + 5 * col_width, y_line)

    for cnum in range(6):
        x_line = x + cnum * col_width
        c.line(x_line, y - 10, x_line, y - 10 - max_rows * row_height)

        c.setFont("Helvetica",9)

        for i in range(5):
            c.drawCentredString(x + i*col_width + col_width/2, y, str(i+1))

    y -= 10
    c.line(x, y, x + 5*col_width, y)

    y -= row_height

    c.setFont("Helvetica",10)
    
    word_number = 1

    for row in rows:

        # draw starting word number at left
        c.setFont("Helvetica",8)
        c.drawRightString(x - 8, y, str(word_number))

        c.setFont("Helvetica",10)

        for i,word in enumerate(row):
            c.drawString(x + i*col_width + 6, y + 2, word)

        word_number += 5
        y -= row_height


# ---------------------------------------------------------

# Draw radiogram front page

# ---------------------------------------------------------

def draw_radiogram(c,data):

    # Title
    c.setFont("Helvetica-Bold",16)
    c.drawCentredString(PAGE_WIDTH/2,750,"AMATEUR (“HAM”) RADIO RADIOGRAM")
    c.setFont("Helvetica-Bold",12)
    c.drawCentredString(PAGE_WIDTH/2,735,"for mail delivery")

    # Header
    c.setFont("Helvetica",10)

    c.drawString(40,710,"Number:")
    c.drawString(100,710,data["number"])

    c.drawString(180,710,"Precedence:")
    c.drawString(260,710,data["prec"])

    c.drawString(380,710,"Station:")
    c.drawString(420,710,data["station"])

    c.drawString(40,680,"Check:")
    c.drawString(100,680,data["check"])

    c.drawString(180,680,"City of Origin:")
    c.drawString(260,680,data["place"])

    c.drawString(380,680,"Date:")
    c.drawString(420,680,data["date"])

    # Address
    c.drawString(40,640,"TO:")

    y = 620

    for line in data["address"]:
        c.drawString(60,y,line)
        y -= 16
        
    # Phone below recipient address
    phone_y = y
    if data["telephone"]:
        c.drawString(60, phone_y,"PHONE:")
        c.drawString(100,phone_y,data["telephone"])



    # Message
    c.drawString(40,540,"MESSAGE:")

    msg = data["message"]

    draw_radiogram_grid(
        c,
        msg,
        60,
        510
    )

    # ---- ARL numbered radiogram meanings ----

    arl_notes = collect_arl_meanings(data["message"])

    if arl_notes:

        y = 410

        c.setFont("Helvetica-Oblique",9)

        for note in arl_notes:
            c.drawString(60,y,note)
            y -= 12

    # Signature
    sig_y = 390

    c.setFont("Helvetica",10)

    c.drawString(40,sig_y,"SIGNATURE:")
    c.drawString(120,sig_y,data["signature"])
    
    # Boilerplate
    boilerplate_text = (
        """This message was handled free of charge by a licensed amateur radio operator. As such messages are
        handled solely for the pleasure of operating, no compensation may be
        accepted by a “ham” operator. A return message may be filed with the radio operator
        delivering this message to you. Further information on amateur radio may be
        obtained from ARRL Headquarters, 225 Main Street, Newington, CT 06111"""
    )

    # Create a style for the boilerplate paragraph
    styles = getSampleStyleSheet()
    style = styles["Normal"]
    style.fontName = "Times-Italic"
    style.fontSize = 11
    style.leading = 18  # line spacing

    # Wrap the paragraph and draw it
    p = Paragraph(boilerplate_text, style)
    p.wrapOn(c, 500, 200)   # width, height
    p.drawOn(c, 45, 250)    # x, y position

#    c.save()

# ---------------------------------------------------------

# Mailing side

# ---------------------------------------------------------

def draw_mailing_side(c,data):
    
    # Check if return address file is present
    return_address = read_return_address() # returns [] if no file found
    
    # Print return address
    if return_address:
        c.setFont("Helvetica", 8)
        y = 500          # top of mailing-address section

        for line in return_address:
            c.drawString(40, y, line)
            y -= 10
    
    # set up mailing address section
    c.setFont("Helvetica-Bold",14)
    
    c.saveState()

    c.translate(PAGE_WIDTH/2, 720)
    c.rotate(180)

    c.drawCentredString(0,0,"AMATEUR RADIO")
    c.drawCentredString(0,-20,"RADIOGRAM")
    c.restoreState()
    
    c.setFont("Helvetica",12)

    y = 410

    for line in data["address"]:
        c.drawString(260,y,line)
        y -= 18


    c.setDash(3,3)

    c.line(0,PAGE_HEIGHT*2/3,PAGE_WIDTH,PAGE_HEIGHT*2/3)
    c.line(0,PAGE_HEIGHT*1/3,PAGE_WIDTH,PAGE_HEIGHT*1/3)

    c.setFont("Helvetica",8)

    c.drawString(10,PAGE_HEIGHT*2/3+4,"FOLD")
    c.drawString(10,PAGE_HEIGHT*1/3+4,"FOLD")

# ---------------------------------------------------------

# Create PDF

# ---------------------------------------------------------

def create_pdf(data,outfile):

    c = canvas.Canvas(outfile,pagesize=letter)

    draw_radiogram(c,data)
    c.showPage()

    draw_mailing_side(c,data)
    c.showPage()

    c.save()

# ---------------------------------------------------------

# Main

# ---------------------------------------------------------
    
def main():

    # hide the Tk window
    root = tk.Tk()
    root.withdraw()

    # choose input file
    infile = filedialog.askopenfilename(
        title="Select FLMSG Radiogram (.m2s)",
        filetypes=[("FLMSG radiogram","*.m2s"),("All files","*.*")]
    )

    if not infile:
        print("No input file selected.")
        return

    # choose output PDF
    outfile = filedialog.asksaveasfilename(
        title="Save Radiogram PDF",
        defaultextension=".pdf",
        filetypes=[("PDF files","*.pdf")]
    )

    if not outfile:
        print("No output file selected.")
        return

    data = parse_flmsg_radiogram(infile)

    create_pdf(data,outfile)

    print("Created:",outfile)


if __name__ == "__main__":
    main()
