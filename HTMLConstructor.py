import os

def get_header(title: str) -> str:
    header_path = os.path.join(os.path.dirname(__file__), "templates/header.html")
    css_path = os.path.join(os.path.dirname(__file__), "templates/min.css")
    header = ""
    with open(header_path,"r",encoding="utf-8") as file:
        for line in file:
            header = header + line
    css = ""
    with open(css_path,"r",encoding="utf-8") as file:
        for line in file:
            css = css + line
    header = header.replace("$TITLE",title).replace("$CSS",css)
    return header

def get_footer() -> str:
    footer_path = os.path.join(os.path.dirname(__file__), "templates/footer.html")
    footer = ""
    with open(footer_path, "r", encoding="utf-8") as file:
        for line in file:
            footer = footer + line
    return footer

# position = "left"/"right"
def construct_body(position: str, name: str, pic_url: str, profile_url: str, message: str, date: str) -> str:
    body_path = os.path.join(os.path.dirname(__file__), "templates/body.html")
    body = ""
    with open(body_path, "r", encoding="utf-8") as file:
        for line in file:
            body = body + line
    body = body.replace("$POSITION", position)
    if position == "right":
        body = body.replace("media-body pad-hor","media-body pad-hor speech-right")
    body = body.replace("$NAME", name)\
        .replace("$PIC_URL", pic_url)\
        .replace("$PROFILE_LINK", profile_url)\
        .replace("$MESSAGE", message)\
        .replace("$DATE", date)
    return body

# test
if __name__ == "__main__":
    print(get_header("mother fkr"))
    print(construct_body("right","Mahmoud","#","#","whats up?", "2019.10.9 05:03"))
    print(get_footer())
