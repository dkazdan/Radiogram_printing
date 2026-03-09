"""
Python script for creating foldable, mailable radiogram
Uses tkinter pulldown menu to choose the .m2s file from flmsg

Started 8 March 2026

v. 7: 9 March 2026
TODO: Format a little better9 
v. 8: DK March 2026
Put in light boxes for words

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

ARL_TEXT = {
50: "Greetings by Amateur Radio.",
56: "Congratulations on your achievement:",
46: "Greetings on your birthday and best wishes for many more to come.",
47: "Reference your message number _____ to _____ delivered on _____ at _____ UTC.",
67: "Your message number _______ undeliverable because of _______. Please advise."
}

# ---------------------------------------------------------

# Decode FLMSG length/value format

# Example: "2 85" → "85"

# ---------------------------------------------------------

def decode_flmsg_value(text):

    text = text.strip()
    parts = text.split(" ",1)

    if len(parts) == 2 and parts[0].isdigit():
        return parts[1].strip()

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

    if "to" in raw:
        data["address"] = [decode_flmsg_value(x) for x in raw["to"]]

    if "msg" in raw:
        msg = [decode_flmsg_value(x) for x in raw["msg"]]
        data["message"] = " ".join(msg)
        
    return data

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
                result.append(f"ARL {value} ({ARL_TEXT[value]})")
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

def collect_arl_meanings(text):

    words = text.upper().split()
    meanings = []

    i = 0

    while i < len(words):

        if words[i] == "ARL":

            j = i + 1
            value = 0

            while j < len(words) and words[j] in NUMBER_WORDS:
                value += NUMBER_WORDS[words[j]]
                j += 1

            if value in ARL_TEXT:
                meanings.append(f"ARL {value}: {ARL_TEXT[value]}")

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

    c.setFont("Helvetica-Bold",14)

    c.drawString(60,700,"AMATEUR RADIO")
    c.drawString(60,680,"RADIOGRAM")

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
