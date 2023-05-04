from urllib.parse import urlparse

def qs_parser(url):
    parts = urlparse(url)
    base_url = parts.scheme + "://" + parts.netloc
    directories = parts.path.strip('/').split('/')
    destinations = directories[2:-2]
    return destinations, base_url, directories

# https://www.google.com/maps/dir/Blue+Mountains,+Australia/Uluru,+Petermann+NT+0872,+Australia/Canberra+Australian+Capital+Territory,+Australia/Kakadu,+Northern+Territory+0822,+Australia/@-23.6834376,131.6834616,5z/data=!3m1!4b1!4m28!4m27!1m5!1m1!1s0x6b12750cf28ca111:0x459d55ceda733f5e!2m2!1d150.4865272!2d-33.3856304!1m5!1m1!1s0x2b236c2b6d625223:0x43a8cd4d9bc55f21!2m2!1d131.0368822!2d-25.3444277!1m5!1m1!1s0x6b164ca3b20b34bb:0x400ea6ea7695970!2m2!1d149.1310324!2d-35.2801846!1m5!1m1!1s0x2cb71d596c3de88f:0x40217a82a254820!2m2!1d132.8942719!2d-12.6661075!2m1!2b1!3e0